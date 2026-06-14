#!/usr/bin/env python3
"""Etapa 1 do pipeline V11 — Análise estruturada do questionário.

Lê o questionário pré-consulta (e hormonal, se mulher) e usa Claude Sonnet 4.5
via OpenRouter com structured outputs para gerar um JSON canônico com:

- queixas principais (intensidade, contexto)
- histórico clínico (doenças, cirurgias, medicações, alergias, família)
- estilo de vida (atividade, alimentação, sono, hidratação, trabalho)
- saúde hormonal (se F)
- perfil psicossocial
- metas
- SPIN
- sinais de alerta (red flags clínicos)
- perfil DISC
- interpretação inicial do questionário (1-2 parágrafos, SEM olhar exames ainda)

NÃO conclui diagnóstico. Apenas estrutura e identifica padrões pré-clínicos.

Uso:
    python3 analisar_questionario_llm.py <paciente_dir>/dados-questionario.json [--output OUT]

Output: JSON validado contra V11_QUESTIONARIO_SCHEMA, salvo em
        state/auditoria_v11/<paciente>_<ts>/etapa_1_questionario.json
"""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

OPENROUTER_BASE = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "anthropic/claude-fable-5"  # via OpenRouter; primario Ana/apresentacoes
FALLBACK_MODELS = ["anthropic/claude-sonnet-4.6", "anthropic/claude-sonnet-4", "google/gemini-2.5-pro"]
SCHEMA_VERSION = "v11.1"


def _load_api_key():
    for p in [
        "/root/.openclaw/.env.runtime",
        "/root/.openclaw/.env",
        os.path.expanduser("~/.openrouter.env"),
    ]:
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


