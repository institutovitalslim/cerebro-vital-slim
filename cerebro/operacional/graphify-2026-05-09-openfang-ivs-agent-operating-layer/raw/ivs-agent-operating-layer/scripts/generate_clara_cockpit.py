#!/usr/bin/env python3
"""Generate Clara/Z-API operational cockpit HTML from read-only monitor data."""
import argparse
import html
import json
import subprocess
import sys
import time
from pathlib import Path

SKILL_DIR = Path('/root/.openclaw/workspace/skills/ivs-agent-operating-layer')
MONITOR = SKILL_DIR / 'scripts' / 'clara_safety_monitor.py'
DEFAULT_OUT = Path('/root/deliverables/cockpit-clara-zapi-ivs.html')


def run_monitor():
    out = subprocess.check_output([sys.executable, str(MONITOR), '--json'], text=True)
    return json.loads(out)


def esc(v):
    return html.escape('' if v is None else str(v))


def fmt_ts(ts):
    if not ts:
        return '—'
    try:
        return time.strftime('%d/%m/%Y %H:%M UTC', time.gmtime(float(ts)))
    except Exception:
        return esc(ts)


def severity_class(sev):
    return {'HIGH': 'danger', 'MEDIUM': 'warn', 'LOW': 'info', 'INFO': 'info'}.get(str(sev).upper(), 'info')


def rows(items, cols):
    if not items:
        return f'<tr><td colspan="{len(cols)}" class="muted">Sem itens para exibir.</td></tr>'
    body = []
    for item in items:
        body.append('<tr>' + ''.join(f'<td>{esc(item.get(c))}</td>' for c in cols) + '</tr>')
    return '\n'.join(body)


def render(report):
    health_ok = (report.get('bridge_health') or {}).get('ok') is True
    admin_body = (report.get('bridge_admin_status') or {}).get('body') or {}
    paused = admin_body.get('paused') is True
    findings = report.get('findings') or []
    collisions = report.get('collisions') or {}
    exclusions = report.get('exclusions') or {}
    manual = report.get('manual_overrides') or {}
    lead_total = (report.get('leads') or {}).get('active_total')
    generated = fmt_ts(report.get('generated_at'))
    status_label = 'Saudável' if health_ok and not paused else ('Pausada' if paused else 'Atenção')
    status_class = 'ok' if health_ok and not paused else 'warn'

    finding_cards = ''.join(
        f'<div class="finding {severity_class(f.get("severity"))}"><strong>{esc(f.get("severity"))} · {esc(f.get("code"))}</strong><pre>{esc(json.dumps(f.get("detail"), ensure_ascii=False, indent=2))}</pre></div>'
        for f in findings
    ) or '<div class="finding info"><strong>INFO · sem achados críticos</strong><p>Nenhum alerta crítico no momento.</p></div>'

    html_doc = f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Cockpit Clara/Z-API — IVS</title>
