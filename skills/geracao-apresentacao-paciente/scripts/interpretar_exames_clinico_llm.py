#!/usr/bin/env python3
"""Etapa 3 do pipeline V11 — Interpretação clínica por exame.

Lê o JSON de exames extraídos (output do extrator V10 + validador 11 layers)
e usa Claude Fable 5 via OpenRouter para gerar, POR EXAME:

- diagnóstico de tendência (normal / pré-X / X estabelecido / risco de X)
- risco associado curto e médio prazo
- fator etiológico mais provável
- severidade clínica 1-5
- recomendação de investigação adicional (se aplicável)

Agrupa por sistema fisiológico para reduzir chamadas LLM:
- tireoide (TSH, T4L, T3L, anti-TPO, anti-Tg)
- metabolico (glicemia, HbA1c, insulina, HOMA, lipidograma)
- hormonal_feminino (estradiol, progesterona, FSH, LH, DHEA, SHBG, etc.)
- hormonal_masculino (testo total/livre, SHBG, estradiol, PSA)
- hematologico (hemograma, plaquetas)
- hepatico (TGO, TGP, GGT, FA, bilirrubinas)
- renal (creatinina, ureia, ácido úrico, clearance)
- inflamatorio (PCR, VHS, ferritina)
- nutricional (vit D, B12, folato, ferro, zinco, magnesio)
- cardiovascular (homocisteína, ApoB, Lp(a))

NÃO conclui diagnóstico definitivo. Identifica tendências e riscos com base
em refs canônicas IVS + literatura médica. Linguagem compliance CFM.

Uso:
    python3 interpretar_exames_clinico_llm.py <exames.json> --paciente-sexo F --paciente-idade 49 [--output OUT]

Input esperado: JSON com chave "grupos" (formato do orchestrator V10) OU
                lista flat de exames.
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


INTERPRETACAO_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "schema_version": {"type": "string"},
        "sistema": {"type": "string"},
        "exames_interpretados": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "nome": {"type": "string"},
                    "valor": {"type": "string"},
                    "unidade": {"type": "string"},
                    "referencia": {"type": "string"},
                    "status_validador": {"type": "string",
                                         "enum": ["normal", "alterado", "alert", "crit"]},
                    "diagnostico_tendencia": {
                        "type": "string",
                        "description": "Tendência clínica: 'normal', 'normal-limítrofe', 'pré-X', 'X estabelecido', 'risco de X'. NÃO conclui diagnóstico definitivo."
                    },
                    "risco_curto_prazo": {
                        "type": "string",
                        "description": "O que esse valor representa em risco clínico nos próximos 3-12 meses. Frase técnica curta."
                    },
                    "risco_medio_prazo": {
                        "type": "string",
                        "description": "Risco em 1-5 anos se não tratado. Frase técnica curta."
                    },
                    "fator_etiologico_provavel": {
                        "type": "string",
                        "description": "Hipótese etiológica principal (ex: 'deficiência por baixa ingesta', 'resistência insulínica', 'perimenopausa'). Sem afirmação definitiva."
                    },
                    "severidade": {
                        "type": "integer",
                        "enum": [1, 2, 3, 4, 5],
                        "description": "1=irrelevante; 2=monitorar; 3=alterado leve; 4=alterado significativo; 5=crítico/urgente"
                    },
                    "investigacao_adicional": {
                        "type": "string",
                        "description": "Sugestão de exames complementares OU 'nenhuma' se não aplicável"
                    }
                },
                "required": ["nome", "valor", "unidade", "referencia", "status_validador",
                             "diagnostico_tendencia", "risco_curto_prazo", "risco_medio_prazo",
                             "fator_etiologico_provavel", "severidade", "investigacao_adicional"]
            }
        },
        "sintese_do_sistema": {
            "type": "string",
            "description": "1-2 parágrafos integrando os achados deste sistema. Tom técnico, compliance CFM, sem diagnóstico definitivo."
        },
        "alertas_criticos": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "exame": {"type": "string"},
                    "motivo": {"type": "string"},
                    "acao_clinica_sugerida": {"type": "string"}
                },
                "required": ["exame", "motivo", "acao_clinica_sugerida"]
            }
        }
    },
    "required": ["schema_version", "sistema", "exames_interpretados", "sintese_do_sistema",
                 "alertas_criticos"]
}


SYSTEM_PROMPT = """Você é uma médica clínica integrativa sênior do Instituto Vital Slim, com forte expertise em endocrinologia metabólica, hormônios femininos/masculinos, nutrição funcional e medicina preventiva.

Sua tarefa: interpretar exames laboratoriais já EXTRAÍDOS e VALIDADOS, gerando análise clínica POR EXAME com:
- diagnóstico de tendência (sem ser definitivo)
- riscos associados curto/médio prazo
- fator etiológico provável
- severidade 1-5

