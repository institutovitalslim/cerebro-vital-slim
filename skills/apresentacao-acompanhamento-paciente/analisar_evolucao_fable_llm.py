#!/usr/bin/env python3
"""Análise de evolução de exames usando Claude Fable 5 via OpenRouter.

Para apresentações de pacientes em PROGRAMA DE ACOMPANHAMENTO (devolutiva pós-protocolo).

Diferente do V11 (paciente novo, foco em diagnóstico inicial), aqui o foco é:
- comparar EXAME ATUAL vs EXAME ANTERIOR (mesmo paciente, datas diferentes)
- gerar narrativa de evolução em tom de jornada/conquista (não diagnóstico)
- conectar o que o paciente sentiu com o que o exame confirma
- destacar vitórias (melhorias) e pontos ainda em ajuste

Por que Fable 5: modelo Claude otimizado para criação de conteúdo narrativo.
Tom mais humano e vivo que Sonnet (que é mais técnico/clínico).

Uso:
    python3 analisar_evolucao_fable_llm.py <exames_atuais.json> <exames_anteriores.json> \\
        --paciente-nome <nome> --paciente-sexo F --paciente-idade 49 \\
        [--queixas-iniciais "fadiga, ganho de peso"] [--output OUT]

Schema do output:
    {
      "paciente": {...},
      "intervalo_meses": N,
      "evolucao_por_parametro": [
        {
          "nome": "Vitamina D",
          "valor_anterior": "18 ng/mL",
          "valor_atual": "52 ng/mL",
          "delta_pct": +189,
          "status_evolucao": "melhorou_muito | melhorou | estavel | piorou | piorou_muito",
          "narrativa_fable": "Sua vitamina D estava em deficiência (18) e subiu para ótima (52). Isso explica boa parte do ganho de energia que você relatou nas últimas semanas."
        }
      ],
      "vitorias_principais": ["..."],
      "pontos_em_ajuste": ["..."],
      "sintese_jornada": "2-3 parágrafos narrativos sobre a evolução, escritos para a paciente",
      "proximo_passo_sugerido": "frase curta orientando próximos meses"
    }
"""
from __future__ import annotations
import argparse, json, os, re, sys, time, urllib.request, urllib.error
from pathlib import Path

OPENROUTER_BASE = "https://openrouter.ai/api/v1/chat/completions"
MODEL_PRIMARIO = "anthropic/claude-fable-5"  # narrativa + raciocinio clinico via OpenRouter (primario Ana/apresentacoes)
MODEL_FALLBACK = "anthropic/claude-opus-4.8"  # fallback de maior raciocinio quando Fable nao estiver liberado
MODEL_FALLBACK_2 = "anthropic/claude-sonnet-4.6"  # fallback operacional rapido
SCHEMA_VERSION = "evolucao-v1"


def _load_api_key():
    for p in ["/root/.openclaw/.env.runtime", "/root/.openclaw/.env"]:
        if not os.path.exists(p):
            continue
        for line in open(p):
            line = line.strip()
            if line.startswith("OPENROUTER_API_KEY="):
                v = line.split("=", 1)[1].strip().strip('"').strip("'")
                if v and not v.startswith("op://"):
                    return v
    return os.environ.get("OPENROUTER_API_KEY", "")


SYSTEM_PROMPT = """Você é uma redatora clínica do Instituto Vital Slim, especialista em traduzir resultados de exames em narrativa de jornada pra paciente.

Sua tarefa: gerar texto humano, vivo, em primeira pessoa para o paciente, comparando exames de DIFERENTES MOMENTOS do tratamento.

REGRAS ABSOLUTAS:
1. Você está conversando COM o paciente, não fazendo laudo médico.
2. Tom: humano, claro, sem jargão pesado. Como uma amiga médica explicando.
3. Vitórias merecem destaque ("você conseguiu", "boa resposta"), pioras merecem honestidade sem alarmismo ("esse ponto pediu mais atenção, vamos ajustar").
4. Conecta SEMPRE o exame com a experiência humana ("isso explica o cansaço que diminuiu", "por isso a roupa começou a folgar").
5. NÃO diagnostica. Usa "sugere", "indica", "está compatível com".
6. NÃO prometa cura ou resultado futuro garantido.
7. NÃO use lista interminável de termos técnicos. Foque no que mudou e o que isso significa pra ela.
8. Compliance CFM: nada de tratamento prescrito direto, só "o caminho mostrou ser X".

CONTEXTO IVS:
- Pacientes em programa de acompanhamento de 6+ meses.
- Foco em metabolismo, hormônios, composição corporal.
- A apresentação é entregue na consulta de DEVOLUTIVA.

Responda APENAS em JSON válido conforme schema fornecido."""