<style>
:root {{
  --bg:#f7f3ec; --ink:#1f2a24; --muted:#68746c; --card:#fffaf2; --line:#e8dccb;
  --green:#244234; --gold:#b78a42; --warn:#a86b00; --danger:#9c2f2f; --soft:#efe5d6;
}}
*{{box-sizing:border-box}} body{{margin:0;background:radial-gradient(circle at 20% 0%,#fffaf2 0,#f7f3ec 42%,#efe5d6 100%);font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,sans-serif;color:var(--ink)}}
.wrap{{max-width:1180px;margin:0 auto;padding:42px 24px 64px}}
.hero{{display:flex;justify-content:space-between;gap:24px;align-items:flex-start;border:1px solid var(--line);background:rgba(255,250,242,.82);backdrop-filter:blur(10px);border-radius:28px;padding:30px;box-shadow:0 22px 70px rgba(44,35,22,.10)}}
.kicker{{color:var(--gold);font-weight:800;letter-spacing:.11em;text-transform:uppercase;font-size:12px}} h1{{font-size:38px;line-height:1.02;margin:10px 0 12px;color:var(--green)}} .sub{{color:var(--muted);font-size:16px;max-width:720px}}
.badge{{border-radius:999px;padding:10px 14px;font-weight:800;border:1px solid var(--line);background:#fff}} .badge.ok{{color:var(--green)}} .badge.warn{{color:var(--warn)}}
.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:22px 0}} .card{{background:var(--card);border:1px solid var(--line);border-radius:22px;padding:20px;box-shadow:0 14px 42px rgba(44,35,22,.06)}}
.metric{{font-size:34px;font-weight:900;color:var(--green);letter-spacing:-.03em}} .label{{color:var(--muted);font-size:13px;margin-top:4px}} .section{{margin-top:22px}} h2{{font-size:22px;color:var(--green);margin:0 0 12px}}
table{{width:100%;border-collapse:separate;border-spacing:0;overflow:hidden;border-radius:18px;border:1px solid var(--line);background:#fffaf2}} th,td{{padding:12px 14px;text-align:left;border-bottom:1px solid var(--line);font-size:13px;vertical-align:top}} th{{background:#efe5d6;color:var(--green);font-size:12px;text-transform:uppercase;letter-spacing:.05em}} tr:last-child td{{border-bottom:none}} .muted{{color:var(--muted)}}
.finding{{border-radius:18px;padding:16px;margin:10px 0;border:1px solid var(--line);background:#fff}} .finding pre{{white-space:pre-wrap;font-size:12px;color:var(--muted);margin:8px 0 0}} .finding.warn{{border-color:#e2b86d;background:#fff7e8}} .finding.danger{{border-color:#e6a0a0;background:#fff0f0}} .finding.info{{border-color:#cdded4;background:#f3faf5}}
.footer{{margin-top:28px;color:var(--muted);font-size:12px;line-height:1.5}}
@media(max-width:900px){{.hero{{display:block}}.grid{{grid-template-columns:repeat(2,1fr)}}}} @media(max-width:560px){{.grid{{grid-template-columns:1fr}} h1{{font-size:30px}}}}
</style>
</head>
<body><main class="wrap">
<section class="hero"><div><div class="kicker">Instituto Vital Slim · Operação</div><h1>Cockpit Clara/Z-API</h1><p class="sub">Painel read-only para segurança operacional da Clara: bloqueios de pacientes, colisões com leads, saúde do bridge, pausas e overrides. Não envia mensagem e não altera produção.</p></div><div class="badge {status_class}">{esc(status_label)}</div></section>
<section class="grid">
  <div class="card"><div class="metric">{'OK' if health_ok else 'Falha'}</div><div class="label">Bridge Z-API</div></div>
  <div class="card"><div class="metric">{'Sim' if paused else 'Não'}</div><div class="label">Pausa global Clara</div></div>
  <div class="card"><div class="metric">{esc(lead_total)}</div><div class="label">Leads ativos rastreados</div></div>
  <div class="card"><div class="metric">{esc(collisions.get('patient_like_active_lead_collision_count'))}</div><div class="label">Colisões lead + paciente-like</div></div>
  <div class="card"><div class="metric">{esc(exclusions.get('total'))}</div><div class="label">Exclusões totais</div></div>
  <div class="card"><div class="metric">{esc(exclusions.get('patient_do_not_reply_count'))}</div><div class="label">patient_do_not_reply</div></div>
  <div class="card"><div class="metric">{esc(exclusions.get('patient_bridge_known_count'))}</div><div class="label">patient_bridge_known</div></div>
  <div class="card"><div class="metric">{esc(manual.get('active_count'))}</div><div class="label">Overrides manuais ativos</div></div>
</section>
<section class="section card"><h2>Achados</h2>{finding_cards}</section>
<section class="section card"><h2>Colisões para revisão</h2><table><thead><tr><th>Telefone</th><th>Nome</th><th>Lead source</th><th>Bloqueio</th><th>Origem bloqueio</th></tr></thead><tbody>{rows(collisions.get('patient_like_active_lead_collision_sample') or [], ['phone','name','lead_source','exclusion_reason','exclusion_source'])}</tbody></table></section>
<section class="section card"><h2>Patient do not reply — amostra</h2><table><thead><tr><th>Telefone</th><th>Nome</th><th>Motivo</th><th>Origem</th></tr></thead><tbody>{rows(exclusions.get('patient_do_not_reply_sample') or [], ['phone','name','reason','source'])}</tbody></table></section>
<section class="section card"><h2>Overrides manuais ativos</h2><table><thead><tr><th>Telefone</th><th>Nota</th><th>Dono</th><th>Definido em</th><th>Até</th></tr></thead><tbody>{rows(manual.get('active_sample') or [], ['phone','note','owner','set_at','until'])}</tbody></table></section>
<div class="footer">Gerado em {generated}. Fonte: Clara Safety Monitor. Regra operacional: paciente e do_not_reply permanecem bloqueados por padrão; exceções só com autorização explícita.</div>
</main></body></html>'''
    return html_doc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=str(DEFAULT_OUT))
    ap.add_argument('--json-out')
    args = ap.parse_args()
    report = run_monitor()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(report), encoding='utf-8')
    if args.json_out:
        Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json_out).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'ok': True, 'html': str(out), 'json': args.json_out, 'generated_at': report.get('generated_at')}, ensure_ascii=False))

if __name__ == '__main__':
    main()