REGRAS ABSOLUTAS (compliance CFM):
1. NUNCA escreva diagnóstico definitivo. Use sempre "sugere", "compatível com", "tendência a", "risco de", "possível".
2. NÃO prometa cura nem reversão.
3. NÃO indique medicação direta. Pode sugerir "avaliação clínica para considerar X" mas nunca prescrever.
4. NÃO use linguagem alarmista. Tom técnico, factual, sóbrio.
5. Use referências IVS conservadoras quando aplicável:
   - HbA1c: <5,4 ótimo / 5,4-5,7 atenção / 5,8-6,4 pré-diabetes / ≥6,5 diabetes
   - Glicemia jejum: <90 ótimo / 90-99 atenção / 100-125 pré-DM / ≥126 DM
   - Vit D: <30 deficiência / 30-50 insuficiência / 50-80 OK / >80 ótimo IVS
   - B12: <300 deficiência / 300-500 limítrofe / >500 OK / >800 ótimo IVS
   - Ferritina (F): <30 ferropriva / 30-50 baixa / 50-150 OK / >150 atenção
   - TSH: <0,5 sub-hiper / 0,5-2,5 ótimo IVS / 2,5-4,0 atenção / >4,0 sub-hipo
   - LDL: <100 ótimo / 100-129 limítrofe / 130-159 alto / ≥160 muito alto
   - HDL: F >50 / M >40
   - Triglicérides: <150 OK / ≥150 alto
   - Insulina jejum: <10 OK / 10-15 atenção / >15 resistência
   - HOMA-IR: <2,0 OK / 2,0-2,5 atenção / >2,5 resistência
   - Testo Total (M): >400 ng/dL ótimo IVS / 300-400 baixo-limítrofe / <300 hipogonadismo
6. Para mulheres em perimenopausa/menopausa, valorizar contexto hormonal nos achados.
7. Severidade 5 só para valores que merecem atenção médica em até 7 dias (ex: HbA1c >7, TSH >10, PSA muito alto, etc.).
8. Severidade 1-2 são achados normais ou monitoráveis a longo prazo.

NÃO inclua exames que vieram dentro da faixa de referência E que não merecem comentário técnico. Foque nos que têm valor clínico real.

