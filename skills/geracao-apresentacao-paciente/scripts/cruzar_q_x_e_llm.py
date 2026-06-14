#!/usr/bin/env python3
"""Etapa 4 do pipeline V11 — Cruzamento Questionário × Exames.

Recebe:
- analise_questionario.json (output Etapa 1)
- interpretacao_exames.json (output Etapa 3)

Usa Claude Fable 5 para gerar hipóteses clínicas integradas do tipo:
- "Queixa X + achado laboratorial Y = padrão Z" (com prioridade)
- "Sintoma sem suporte laboratorial = revisão clínica"
- "Achado laboratorial sem queixa = atenção subclínica"

Output: cruzamento_clinico.json com hipóteses priorizadas + plano clínico
        integrado + texto narrativo pra entrar na apresentação V11.

Uso:
    python3 cruzar_q_x_e_llm.py <questionario.json> <interpretacao.json> [--output OUT]
"""
from __future__ import annotations
import argparse, json, os, re, sys, time, urllib.request, urllib.error
from pathlib import Path

OPENROUTER_BASE = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "anthropic/claude-fable-5"
FALLBACK_MODELS = ["anthropic/claude-opus-4.8", "anthropic/claude-sonnet-4.6", "anthropic/claude-sonnet-4", "google/gemini-2.5-pro", "openai/gpt-5.5"]
SCHEMA_VERSION = "V11"


def _load_api_key():
    for p in ["/root/.openclaw/.env.runtime", "/root/.openclaw/.env"]:
        if not os.path.exists(p):
            continue
        with open(p) as f:
            for line in f:
                line = line.strip()
                if line.startswith("OPENROUTER_API_KEY="):
                    v = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if v and not v.startswith("op://"):
                        return v
    return os.environ.get("OPENROUTER_API_KEY", "")


CRUZAMENTO_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "schema_version": {"type": "string"},
        "hipoteses_integradas": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "titulo": {"type": "string", "description": "Frase curta resumindo o padrão"},
                    "queixas_relacionadas": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Queixas do questionário que apoiam essa hipótese"
                    },
                    "exames_relacionados": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Nomes dos exames laboratoriais que apoiam essa hipótese"
                    },
                    "descricao_clinica": {
                        "type": "string",
                        "description": "Parágrafo técnico explicando a conexão queixa-exame. NÃO conclui diagnóstico definitivo."
                    },
                    "prioridade": {"type": "integer", "enum": [1, 2, 3], "description": "1=baixa; 2=média; 3=alta — definir abordagem clínica"},
                    "tipo": {
                        "type": "string",
                        "enum": ["queixa_com_suporte_laboratorial", "queixa_sem_suporte_laboratorial",
                                 "achado_laboratorial_sem_queixa", "padrao_metabolico", "padrao_hormonal",
                                 "padrao_nutricional", "padrao_inflamatorio"]
                    },
                    "acao_proposta": {
                        "type": "string",
                        "description": "Próximo passo clínico sugerido. Linguagem CFM: 'considerar avaliar X', 'investigar Y', NUNCA prescrição direta."
                    }
                },
                "required": ["titulo", "queixas_relacionadas", "exames_relacionados",
                             "descricao_clinica", "prioridade", "tipo", "acao_proposta"]
            }
        },
        "queixas_sem_correlato_laboratorial": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "queixa": {"type": "string"},
                    "interpretacao": {"type": "string", "description": "Hipóteses não laboratoriais (ex: estilo de vida, psicossocial)"},
                    "proxima_acao": {"type": "string"}
                },
                "required": ["queixa", "interpretacao", "proxima_acao"]
            }
        },
        "achados_sem_queixa_correspondente": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "achado": {"type": "string"},
                    "relevancia_clinica": {"type": "string"},
                    "monitoramento": {"type": "string"}
                },
                "required": ["achado", "relevancia_clinica", "monitoramento"]
            }
        },
        "plano_clinico_integrado": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "alvos_prioritarios": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "3-6 frentes prioritárias para abordar no programa"
                },
                "monitoramento_sugerido": {"type": "string", "description": "Quais marcadores reavaliar e em quanto tempo"},
                "investigacoes_adicionais": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Exames complementares sugeridos"
                }
            },
            "required": ["alvos_prioritarios", "monitoramento_sugerido", "investigacoes_adicionais"]
        },
        "narrativa_executiva": {
            "type": "string",
            "description": "MÁXIMO 2 frases curtas (até 360 caracteres total). É APRESENTAÇÃO pro paciente, não relatório técnico — a Dra. explica os detalhes na consulta. Foco: o que está acontecendo (1 frase) + por que importa agora (1 frase). Sem listar exames, sem jargão pesado, sem promessa de cura."
        },
        "alinhamento_disc": {
            "type": "string",
            "description": "Como apresentar essas hipóteses ao paciente respeitando o perfil DISC dele (D/I/S/C). Frase curta."
        }
    },
    "required": ["schema_version", "hipoteses_integradas", "queixas_sem_correlato_laboratorial",
                 "achados_sem_queixa_correspondente", "plano_clinico_integrado", "narrativa_executiva",
                 "alinhamento_disc"]
}