EVOLUCAO_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "schema_version": {"type": "string"},
        "intervalo_meses": {"type": "number"},
        "evolucao_por_parametro": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "nome": {"type": "string"},
                    "valor_anterior": {"type": "string"},
                    "valor_atual": {"type": "string"},
                    "delta_pct": {"type": "number"},
                    "direcao": {"type": "string", "enum": ["melhorou_muito", "melhorou", "estavel", "piorou", "piorou_muito"]},
                    "narrativa_fable": {"type": "string", "description": "1-2 frases humanas em primeira pessoa explicando essa evolução específica pro paciente"}
                },
                "required": ["nome", "valor_anterior", "valor_atual", "delta_pct", "direcao", "narrativa_fable"]
            }
        },
        "vitorias_principais": {
            "type": "array",
            "items": {"type": "string"},
            "description": "3-5 conquistas mais relevantes do período, em linguagem leiga"
        },
        "pontos_em_ajuste": {
            "type": "array",
            "items": {"type": "string"},
            "description": "1-3 pontos que ainda merecem trabalho — tom honesto, sem alarmismo"
        },
        "sintese_jornada": {
            "type": "string",
            "description": "2-3 parágrafos narrativos contando a jornada do paciente neste período. Tom: amiga médica, primeira pessoa do paciente, conectando exame e experiência. Sem jargão."
        },
        "proximo_passo_sugerido": {
            "type": "string",
            "description": "1 frase curta sobre o foco dos próximos 3-6 meses"
        }
    },
    "required": ["schema_version", "intervalo_meses", "evolucao_por_parametro",
                 "vitorias_principais", "pontos_em_ajuste", "sintese_jornada", "proximo_passo_sugerido"]
}


def _validar(data, schema):
    missing = [k for k in schema.get("required", []) if k not in data]
    if missing:
        raise ValueError(f"campos obrigatórios faltando: {missing}")
    return True


def chamar_fable(messages, schema, max_retries=2):
    api_key = _load_api_key()
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY não configurada")

    schema_str = json.dumps(schema, ensure_ascii=False, indent=2)
    instr = f"\n\nSCHEMA OBRIGATÓRIO:\n```json\n{schema_str}\n```"
    msgs = messages.copy()
    if msgs and msgs[0]["role"] == "system":
        msgs[0] = {"role": "system", "content": msgs[0]["content"] + instr}

    body = {
        "messages": msgs,
        "response_format": {"type": "json_object"},
        "temperature": 0.5,  # mais criativo que Sonnet, mas controlado
        "max_tokens": 8000,
    }
    headers = {
        "Authorization": f"Bearer {api_key}", "Content-Type": "application/json",
        "HTTP-Referer": "https://institutovitalslim.com.br",
        "X-Title": "IVS Evolucao Fable",
    }

    last_err = None
    for try_model in [MODEL_PRIMARIO, MODEL_FALLBACK, MODEL_FALLBACK_2]:
        body["model"] = try_model
        for attempt in range(1, max_retries + 1):
            try:
                req = urllib.request.Request(OPENROUTER_BASE, data=json.dumps(body).encode(),
                                              headers=headers, method="POST")
                with urllib.request.urlopen(req, timeout=180) as r:
                    resp = json.loads(r.read().decode())
                    content = resp["choices"][0]["message"]["content"].strip()
                    if content.startswith("```"):
                        content = re.sub(r"^```(?:json)?\s*", "", content)
                        content = re.sub(r"\s*```$", "", content)
                    parsed = json.loads(content)
                    _validar(parsed, schema)
                    usage = resp.get("usage", {})
                    usage["model_used"] = try_model
                    return parsed, usage
            except Exception as e:
                err = str(e)
                if isinstance(e, urllib.error.HTTPError) and e.fp:
                    err = f"HTTP {e.code}: {e.read().decode()[:200]}"
                last_err = f"{try_model} attempt {attempt}: {err}"
                print(f"[WARN] {last_err}", file=sys.stderr)
                if attempt < max_retries:
                    time.sleep(2 ** attempt)
                    continue
                break
    raise RuntimeError(f"Todos os modelos falharam: {last_err}")


def _pares_para_comparar(atuais, anteriores):
    """Cruza exames atual vs anterior pelo nome (case-insensitive, normalizado)."""
    def _key(nome):
        return re.sub(r"[^\w]", "", nome.lower())

    def _flatten(data):
        if isinstance(data, dict) and "grupos" in data:
            out = []
            for g in data["grupos"]:
                for ex in g.get("exames", []):
                    out.append({**ex, "_grupo": g.get("nome", "")})
            return out
        elif isinstance(data, list):
            return data
        return []

    flat_at = _flatten(atuais)
    flat_an = _flatten(anteriores)

    idx_an = {_key(ex.get("nome", "")): ex for ex in flat_an}
    pares = []
    for ex_at in flat_at:
        k = _key(ex_at.get("nome", ""))
        ex_an = idx_an.get(k)
        if ex_an:
            pares.append({
                "nome": ex_at.get("nome", ""),
                "atual": ex_at,
                "anterior": ex_an,
            })
    return pares