V11_QUESTIONARIO_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "schema_version": {"type": "string"},
        "paciente": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "nome": {"type": "string"},
                "sexo": {"type": "string", "enum": ["F", "M"]},
                "idade": {"type": ["integer", "null"]},
                "imc_atual": {"type": ["number", "null"]},
                "imc_objetivo": {"type": ["number", "null"]},
                "profissao": {"type": ["string", "null"]},
                "como_conheceu": {"type": ["string", "null"]},
            },
            "required": ["nome", "sexo", "idade", "imc_atual", "imc_objetivo", "profissao", "como_conheceu"],
        },
        "queixas_principais": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "queixa": {"type": "string"},
                    "intensidade": {"type": "integer", "enum": [1, 2, 3, 4, 5]},
                    "contexto": {"type": "string"},
                    "categoria": {
                        "type": "string",
                        "enum": ["metabolico", "hormonal", "gastrointestinal", "musculo_esqueletico",
                                "psicossocial", "energia_sono", "estetico_funcional", "outro"],
                    },
                },
                "required": ["queixa", "intensidade", "contexto", "categoria"],
            },
        },
        "historico_clinico": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "doencas_cronicas": {"type": "array", "items": {"type": "string"}},
                "cirurgias": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "procedimento": {"type": "string"},
                            "ano": {"type": ["integer", "null"]},
                        },
                        "required": ["procedimento", "ano"],
                    },
                },
                "medicacoes_atuais": {"type": "array", "items": {"type": "string"}},
                "alergias_intolerancias": {"type": "array", "items": {"type": "string"}},
                "historico_familiar": {"type": "string"},
                "reposicao_hormonal": {"type": "string"},
            },
            "required": ["doencas_cronicas", "cirurgias", "medicacoes_atuais",
                         "alergias_intolerancias", "historico_familiar", "reposicao_hormonal"],
        },
        "estilo_de_vida": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "atividade_fisica": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "frequencia": {"type": "string"},
                        "tipo": {"type": "string"},
                    },
                    "required": ["frequencia", "tipo"],
                },
                "alimentacao": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "refeicoes_por_dia": {"type": ["integer", "null"]},
                        "doces": {"type": "string"},
                        "alcool": {"type": "string"},
                        "tabaco": {"type": "string"},
                        "hidratacao_litros": {"type": ["number", "null"]},
                        "padrao_geral": {"type": "string"},
                    },
                    "required": ["refeicoes_por_dia", "doces", "alcool", "tabaco",
                                 "hidratacao_litros", "padrao_geral"],
                },
                "sono": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "horas": {"type": ["number", "null"]},
                        "qualidade_1_10": {"type": ["integer", "null"], "description": "Inteiro 1-10 ou null se não informado"},
                        "energia_ao_acordar_1_5": {"type": ["integer", "null"], "description": "Inteiro 1-5 ou null se não informado"},
                        "cansaco_durante_dia": {"type": "string"},
                    },
                    "required": ["horas", "qualidade_1_10", "energia_ao_acordar_1_5", "cansaco_durante_dia"],
                },
                "trabalho": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "tipo": {"type": "string"},
                        "horarios": {"type": "string"},
                    },
                    "required": ["tipo", "horarios"],
                },
                "frequencia_intestinal": {"type": "string"},
            },
            "required": ["atividade_fisica", "alimentacao", "sono", "trabalho", "frequencia_intestinal"],
        },
        "saude_hormonal": {
            "type": ["object", "null"],
            "additionalProperties": False,
            "properties": {
                "ciclo_menstrual": {"type": "string"},
                "menopausa": {"type": "string"},
                "metodo_contraceptivo": {"type": "string"},
                "libido": {"type": "string"},
                "ressecamento_vaginal": {"type": "string"},
                "dispareunia": {"type": "string"},
                "queda_cabelo": {"type": "string"},
                "pele": {"type": "string"},
                "unhas": {"type": "string"},
                "sintomas_ciclo": {"type": "string"},
            },
            "required": ["ciclo_menstrual", "menopausa", "metodo_contraceptivo", "libido",
                         "ressecamento_vaginal", "dispareunia", "queda_cabelo", "pele", "unhas",
                         "sintomas_ciclo"],
        },
        "perfil_psicossocial": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "barreira_principal": {"type": "string"},
                "investe_em_saude": {"type": "string"},
                "nivel_energia_1_10": {"type": ["integer", "null"], "description": "Inteiro 1-10 ou null se não informado"},
                "ansiedade_estresse": {"type": "string"},
            },
            "required": ["barreira_principal", "investe_em_saude", "nivel_energia_1_10", "ansiedade_estresse"],
        },
        "metas": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "peso_atual_kg": {"type": ["number", "null"]},
                "peso_objetivo_kg": {"type": ["number", "null"]},
                "peso_maximo_anterior_kg": {"type": ["number", "null"]},
                "diferenca_para_objetivo_kg": {"type": ["number", "null"]},
            },
            "required": ["peso_atual_kg", "peso_objetivo_kg", "peso_maximo_anterior_kg",
                         "diferenca_para_objetivo_kg"],
        },
        "spin": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "tempo_luta": {"type": "string"},
                "incomodo_principal": {"type": "string"},
                "desafios": {"type": "string"},
                "cenario_sem_tratamento": {"type": "string"},
                "investimento_perdido": {"type": "string"},
                "vida_resolvida_significaria": {"type": "string"},
                "interesse_programa": {"type": "string"},
            },
            "required": ["tempo_luta", "incomodo_principal", "desafios", "cenario_sem_tratamento",
                         "investimento_perdido", "vida_resolvida_significaria", "interesse_programa"],
        },
        "sinais_alerta": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "sinal": {"type": "string"},
                    "categoria": {
                        "type": "string",
                        "enum": ["metabolico", "hormonal", "gastrointestinal", "cardiovascular",
                                "psicossocial", "energia_sono", "outro"],
                    },
                    "prioridade": {"type": "integer", "enum": [1, 2, 3],
                                   "description": "1=baixa, 2=moderada, 3=alta urgência clínica"},
                    "justificativa": {"type": "string"},
                },
                "required": ["sinal", "categoria", "prioridade", "justificativa"],
            },
        },
        "perfil_disc": {
            "type": "string",
            "enum": ["D", "I", "S", "C", "default"],
        },
        "interpretacao_inicial": {
            "type": "string",
            "description": "Síntese clínica do questionário em 1-2 parágrafos. NÃO conclui diagnóstico. Identifica padrões e hipóteses que serão cruzadas com exames depois.",
        },
        "completude": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "campos_preenchidos": {"type": "integer"},
                "campos_totais": {"type": "integer"},
                "percentual": {"type": "number"},
                "campos_criticos_faltantes": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["campos_preenchidos", "campos_totais", "percentual", "campos_criticos_faltantes"],
        },
    },
    "required": ["schema_version", "paciente", "queixas_principais", "historico_clinico",
                 "estilo_de_vida", "saude_hormonal", "perfil_psicossocial", "metas", "spin",
                 "sinais_alerta", "perfil_disc", "interpretacao_inicial", "completude"],
}


