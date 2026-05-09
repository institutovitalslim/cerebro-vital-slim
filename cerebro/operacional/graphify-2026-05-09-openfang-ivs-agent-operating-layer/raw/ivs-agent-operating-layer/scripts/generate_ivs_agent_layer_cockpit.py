#!/usr/bin/env python3
import argparse, html, json, subprocess, sys, time
from pathlib import Path
SKILL_DIR=Path('/root/.openclaw/workspace/skills/ivs-agent-operating-layer')
MONITOR=SKILL_DIR/'scripts/ivs_agent_layer_monitor.py'
DEFAULT_OUT=Path('/root/deliverables/cockpit-geral-ivs-agent-operating-layer.html')

def run(): return json.loads(subprocess.check_output([sys.executable,str(MONITOR),'--json'], text=True))
def esc(v): return html.escape('' if v is None else str(v))
def fmt(ts):
 try: return time.strftime('%d/%m/%Y %H:%M UTC', time.gmtime(float(ts)))
 except Exception: return '—'
def rows(items, cols):
 if not items: return f'<tr><td colspan="{len(cols)}" class="muted">Sem itens.</td></tr>'
 return '\n'.join('<tr>'+''.join(f'<td>{esc(i.get(c))}</td>' for c in cols)+'</tr>' for i in items)
def state_rows(states):
 items=[]
 for k,v in (states or {}).items():
  items.append({'area':k,'exists':v.get('exists'),'updated_at':fmt(v.get('updated_at')) if v.get('updated_at') else '—','error':v.get('error') or ''})
 return rows(items,['area','exists','updated_at','error'])
def render(r):
 sev=r.get('overall_severity') or 'OK'; cls='danger' if sev=='ALTA' else ('warn' if sev=='MÉDIA' else ('low' if sev=='BAIXA' else 'ok'))
 areas=r.get('areas') or []; findings=r.get('findings') or []
 cards=''.join(f'''<div class="card area {esc(str(a.get('severity')).lower())}"><div class="label">{esc(a.get('area'))}</div><div class="metric">{esc(a.get('severity'))}</div><p>{esc(a.get('headline'))}</p><small>{esc(a.get('findings_count'))} achado(s)</small></div>''' for a in areas)
 finding_html=''.join(f'<div class="finding {esc(str(f.get("severity")).lower())}"><strong>{esc(f.get("area"))} · {esc(f.get("severity"))} · {esc(f.get("code"))}</strong><p>Count: {esc(f.get("count") or "—")}</p></div>' for f in findings) or '<div class="finding info"><strong>Sem achados ativos</strong></div>'
 return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Cockpit Geral — IVS Agent Operating Layer</title><style>
:root{{--bg:#f7f3ec;--ink:#1f2a24;--muted:#68746c;--card:#fffaf2;--line:#e8dccb;--green:#244234;--gold:#b78a42;--warn:#a86b00;--danger:#9c2f2f;--low:#6b7280}}*{{box-sizing:border-box}}body{{margin:0;background:linear-gradient(135deg,#fffaf2,#efe2cf 65%,#e8dccb);font-family:Inter,system-ui,sans-serif;color:var(--ink)}}.wrap{{max-width:1220px;margin:0 auto;padding:44px 24px}}.hero,.card{{background:rgba(255,250,242,.9);border:1px solid var(--line);border-radius:30px;padding:28px;box-shadow:0 22px 70px rgba(50,40,25,.09)}}.hero{{display:flex;justify-content:space-between;gap:24px;align-items:flex-start}}.k{{color:var(--gold);font-weight:950;letter-spacing:.12em;text-transform:uppercase;font-size:12px}}h1{{margin:8px 0;color:var(--green);font-size:42px;line-height:1.05}}h2{{color:var(--green);font-size:22px}}.sub,.muted{{color:var(--muted)}}.badge{{border-radius:999px;padding:12px 16px;background:#fff;border:1px solid var(--line);font-weight:950;white-space:nowrap}}.badge.ok{{color:var(--green)}}.badge.warn{{color:var(--warn)}}.badge.danger{{color:var(--danger)}}.badge.low{{color:var(--low)}}.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:24px 0}}.metric{{font-size:34px;font-weight:950;color:var(--green)}}.label{{font-size:13px;color:var(--gold);font-weight:900;text-transform:uppercase;letter-spacing:.08em}}.area.high,.area.alta{{border-color:#e6a0a0}}.area.medium,.area.média{{border-color:#e2b86d}}.area.ok{{border-color:#b9d0c3}}table{{width:100%;border-collapse:separate;border-spacing:0;border:1px solid var(--line);border-radius:18px;overflow:hidden}}th,td{{padding:12px;border-bottom:1px solid var(--line);font-size:13px;text-align:left;vertical-align:top}}th{{background:#efe5d6;color:var(--green);text-transform:uppercase;font-size:12px}}tr:last-child td{{border-bottom:0}}.section{{margin-top:20px}}.finding{{border-radius:16px;padding:14px;margin:8px 0;background:#fff;border:1px solid var(--line)}}.finding.high{{background:#fff0f0;border-color:#e6a0a0}}.finding.medium{{background:#fff7e8;border-color:#e2b86d}}.finding.low{{background:#f7f7f7}}.footer{{margin-top:22px;color:var(--muted);font-size:12px}}@media(max-width:900px){{.grid{{grid-template-columns:1fr}}.hero{{display:block}}}}
</style></head><body><main class="wrap"><section class="hero"><div><div class="k">Instituto Vital Slim · Agent Operating Layer</div><h1>Cockpit Geral da Operação Assistida</h1><p class="sub">Visão executiva consolidada de Clara/Z-API, Pré-consulta e Marketing OS/João. Monitor read-only: não contata pacientes, não publica externamente e não altera produção.</p></div><div class="badge {cls}">Severidade {esc(sev)}</div></section><section class="grid">{cards}</section>
<section class="card section"><h2>Achados consolidados</h2>{finding_html}</section>
<section class="card section"><h2>Resumo das áreas</h2><table><thead><tr><th>Área</th><th>Severidade</th><th>Status</th><th>Resumo</th><th>Achados</th></tr></thead><tbody>{rows(areas,['area','severity','status','headline','findings_count'])}</tbody></table></section>
<section class="card section"><h2>Baselines das auditorias</h2><table><thead><tr><th>Área</th><th>Existe</th><th>Atualizado em</th><th>Erro</th></tr></thead><tbody>{state_rows(r.get('states'))}</tbody></table></section>
<section class="card section"><h2>Próximas ações</h2><ul>{''.join('<li>'+esc(x)+'</li>' for x in (r.get('next_actions') or []))}</ul></section>
<div class="footer">Gerado em {fmt(r.get('generated_at'))}. Este cockpit é operacional e interno.</div></main></body></html>'''
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--out',default=str(DEFAULT_OUT)); ap.add_argument('--json-out'); args=ap.parse_args(); r=run(); out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(render(r),encoding='utf-8')
 if args.json_out: Path(args.json_out).write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'ok':True,'html':str(out),'json':args.json_out,'generated_at':r.get('generated_at'),'overall':r.get('overall_severity')},ensure_ascii=False))
if __name__=='__main__': main()