Responda APENAS com JSON válido conforme schema fornecido."""


def _validar_schema_manual(data, schema):
    if not isinstance(data, dict):
        raise ValueError("response não é dict")
    required = schema.get("required", [])
    missing = [k for k in required if k not in data]
    if missing:
        raise ValueError(f"campos obrigatórios faltando: {missing}")
    return True


def chamar_openrouter(messages, schema, max_retries=2):
    api_key = _load_api_key()
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY não configurada")

    schema_str = json.dumps(schema, ensure_ascii=False, indent=2)
    schema_instruction = f"\n\nSCHEMA OBRIGATÓRIO DO JSON DE RESPOSTA (siga exatamente):\n```json\n{schema_str}\n```"
    messages_with_schema = messages.copy()
    if messages_with_schema and messages_with_schema[0]["role"] == "system":
        messages_with_schema[0] = {
            "role": "system",
            "content": messages_with_schema[0]["content"] + schema_instruction,
        }

    body = {
        "messages": messages_with_schema,
        "response_format": {"type": "json_object"},
        "temperature": 0.1,
        "max_tokens": 12000,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://institutovitalslim.com.br",
        "X-Title": "IVS V11 Interpretacao Clinica",
    }

    models = [MODEL] + FALLBACK_MODELS
    last_err = None

    for try_model in models:
        body["model"] = try_model
        for attempt in range(1, max_retries + 1):
            try:
                req = urllib.request.Request(
                    OPENROUTER_BASE,
                    data=json.dumps(body).encode("utf-8"),
                    headers=headers, method="POST"
                )
                with urllib.request.urlopen(req, timeout=180) as r:
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
            except (urllib.error.HTTPError, json.JSONDecodeError, ValueError) as e:
                err_str = str(e)
                if isinstance(e, urllib.error.HTTPError) and e.fp:
                    err_str = f"HTTP {e.code}: {e.read().decode()[:300]}"
                last_err = f"{try_model} attempt {attempt}: {err_str[:300]}"
                print(f"[WARN] {last_err}", file=sys.stderr)
                if attempt < max_retries:
                    time.sleep(2 ** attempt)
                    continue
                break
            except Exception as e:
                last_err = f"{try_model} attempt {attempt}: {e}"
                print(f"[WARN] {last_err}", file=sys.stderr)
                if attempt < max_retries:
                    time.sleep(2 ** attempt)
                    continue
                break

    raise RuntimeError(f"Todos os modelos falharam: {last_err}")


SISTEMA_LABELS = {
    "tireoide": "Tireoide",
    "metabolico": "Metabólico",
    "hormonal_feminino": "Hormonal Feminino",
    "hormonal_masculino": "Hormonal Masculino",
    "hematologico": "Hematológico",
    "hepatico": "Hepático",
    "renal": "Renal",
    "inflamatorio": "Inflamatório",
    "nutricional": "Nutricional / Vitaminas / Minerais",
    "cardiovascular": "Cardiovascular",
    "lipidico": "Lipídico",
    "urinario": "Urinário",
    "outros": "Outros",
}


def _agrupar_por_sistema(exames_input):
    """Recebe formato grupos OU lista flat e agrupa por sistema fisiológico."""
    grupos = {}

    if isinstance(exames_input, dict) and "grupos" in exames_input:
        # formato orchestrator
        for grupo in exames_input["grupos"]:
            sys_name = grupo.get("nome", "outros").lower().strip()
            sys_key = _normalizar_sistema(sys_name)
            grupos.setdefault(sys_key, []).extend(grupo.get("exames", []))
    elif isinstance(exames_input, list):
        for ex in exames_input:
            sys_name = ex.get("grupo") or ex.get("categoria") or "outros"
            sys_key = _normalizar_sistema(sys_name)
            grupos.setdefault(sys_key, []).append(ex)
    else:
        raise ValueError("formato de exames não reconhecido")

    return grupos


def _normalizar_sistema(nome):
    n = nome.lower().strip()
    # ordem importa — patterns mais específicos primeiro
    mapeamento = [
        ("tireoide", "tireoide"), ("tireoid", "tireoide"), ("tsh", "tireoide"), ("t4", "tireoide"), ("t3", "tireoide"),
        ("hemograma", "hematologico"), ("hematolog", "hematologico"),
        ("perfil lipid", "lipidico"), ("lipidio", "lipidico"), ("lipidograma", "lipidico"),
        ("lipido", "lipidico"), ("colesterol", "lipidico"), ("triglic", "lipidico"),
        ("perfil glic", "metabolico"), ("metabolic", "metabolico"), ("glicem", "metabolico"),
        ("diabet", "metabolico"), ("insulin", "metabolico"), ("homa", "metabolico"),
        ("hepatic", "hepatico"), ("figado", "hepatico"), ("transamin", "hepatico"),
        ("renal", "renal"), ("rim", "renal"), ("ureia", "renal"), ("creatinin", "renal"),
        ("hormonal sex", "hormonal_feminino"),  # context inferido pelo sexo do paciente
        ("hormonal fem", "hormonal_feminino"), ("ginecolog", "hormonal_feminino"),
        ("estradiol", "hormonal_feminino"), ("progester", "hormonal_feminino"),
        ("fsh", "hormonal_feminino"), ("lh", "hormonal_feminino"),
        ("hormonal masc", "hormonal_masculino"), ("testosteron", "hormonal_masculino"),
        ("dhea", "hormonal_feminino"), ("shbg", "hormonal_feminino"),
        ("marcador inflam", "inflamatorio"), ("inflamatori", "inflamatorio"),
        ("pcr", "inflamatorio"), ("vhs", "inflamatorio"),
        ("vitaminas e minerais", "nutricional"), ("vitamina", "nutricional"),
        ("mineral", "nutricional"), ("nutricional", "nutricional"),
        ("ferro", "nutricional"), ("ferritin", "nutricional"), ("zinco", "nutricional"),
        ("magnesio", "nutricional"), ("b12", "nutricional"),
        ("cardiovascular", "cardiovascular"), ("cardio", "cardiovascular"),
        ("homocistein", "cardiovascular"), ("apo", "cardiovascular"),
        ("urinari", "urinario"), ("urina", "urinario"), ("eas", "urinario"),
    ]
    for k, v in mapeamento:
        if k in n:
            return v
    return "outros"


def interpretar_sistema(sistema, exames, paciente_meta):
    """Chama o LLM para interpretar um sistema fisiológico."""
    sexo = paciente_meta.get("sexo", "")
    idade = paciente_meta.get("idade", "")
    nome_pac = paciente_meta.get("nome", "")

    exames_resumo = []
    for ex in exames:
        exames_resumo.append({
            "nome": ex.get("nome", ""),
            "valor": str(ex.get("valor", "")),
            "unidade": ex.get("unit") or ex.get("unidade", ""),
            "referencia": ex.get("ref") or ex.get("referencia", ""),
            "status": ex.get("status", "normal"),
            "alterado": ex.get("alterado", False),
        })

    user_msg = f"""Interprete clinicamente os exames abaixo do sistema **{SISTEMA_LABELS.get(sistema, sistema)}**.

Paciente: {nome_pac}, sexo {sexo}, {idade} anos.

EXAMES (JSON):
{json.dumps(exames_resumo, ensure_ascii=False, indent=2)}