SYSTEM_PROMPT = """Você é uma médica clínica integrativa sênior do Instituto Vital Slim, especializada em metabolismo, hormônios e composição corporal.

Sua tarefa: analisar o questionário de pré-consulta de uma paciente e estruturar TODAS as informações em um JSON canônico que será cruzado com exames laboratoriais posteriormente.

REGRAS ABSOLUTAS:
1. NÃO conclua diagnóstico definitivo (você ainda não viu os exames).
2. NÃO prometa resultados clínicos.
3. NÃO use linguagem mercadológica ("emagrecimento garantido", "cura").
4. Use linguagem técnica e neutra (compliance CFM).
5. Identifique HIPÓTESES e PADRÕES, não conclusões.
6. Cada queixa principal deve ter intensidade 1-5 baseada no que o questionário descreve.
7. Sinais de alerta = red flags clínicos que MERECEM atenção mas não são emergência (ex: cansaço persistente, libido reduzida + perimenopausa, ciclo irregular).
8. A interpretação inicial deve ser sóbria, técnica, 1-2 parágrafos no máximo.
9. Se um campo do questionário estiver vazio ou ambíguo, registre em completude.campos_criticos_faltantes.
10. Categorias e enums DEVEM bater exatamente com o schema (case-sensitive).
11. **NUNCA mencione "perfil DISC", "tipo D/I/S/C", ou caracterizações DISC no texto livre** (interpretacao_inicial). O DISC é usado internamente para adaptar tom da apresentação, mas o paciente NÃO deve ver essa terminologia. O campo `perfil_disc` JSON registra o tipo, sem aparecer em prosa.

CONTEXTO IVS:
- Instituto Vital Slim trabalha com mulheres em perimenopausa/menopausa, hipotireoidismo, resistência à insulina e síndrome metabólica.
- Linha de cuidado: reposição hormonal bioidêntica + tratamento metabólico + acompanhamento nutricional/exercício.
- Toda paciente é VIP, atendimento particular, sem convênio.

Responda APENAS com o JSON conforme schema. Nenhum texto adicional."""


def _validar_schema_manual(data, schema):
    """Validação básica do schema. Não é tão rigorosa quanto jsonschema lib, mas pega buracos críticos."""
    if not isinstance(data, dict):
        raise ValueError("response não é dict")
    required = schema.get("required", [])
    missing = [k for k in required if k not in data]
    if missing:
        raise ValueError(f"campos obrigatórios faltando: {missing}")
    return True


def chamar_openrouter(messages, schema, model=MODEL, max_retries=3):
    """Chama OpenRouter em modo json_object (sem strict, mais compatível) e valida manualmente."""
    api_key = _load_api_key()
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY não configurada")

    # injeta o schema no system prompt para o modelo seguir
    schema_str = json.dumps(schema, ensure_ascii=False, indent=2)
    schema_instruction = f"\n\nSCHEMA OBRIGATÓRIO DO JSON DE RESPOSTA (siga exatamente, todos os campos required):\n```json\n{schema_str}\n```"
    messages_with_schema = messages.copy()
    if messages_with_schema and messages_with_schema[0]["role"] == "system":
        messages_with_schema[0] = {
            "role": "system",
            "content": messages_with_schema[0]["content"] + schema_instruction,
        }
    else:
        messages_with_schema.insert(0, {"role": "system", "content": schema_instruction})

    body = {
        "model": model,
        "messages": messages_with_schema,
        "response_format": {"type": "json_object"},
        "temperature": 0.1,
        "max_tokens": 4096,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://institutovitalslim.com.br",
        "X-Title": "IVS V11 Analise Questionario",
    }

    models_to_try = [model] + [m for m in FALLBACK_MODELS if m != model]
    last_err = None

    for try_model in models_to_try:
        body["model"] = try_model
        for attempt in range(1, max_retries + 1):
            try:
                req = urllib.request.Request(
                    OPENROUTER_BASE,
                    data=json.dumps(body).encode("utf-8"),
                    headers=headers,
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=180) as r:
                    resp = json.loads(r.read().decode("utf-8"))
                    content = resp["choices"][0]["message"]["content"]
                    # alguns modelos colocam markdown wrappers
                    content = content.strip()
                    if content.startswith("```"):
                        content = re.sub(r"^```(?:json)?\s*", "", content)
                        content = re.sub(r"\s*```$", "", content)
                    parsed = json.loads(content)
                    _validar_schema_manual(parsed, schema)
                    usage = resp.get("usage", {})
                    usage["model_used"] = try_model
                    return parsed, usage
            except urllib.error.HTTPError as e:
                err_body = e.read().decode() if e.fp else ""
                last_err = f"HTTP {e.code} ({try_model}): {err_body[:200]}"
                print(f"[WARN] {try_model} tentativa {attempt}/{max_retries}: {last_err}", file=sys.stderr)
                if e.code in (429, 502, 503, 504) and attempt < max_retries:
                    time.sleep(2 ** attempt)
                    continue
                break  # erro permanente — pula pro próximo modelo
            except (json.JSONDecodeError, ValueError) as e:
                last_err = f"{type(e).__name__} ({try_model}): {e}"
                print(f"[WARN] {try_model} tentativa {attempt}/{max_retries}: {last_err}", file=sys.stderr)
                if attempt < max_retries:
                    time.sleep(1)
                    continue
                break
            except Exception as e:
                last_err = f"{type(e).__name__} ({try_model}): {e}"
                print(f"[WARN] {try_model} tentativa {attempt}/{max_retries}: {last_err}", file=sys.stderr)
                if attempt < max_retries:
                    time.sleep(2 ** attempt)
                    continue
                break
        print(f"[INFO] {try_model} falhou. Tentando próximo modelo...", file=sys.stderr)

    raise RuntimeError(f"Todos os modelos falharam. Último erro: {last_err}")