SYSTEM_PROMPT = """Você é uma médica clínica integrativa sênior do Instituto Vital Slim, especializada em integrar contexto clínico (queixas, sintomas, estilo de vida) com achados laboratoriais para gerar hipóteses diagnósticas e plano de cuidado.

Sua tarefa: receber o JSON da análise do questionário (Etapa 1) e o JSON da interpretação clínica dos exames (Etapa 3) de uma paciente, e gerar hipóteses INTEGRADAS no formato:

- "Queixa X + achado laboratorial Y = padrão Z" (com prioridade clínica)
- "Sintoma sem suporte laboratorial = considerar outras causas"
- "Achado laboratorial sem queixa = atenção subclínica + monitoramento"

REGRAS ABSOLUTAS (compliance CFM):
1. NUNCA escreva diagnóstico definitivo. Use "sugere", "compatível com", "padrão de", "hipótese de".
2. NÃO prescreva. Sugira "avaliação clínica para considerar X" no máximo.
3. NÃO prometa resultado.
4. Tom técnico, integrado, humano. Como uma médica explicando o caso pra equipe multidisciplinar.
5. Foque em CORRELAÇÕES REAIS. Não force hipóteses sem suporte.
6. Priorize hipóteses por urgência clínica (3=alta) e impacto (peso na vida da paciente).
7. Para padrões metabólicos/hormonais, integre estilo de vida e idade fisiológica.
8. A narrativa executiva deve ser pronto-pra-uso na apresentação V11. Linguagem que a paciente (leiga) entende, mas técnica suficiente para o médico.
9. O alinhamento DISC deve sugerir HOW (não WHAT) — como entregar as hipóteses respeitando perfil.
10. **NUNCA mencione "perfil DISC", "tipo D/I/S/C", ou caracterizações DISC nos textos visíveis ao paciente** (narrativa_executiva, descricao_clinica, acao_proposta, interpretacao). O DISC vive apenas no campo `alinhamento_disc` (orientação interna pro time clínico). O paciente NÃO deve ver essa terminologia em prosa.

PADRÕES CLÁSSICOS A CONSIDERAR (lista não exaustiva):
- Síndrome metabólica: HOMA-IR alto + TG alto + HDL baixo + circunferência abdominal + cansaço/desânimo
- Hipotireoidismo subclínico: TSH alto + queixas de cansaço, ganho de peso, frio, queda cabelo
- Perimenopausa: FSH alto + estradiol oscilante + queixas de calorão, libido, sono, irregularidade menstrual
- Anemia ferropriva: Hb baixa + ferritina <30 + queixas de cansaço, falta de ar, palidez
- Dislipidemia aterogênica: LDL alto + HDL baixo + TG alto + sedentarismo + alimentação inadequada
- Deficiência Vit D: <30 + queixas musculares, fadiga, queda de cabelo, baixa imunidade
- Deficiência B12: <500 + queixas neurológicas, fadiga, formigamento
- Inflamação crônica subclínica: PCR>3 + cansaço + dor articular + alimentação inflamatória

Responda APENAS com o JSON conforme schema."""