def analisar_evolucao(exames_atuais, exames_anteriores, paciente_meta, queixas_iniciais="", intervalo_meses=6):
    pares = _pares_para_comparar(exames_atuais, exames_anteriores)
    if not pares:
        raise RuntimeError("Nenhum exame em comum entre as duas datas encontrado.")

    primeiro_nome = (paciente_meta.get("nome", "") or "").split()[0] or "Paciente"
    sexo = paciente_meta.get("sexo", "")
    idade = paciente_meta.get("idade", "")

    pares_resumo = []
    for p in pares:
        pares_resumo.append({
            "nome": p["nome"],
            "valor_anterior": str(p["anterior"].get("valor", "")),
            "valor_atual": str(p["atual"].get("valor", "")),
            "unidade": p["atual"].get("unidade", "") or p["anterior"].get("unidade", ""),
            "ref": p["atual"].get("ref", "") or p["anterior"].get("ref", ""),
            "status_atual": p["atual"].get("status", ""),
            "status_anterior": p["anterior"].get("status", ""),
        })

    user_msg = f"""Analise a EVOLUÇÃO dos exames de **{primeiro_nome}** ({sexo}, {idade} anos) no período de aproximadamente {intervalo_meses} meses.

QUEIXAS INICIAIS DO PACIENTE (quando começou o programa):
{queixas_iniciais or "não informado pelo orchestrator"}

EXAMES COMPARADOS ({len(pares_resumo)} parâmetros):
{json.dumps(pares_resumo, ensure_ascii=False, indent=2)}

INSTRUÇÕES:
- Para cada parâmetro com mudança RELEVANTE (delta_pct >= 10% OU mudança de status normal/alterado/crit), gere uma narrativa Fable em 1-2 frases.
- Para parâmetros pouco mudados, classifique como "estavel" e use narrativa curta.
- Vitorias_principais: 3-5 conquistas que vão emocionar/motivar o paciente.
- Pontos_em_ajuste: 1-3 pontos honestos, sem alarmismo.
- Sintese_jornada: 2-3 parágrafos narrativos em primeira pessoa do paciente, conectando exames + experiência humana.
- Próximo_passo_sugerido: 1 frase curta.
- schema_version DEVE ser exatamente "{SCHEMA_VERSION}"."""

    return chamar_fable([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_msg}
    ], EVOLUCAO_SCHEMA)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("exames_atuais", help="JSON com exames atuais (formato V10 grupos OU lista flat)")
    ap.add_argument("exames_anteriores", help="JSON com exames de avaliação anterior")
    ap.add_argument("--paciente-nome", default="")
    ap.add_argument("--paciente-sexo", default="")
    ap.add_argument("--paciente-idade", type=int, default=0)
    ap.add_argument("--intervalo-meses", type=float, default=6.0)
    ap.add_argument("--queixas-iniciais", default="")
    ap.add_argument("--output", default="")
    args = ap.parse_args()

    atuais = json.load(open(args.exames_atuais))
    anteriores = json.load(open(args.exames_anteriores))
    meta = {"nome": args.paciente_nome, "sexo": args.paciente_sexo, "idade": args.paciente_idade}

    print(f"[Evolução/Fable] iniciando análise pra {args.paciente_nome}...", file=sys.stderr)
    t0 = time.time()
    resultado, usage = analisar_evolucao(
        atuais, anteriores, meta,
        queixas_iniciais=args.queixas_iniciais,
        intervalo_meses=args.intervalo_meses
    )
    dt = time.time() - t0

    if args.output:
        out_path = Path(args.output)
    else:
        slug = re.sub(r"[^\w\-]", "-", args.paciente_nome.lower()).strip("-")
        ts = time.strftime("%Y%m%d_%H%M%S")
        base = Path("/root/cerebro-vital-slim/skills/apresentacao-acompanhamento-paciente/state/evolucao")
        out_path = base / f"{slug}_{ts}" / "evolucao_fable.json"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    n_evol = len(resultado.get("evolucao_por_parametro", []))
    n_vit = len(resultado.get("vitorias_principais", []))
    n_aj = len(resultado.get("pontos_em_ajuste", []))

    print(json.dumps({
        "etapa": "evolucao_fable",
        "output": str(out_path),
        "modelo_usado": usage.get("model_used"),
        "duracao_s": round(dt, 1),
        "parametros_analisados": n_evol,
        "vitorias": n_vit,
        "pontos_ajuste": n_aj,
        "usage": usage,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