def analisar_questionario(questionario_json: dict, paciente_meta: dict | None = None) -> tuple[dict, dict]:
    """
    Analisa o questionário e retorna (analise_estruturada, usage_info).
    """
    sexo = (paciente_meta or {}).get("sexo", "")
    if not sexo:
        # tentar inferir do questionário
        resp = questionario_json.get("portal-ivs", {}).get("respostas", {})
        s = str(resp.get("Sexo", "")).lower()
        if "fem" in s:
            sexo = "F"
        elif "masc" in s:
            sexo = "M"

    contexto_paciente = ""
    if paciente_meta:
        nome = paciente_meta.get("nome", "")
        idade = paciente_meta.get("idade", "")
        contexto_paciente = f"\n\nMETA do paciente (vindo do orchestrator):\n- nome: {nome}\n- sexo: {sexo}\n- idade: {idade}\n"

    user_msg = f"""Analise este questionário e estruture conforme schema V11.

{contexto_paciente}

QUESTIONÁRIO COMPLETO (JSON):
{json.dumps(questionario_json, ensure_ascii=False, indent=2)}

IMPORTANTE:
- Se a paciente for mulher (sexo F), `saude_hormonal` é OBRIGATÓRIO (use null em campos não preenchidos com string "não informado").
- Se for homem (sexo M), `saude_hormonal` pode ser null (o object inteiro).
- O `perfil_disc` deve ser inferido do campo "Perfil DISC (detalhado)" — pegue o item mais frequente nas 20 respostas.
- `interpretacao_inicial`: 1-2 parágrafos técnicos, foco em padrões que merecerão investigação nos exames.
- `sinais_alerta`: identifique 3-7 red flags clínicos (não emergências, mas pontos de atenção).
- `completude.campos_criticos_faltantes`: liste campos como peso, altura, idade, sexo, sintomas principais que estiverem vazios.
"""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_msg},
    ]

    return chamar_openrouter(messages, V11_QUESTIONARIO_SCHEMA)


def _slug(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[-\s]+", "-", s)
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("questionario", help="Caminho JSON do questionário (paola_q.json formato)")
    ap.add_argument("--paciente-nome", default="")
    ap.add_argument("--paciente-sexo", default="", help="F ou M")
    ap.add_argument("--paciente-idade", type=int, default=0)
    ap.add_argument("--output", default="", help="Output path. Default: state/auditoria_v11/<slug>_<ts>/etapa_1_questionario.json")
    args = ap.parse_args()

    with open(args.questionario) as f:
        q = json.load(f)

    meta = {}
    if args.paciente_nome:
        meta["nome"] = args.paciente_nome
    if args.paciente_sexo:
        meta["sexo"] = args.paciente_sexo
    if args.paciente_idade:
        meta["idade"] = args.paciente_idade

    print(f"[V11/etapa 1] Analisando questionário com {MODEL}...", file=sys.stderr)
    t0 = time.time()
    analise, usage = analisar_questionario(q, meta)
    dt = time.time() - t0

    # Determinar path de saída
    if args.output:
        out_path = Path(args.output)
    else:
        nome = meta.get("nome") or analise.get("paciente", {}).get("nome", "paciente")
        slug = _slug(nome)
        ts = time.strftime("%Y%m%d_%H%M%S")
        base = Path("/root/cerebro-vital-slim/skills/geracao-apresentacao-paciente/state/auditoria_v11")
        out_path = base / f"{slug}_{ts}" / "etapa_1_questionario.json"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(analise, f, ensure_ascii=False, indent=2)

    # Gate da Etapa 1: queixas_principais não vazio
    queixas = analise.get("queixas_principais", [])
    completude = analise.get("completude", {})
    gate_ok = len(queixas) >= 1 and completude.get("percentual", 0) >= 50

    print(json.dumps({
        "etapa": 1,
        "output_path": str(out_path),
        "modelo": MODEL,
        "duracao_s": round(dt, 1),
        "usage": usage,
        "queixas_extraidas": len(queixas),
        "sinais_alerta": len(analise.get("sinais_alerta", [])),
        "completude_pct": completude.get("percentual", 0),
        "campos_criticos_faltantes": completude.get("campos_criticos_faltantes", []),
        "perfil_disc": analise.get("perfil_disc", "default"),
        "gate_ok": gate_ok,
    }, ensure_ascii=False, indent=2))

    sys.exit(0 if gate_ok else 1)


if __name__ == "__main__":
    main()
