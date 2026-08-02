from __future__ import annotations

import argparse
import html
import json
from pathlib import Path


def _pct(value: float) -> str:
    return f"{value * 100:.1f}%".replace(".", ",")


def _ms(value: float) -> str:
    if value >= 1000:
        return f"{value / 1000:.2f} s".replace(".", ",")
    return f"{value:.2f} ms".replace(".", ",")


def _gate_value(name: str, value: float) -> str:
    return _ms(value) if "latency" in name else _pct(value)


def _esc(value: object) -> str:
    return html.escape(str(value))


def render_html(payload: dict) -> str:
    g = payload["gbrain"]
    p = payload["pgvector"]
    decision = payload["decision"]
    g_rows = "".join(
        f"<tr><td>{_esc(row['name'])}</td><td><code>{_esc(row['query'])}</code></td>"
        f"<td><span class='badge {'ok' if row['passed'] else 'fail'}'>{'PASSOU' if row['passed'] else 'FALHOU'}</span></td>"
        f"<td>{_ms(row['latency_ms'])}</td></tr>"
        for row in g.get("results", [])
    ) or "<tr><td colspan='4'>Sem detalhamento nesta amostra.</td></tr>"
    p_rows = "".join(
        f"<tr><td>{_esc(row['name'])}</td><td><code>{_esc(row['expected'])}</code></td>"
        f"<td><code>{_esc(row['retrieved'][0] if row.get('retrieved') else '—')}</code></td>"
        f"<td>{_ms(row['latency_ms'])}</td></tr>"
        for row in p.get("results", [])
    ) or "<tr><td colspan='4'>Sem detalhamento nesta amostra.</td></tr>"
    gate_rows = "".join(
        f"<tr><td><code>{_esc(gate['name'])}</code></td>"
        f"<td>{_gate_value(gate['name'], gate['observed'])}</td>"
        f"<td>{_esc(gate['comparator'])} {_gate_value(gate['name'], gate['threshold'])}</td>"
        f"<td><span class='badge {'ok' if gate['passed'] else 'fail'}'>{'PASSOU' if gate['passed'] else 'FALHOU'}</span></td>"
        f"<td>{_esc(gate['scope'])}</td></tr>"
        for gate in payload.get("gates", [])
    ) or "<tr><td colspan='5'>Gates não disponíveis nesta evidência.</td></tr>"
    plan = p.get("execution_plan", {})
    hnsw_used = "sim" if plan.get("hnsw_used_by_default") else "não"
    decision_title = {
        "KEEP_GBRAIN_NO_STANDALONE_PGVECTOR": "Manter o GBrain sem pgvector independente",
        "INVESTIGATE_GBRAIN_GAP_NO_STANDALONE_DECISION": "Investigar a lacuna do GBrain sem criar banco paralelo",
    }.get(decision["decision"], "Decisão condicionada a nova evidência equivalente")
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>IVS — Benchmark pgvector × GBrain</title>
<style>
:root{{--ink:#17221d;--muted:#65716b;--paper:#f4f1e9;--card:#fffdfa;--green:#173f32;--lime:#b9d96b;--gold:#c99a44;--line:#dcd8cd;--red:#9a3f3f}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--paper);color:var(--ink);font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,sans-serif;line-height:1.5}}
header{{background:linear-gradient(135deg,#102e25,#1e4c3d);color:white;padding:56px 7vw 48px;position:relative;overflow:hidden}}
header:after{{content:"";position:absolute;width:380px;height:380px;border:70px solid rgba(185,217,107,.12);border-radius:50%;right:-90px;top:-180px}}
.brand{{font-size:13px;letter-spacing:.18em;text-transform:uppercase;color:var(--lime);font-weight:800}} h1{{font-size:clamp(32px,5vw,58px);line-height:1.03;max-width:900px;margin:16px 0}}
.subtitle{{max-width:820px;color:#dce8e1;font-size:18px}} main{{width:min(1180px,90vw);margin:-28px auto 64px;position:relative}}
.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}} .card{{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:22px;box-shadow:0 10px 30px rgba(22,45,36,.06)}}
.metric strong{{display:block;font-size:30px;color:var(--green)}} .metric span{{color:var(--muted);font-size:13px}} section{{margin-top:24px}}
.decision{{border-left:7px solid var(--lime);padding:30px}} .decision h2{{margin:0 0 8px;font-size:28px}} .code-label{{font:700 12px ui-monospace,SFMono-Regular,monospace;color:var(--green);background:#e7efda;padding:6px 9px;border-radius:8px;display:inline-block}}
h2{{font-size:25px;margin:0 0 16px}} h3{{margin:22px 0 10px}} .warning{{background:#fff4d8;border:1px solid #e6c978;border-radius:14px;padding:16px 18px;color:#5c4817}}
table{{width:100%;border-collapse:collapse;font-size:14px}} th{{text-align:left;color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.07em}} th,td{{padding:12px 10px;border-bottom:1px solid var(--line);vertical-align:top}} code{{font-family:ui-monospace,SFMono-Regular,monospace;font-size:12px;word-break:break-word}}
.badge{{font-size:11px;font-weight:800;padding:4px 7px;border-radius:99px}} .ok{{background:#dfeec5;color:#274b29}} .fail{{background:#f3d3d3;color:#7d2828}}
.cols{{display:grid;grid-template-columns:1fr 1fr;gap:18px}} ul{{padding-left:20px}} footer{{color:var(--muted);font-size:12px;text-align:center;margin-top:30px}}
@media(max-width:800px){{.grid{{grid-template-columns:1fr 1fr}}.cols{{grid-template-columns:1fr}}header{{padding:42px 5vw}}main{{width:94vw}}}} @media(max-width:480px){{.grid{{grid-template-columns:1fr}}}}
</style>
</head>
<body>
<header><div class="brand">Instituto Vital Slim · Engenharia de dados</div><h1>Benchmark governado<br>pgvector × GBrain</h1><div class="subtitle">Piloto controlado para decidir se uma camada vetorial separada agrega valor real à arquitetura do cérebro IVS.</div></header>
<main>
<section class="grid">
<div class="card metric"><strong>{_pct(g['pass_rate'])}</strong><span>GBrain · casos operacionais</span></div>
<div class="card metric"><strong>{_pct(p['recall_at_3'])}</strong><span>pgvector · Recall@3 sintético</span></div>
<div class="card metric"><strong>{_ms(g['latency_p95_ms'])}</strong><span>GBrain · latência p95</span></div>
<div class="card metric"><strong>{_ms(p['latency_p95_ms'])}</strong><span>pgvector · latência p95</span></div>
</section>
<section class="card decision"><span class="code-label">{_esc(decision['decision'])}</span><h2>{decision_title}</h2><p>{_esc(decision['reason'])}</p><p><strong>Diretriz:</strong> otimizar o GBrain existente antes de criar outro banco, outro índice e outro fluxo de sincronização.</p></section>
<section class="warning"><strong>Limite metodológico:</strong> {_esc(payload['comparability_note'])} O microbenchmark sintético prova viabilidade técnica do pgvector; não prova superioridade sobre o corpus real e a busca híbrida do GBrain.</section>
<section class="cols">
<div class="card"><h2>GBrain operacional</h2><ul><li>{g['passed']}/{g['queries']} casos aprovados.</li><li>p50: {_ms(g['latency_p50_ms'])}; p95: {_ms(g['latency_p95_ms'])}.</li><li>Consulta read-only; nenhum arquivo canônico alterado.</li><li>O GBrain já opera com PGLite/PostgreSQL e embeddings vetoriais.</li></ul></div>
<div class="card"><h2>pgvector sintético</h2><ul><li>{p['documents']} documentos e {p['queries']} consultas sem PII.</li><li>Recall@1: {_pct(p['recall_at_1'])}; MRR: {_pct(p['mrr'])}.</li><li>p50: {_ms(p['latency_p50_ms'])}; p95: {_ms(p['latency_p95_ms'])}.</li><li>Extensão { _esc(p['extension_version']) }; indexação em {_ms(p['index_ms'])}.</li><li>HNSW disponível; usado pelo plano padrão: {hnsw_used}. A latência é do microcorpus, não do índice HNSW.</li></ul></div>
</section>
<section class="card"><h2>Gates executados</h2><table><thead><tr><th>Gate</th><th>Observado</th><th>Limite</th><th>Status</th><th>Escopo</th></tr></thead><tbody>{gate_rows}</tbody></table></section>
<section class="card"><h2>Casos do GBrain</h2><table><thead><tr><th>Caso</th><th>Consulta focada</th><th>Status</th><th>Latência</th></tr></thead><tbody>{g_rows}</tbody></table></section>
<section class="card"><h2>Casos sintéticos do pgvector</h2><table><thead><tr><th>Caso</th><th>Esperado</th><th>Top 1</th><th>Latência</th></tr></thead><tbody>{p_rows}</tbody></table></section>
<section class="card"><h2>Recomendação operacional</h2><ol><li><strong>Não instalar</strong> uma camada pgvector paralela neste momento.</li><li>Tratar a latência do GBrain como pauta de otimização interna: profiling, cache e ajuste do pipeline híbrido.</li><li>Reabrir a decisão apenas se surgir consulta real com falha reproduzível e um piloto no mesmo corpus demonstrar ganho.</li><li>Manter o PostgreSQL/pgvector do benchmark efêmero e fora de produção.</li></ol></section>
<footer>Gerado em {_esc(payload['generated_at'])} · Artefato sem PII e sem credenciais · Instituto Vital Slim</footer>
</main></body></html>"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_html(payload), encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
