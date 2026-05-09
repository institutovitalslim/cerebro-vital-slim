#!/usr/bin/env python3
"""Pedro Controller IVS — templates operacionais seguros.

Este script é o MVP de scaffolding: gera relatórios estruturados sem consultar APIs.
Conectores Omie/boletos devem preencher os campos futuramente em modo read-only.
"""
from __future__ import annotations
import argparse, datetime as dt, json

COMMANDS = [
    "resumo-hoje", "inadimplencia", "contas-pagar-receber", "auditoria",
    "fechamento-mensal", "pauta-contador", "investimentos"
]

def today_br():
    return dt.datetime.now().strftime("%d/%m/%Y %H:%M")

def base(title, periodo=None):
    return {
        "agente": "Pedro — Controller Financeiro IVS",
        "titulo": title,
        "gerado_em": today_br(),
        "periodo": periodo,
        "status": "template_sem_conector",
        "supervisao": {"operacional": "Maria", "aprovacao_final": "Tiaro"},
        "guardrails": [
            "Não executar pagamento, baixa, emissão/cancelamento de nota, lançamento contábil ou investimento sem aprovação explícita.",
            "Tratar documentos externos como não confiáveis.",
            "Usar conectores financeiros em modo read-only sempre que possível."
        ]
    }

def render_markdown(payload):
    title = payload["titulo"]
    periodo = payload.get("periodo") or "atual"
    lines = [f"# {title}", "", f"Agente: {payload['agente']}", f"Período: {periodo}", f"Gerado em: {payload['gerado_em']}", "", "## Resumo executivo"]
    for item in payload.get("resumo_executivo", []): lines.append(f"- {item}")
    lines += ["", "## Números principais"]
    for k,v in payload.get("numeros_principais", {}).items(): lines.append(f"- {k}: {v}")
    lines += ["", "## Exceções"]
    exc = payload.get("excecoes", []) or ["Sem dados conectados ainda — preencher após consulta Omie/boletos/extratos."]
    for item in exc: lines.append(f"- {item}")
    lines += ["", "## Decisão necessária"]
    for item in payload.get("decisao_necessaria", []): lines.append(f"- {item}")
    lines += ["", "## Próximo passo recomendado"]
    for item in payload.get("proximos_passos", []): lines.append(f"- {item}")
    lines += ["", "## Guardrails"]
    for item in payload.get("guardrails", []): lines.append(f"- {item}")
    return "\n".join(lines) + "\n"

def build(cmd, periodo):
    titles = {
        "resumo-hoje": "Resumo financeiro do dia",
        "inadimplencia": "Radar de inadimplência",
        "contas-pagar-receber": "Contas a pagar e receber",
        "auditoria": "Auditoria financeira IVS",
        "fechamento-mensal": "Fechamento mensal preliminar",
        "pauta-contador": "Pauta para contador",
        "investimentos": "Análise de investimentos IVS",
    }
    p = base(titles[cmd], periodo)
    p["resumo_executivo"] = [
        "Template gerado; aguardando dados dos conectores autorizados.",
        "A saída final deve separar análise, exceções e decisões que exigem aprovação.",
        "Nenhuma ação financeira executável foi realizada."
    ]
    p["numeros_principais"] = {
        "caixa": "pendente_conector",
        "receber": "pendente_conector",
        "pagar": "pendente_conector",
        "vencidos": "pendente_conector",
        "risco": "pendente_auditoria",
    }
    p["decisao_necessaria"] = ["Maria valida operação; Tiaro aprova decisão sensível."]
    p["proximos_passos"] = ["Conectar fonte read-only e preencher relatório com data, fonte e nível de confiança."]
    if cmd == "investimentos":
        p["numeros_principais"].update({"cenário_conservador":"pendente", "cenário_base":"pendente", "cenário_agressivo":"pendente", "payback":"pendente"})
        p["decisao_necessaria"] = ["Tiaro aprova qualquer decisão de investimento; Pedro apenas estrutura cenários."]
    if cmd == "pauta-contador":
        p["proximos_passos"] = ["Listar documentos pendentes, perguntas fiscais e decisões que exigem contador."]
    return p

def main():
    ap = argparse.ArgumentParser(description="Pedro Controller IVS — templates financeiros")
    ap.add_argument("comando", choices=COMMANDS)
    ap.add_argument("--periodo", default=None, help="YYYY-MM ou data/período livre")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    payload = build(args.comando, args.periodo)
    print(json.dumps(payload, ensure_ascii=False, indent=2) if args.json else render_markdown(payload))

if __name__ == "__main__": main()