INSTRUÇÕES:
- Inclua TODOS os exames listados, mesmo os normais (status: normal). Para normais, marque severidade 1 ou 2 e use diagnóstico_tendencia="normal".
- Riscos curto/médio prazo: descreva o que cada valor representa CLINICAMENTE, não apenas defina o exame.
- alertas_criticos: liste APENAS valores severidade 4-5 que merecem ação prioritária.
- sintese_do_sistema: 1-2 parágrafos integrando os achados deste sistema com vista compliance CFM.
- O campo "sistema" do JSON de resposta DEVE ser "{sistema}" exatamente."""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_msg}
    ]
    return chamar_openrouter(messages, INTERPRETACAO_SCHEMA)


def interpretar_todos_exames(exames_input, paciente_meta):
    """Roda interpretação por sistema. Retorna dict {sistema: resultado}."""
    grupos = _agrupar_por_sistema(exames_input)
    resultado = {
        "schema_version": SCHEMA_VERSION,
        "paciente": paciente_meta,
        "sistemas": {},
        "alertas_criticos_globais": [],
        "total_exames_interpretados": 0,
        "usage_total": {"input": 0, "output": 0, "cost": 0.0}
    }

    for sistema, exames in grupos.items():
        if not exames:
            continue
        print(f"[V11/etapa 3] Interpretando sistema '{sistema}' com {len(exames)} exames...", file=sys.stderr)
        t0 = time.time()
        try:
            sys_resp, usage = interpretar_sistema(sistema, exames, paciente_meta)
            dt = time.time() - t0
            print(f"  ✓ {sistema} OK em {dt:.1f}s (modelo: {usage.get('model_used','?')})", file=sys.stderr)
            resultado["sistemas"][sistema] = sys_resp
            resultado["alertas_criticos_globais"].extend(sys_resp.get("alertas_criticos", []))
            resultado["total_exames_interpretados"] += len(sys_resp.get("exames_interpretados", []))
            resultado["usage_total"]["input"] += usage.get("prompt_tokens", 0)
            resultado["usage_total"]["output"] += usage.get("completion_tokens", 0)
            resultado["usage_total"]["cost"] += usage.get("cost", 0) or 0
        except Exception as e:
            print(f"  ✗ {sistema} FALHOU: {e}", file=sys.stderr)
            resultado["sistemas"][sistema] = {"erro": str(e), "exames": [e.get("nome") for e in exames]}

    return resultado


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("exames", help="Caminho JSON dos exames extraídos (formato V10 grupos OU lista flat)")
    ap.add_argument("--paciente-nome", default="")
    ap.add_argument("--paciente-sexo", default="", help="F ou M")
    ap.add_argument("--paciente-idade", type=int, default=0)
    ap.add_argument("--output", default="", help="Output path. Default: state/auditoria_v11/<slug>_<ts>/etapa_3_interpretacao.json")
    args = ap.parse_args()

    with open(args.exames) as f:
        exames_input = json.load(f)

    paciente_meta = {
        "nome": args.paciente_nome,
        "sexo": args.paciente_sexo,
        "idade": args.paciente_idade
    }

    print(f"[V11/etapa 3] Iniciando interpretação clínica...", file=sys.stderr)
    t0 = time.time()
    resultado = interpretar_todos_exames(exames_input, paciente_meta)
    dt = time.time() - t0

    if args.output:
        out_path = Path(args.output)
    else:
        slug = re.sub(r"[^\w\-]", "-", paciente_meta["nome"].lower())
        slug = re.sub(r"-+", "-", slug).strip("-")
        ts = time.strftime("%Y%m%d_%H%M%S")
        base = Path("/root/cerebro-vital-slim/skills/geracao-apresentacao-paciente/state/auditoria_v11")
        out_path = base / f"{slug}_{ts}" / "etapa_3_interpretacao.json"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    # Gate da etapa 3
    sistemas_ok = sum(1 for s, v in resultado["sistemas"].items() if "erro" not in v)
    sistemas_fail = len(resultado["sistemas"]) - sistemas_ok
    gate_ok = resultado["total_exames_interpretados"] >= 5 and sistemas_fail == 0

    print(json.dumps({
        "etapa": 3,
        "output_path": str(out_path),
        "modelo_primario": MODEL,
        "duracao_total_s": round(dt, 1),
        "sistemas_processados": list(resultado["sistemas"].keys()),
        "sistemas_ok": sistemas_ok,
        "sistemas_fail": sistemas_fail,
        "total_exames_interpretados": resultado["total_exames_interpretados"],
        "alertas_criticos": len(resultado["alertas_criticos_globais"]),
        "usage_total": resultado["usage_total"],
        "gate_ok": gate_ok,
    }, ensure_ascii=False, indent=2))

    sys.exit(0 if gate_ok else 1)


if __name__ == "__main__":
    main()