def _validar_schema_manual(data, schema):
    if not isinstance(data, dict):
        raise ValueError("response não é dict")
    missing = [k for k in schema.get("required", []) if k not in data]
    if missing:
        raise ValueError(f"campos obrigatórios faltando: {missing}")
    return True


def chamar_openrouter(messages, schema, max_retries=2):
    api_key = _load_api_key()
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY não configurada")

    schema_str = json.dumps(schema, ensure_ascii=False, indent=2)
    schema_instruction = f"\n\nSCHEMA OBRIGATÓRIO DO JSON DE RESPOSTA:\n```json\n{schema_str}\n```"
    msgs = messages.copy()
    if msgs and msgs[0]["role"] == "system":
        msgs[0] = {"role": "system", "content": msgs[0]["content"] + schema_instruction}

    body = {
        "messages": msgs,
        "response_format": {"type": "json_object"},
        "temperature": 0.2,
        "max_tokens": 8000,
    }
    headers = {
        "Authorization": f"Bearer {api_key}", "Content-Type": "application/json",
        "HTTP-Referer": "https://institutovitalslim.com.br",
        "X-Title": "IVS V11 Cruzamento Q x E",
    }

    last_err = None
    for try_model in [MODEL] + FALLBACK_MODELS:
        body["model"] = try_model
        for attempt in range(1, max_retries + 1):
            try:
                req = urllib.request.Request(OPENROUTER_BASE, data=json.dumps(body).encode("utf-8"),
                                              headers=headers, method="POST")
                with urllib.request.urlopen(req, timeout=240) as r:
                    resp = json.loads(r.read().decode("utf-8"))
                    content = resp["choices"][0]["message"]["content"].strip()
                    if content.startswith("```"):
                        content = re.sub(r"^```(?:json)?\s*", "", content)
                        content = re.sub(r"\s*```$", "", content)
                    parsed = json.loads(content)
                    _validar_schema_manual(parsed, schema)
                    usage = resp.get("usage", {})
                    usage["model_used"] = try_model
                    return parsed, usage
            except Exception as e:
                err_str = str(e)
                if isinstance(e, urllib.error.HTTPError) and e.fp:
                    err_str = f"HTTP {e.code}: {e.read().decode()[:300]}"
                last_err = f"{try_model} attempt {attempt}: {err_str[:300]}"
                print(f"[WARN] {last_err}", file=sys.stderr)
                if attempt < max_retries:
                    time.sleep(2 ** attempt)
                    continue
                break

    raise RuntimeError(f"Todos os modelos falharam: {last_err}")


def cruzar(questionario, interpretacao):
    """Roda o cruzamento usando o LLM."""
    # Resumir interpretação pra reduzir tokens
    interp_resumo = {
        "alertas_criticos_globais": interpretacao.get("alertas_criticos_globais", []),
        "sistemas": {}
    }
    for sis, sis_data in interpretacao.get("sistemas", {}).items():
        if isinstance(sis_data, dict) and "exames_interpretados" in sis_data:
            interp_resumo["sistemas"][sis] = {
                "sintese": sis_data.get("sintese_do_sistema", ""),
                "alterados": [
                    {
                        "nome": ex.get("nome"),
                        "valor": ex.get("valor"),
                        "ref": ex.get("referencia"),
                        "tendencia": ex.get("diagnostico_tendencia"),
                        "risco_curto": ex.get("risco_curto_prazo"),
                        "etiologia": ex.get("fator_etiologico_provavel"),
                        "severidade": ex.get("severidade"),
                    }
                    for ex in sis_data.get("exames_interpretados", [])
                    if ex.get("severidade", 1) >= 3
                ]
            }

    questionario_resumo = {
        "paciente": questionario.get("paciente"),
        "queixas_principais": questionario.get("queixas_principais", []),
        "historico_clinico": questionario.get("historico_clinico", {}),
        "estilo_de_vida": questionario.get("estilo_de_vida", {}),
        "saude_hormonal": questionario.get("saude_hormonal"),
        "perfil_psicossocial": questionario.get("perfil_psicossocial", {}),
        "sinais_alerta": questionario.get("sinais_alerta", []),
        "perfil_disc": questionario.get("perfil_disc", "default"),
        "interpretacao_inicial": questionario.get("interpretacao_inicial", ""),
    }

    user_msg = f"""CRUZE o questionário com a interpretação dos exames e gere hipóteses integradas.

QUESTIONÁRIO (Etapa 1):
{json.dumps(questionario_resumo, ensure_ascii=False, indent=2)}

INTERPRETAÇÃO DOS EXAMES (Etapa 3 — só os relevantes severidade >=3):
{json.dumps(interp_resumo, ensure_ascii=False, indent=2)}

GERE:
- 4-8 hipóteses integradas priorizadas (foque em queixas que TÊM correlato laboratorial primeiro)
- Queixas sem correlato laboratorial (revisar causas não-lab)
- Achados sem queixa (atenção subclínica)
- Plano clínico integrado (3-6 alvos prioritários)
- Narrativa executiva 2-3 parágrafos pronto pra apresentação
- Alinhamento DISC: como apresentar pra este perfil específico ({questionario_resumo['perfil_disc']})"""

    return chamar_openrouter([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_msg}
    ], CRUZAMENTO_SCHEMA)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("questionario", help="JSON da Etapa 1")
    ap.add_argument("interpretacao", help="JSON da Etapa 3")
    ap.add_argument("--output", default="")
    args = ap.parse_args()

    questionario = json.load(open(args.questionario))
    interpretacao = json.load(open(args.interpretacao))

    print(f"[V11/etapa 4] Cruzando questionário x exames com {MODEL}...", file=sys.stderr)
    t0 = time.time()
    cruzamento, usage = cruzar(questionario, interpretacao)
    dt = time.time() - t0

    if args.output:
        out_path = Path(args.output)
    else:
        nome = questionario.get("paciente", {}).get("nome", "paciente")
        slug = re.sub(r"[^\w\-]", "-", nome.lower())
        slug = re.sub(r"-+", "-", slug).strip("-")
        ts = time.strftime("%Y%m%d_%H%M%S")
        base = Path("/root/cerebro-vital-slim/skills/geracao-apresentacao-paciente/state/auditoria_v11")
        out_path = base / f"{slug}_{ts}" / "etapa_4_cruzamento.json"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(cruzamento, f, ensure_ascii=False, indent=2)

    hipoteses = cruzamento.get("hipoteses_integradas", [])
    gate_ok = len(hipoteses) >= 3

    print(json.dumps({
        "etapa": 4,
        "output_path": str(out_path),
        "modelo_usado": usage.get("model_used"),
        "duracao_s": round(dt, 1),
        "hipoteses_integradas": len(hipoteses),
        "queixas_sem_correlato": len(cruzamento.get("queixas_sem_correlato_laboratorial", [])),
        "achados_sem_queixa": len(cruzamento.get("achados_sem_queixa_correspondente", [])),
        "alvos_prioritarios": len(cruzamento.get("plano_clinico_integrado", {}).get("alvos_prioritarios", [])),
        "usage": usage,
        "gate_ok": gate_ok,
    }, ensure_ascii=False, indent=2))

    sys.exit(0 if gate_ok else 1)


if __name__ == "__main__":
    main()
