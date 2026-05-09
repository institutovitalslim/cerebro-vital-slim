#!/usr/bin/env python3
import argparse, html, json, subprocess, sys, time
from pathlib import Path
SKILL_DIR=Path('/root/.openclaw/workspace/skills/ivs-agent-operating-layer')
MONITOR=SKILL_DIR/'scripts/marketing_os_monitor.py'
DEFAULT_OUT=Path('/root/deliverables/cockpit-marketing-os-joao-ivs.html')

def run(): return json.loads(subprocess.check_output([sys.executable,str(MONITOR),'--json'], text=True))
def esc(v): return html.escape('' if v is None else str(v))
def fmt(ts):
 try: return time.strftime('%d/%m/%Y %H:%M UTC', time.gmtime(float(ts)))
 except Exception: return '—'
def rows(items, cols):
 if not items: return f'<tr><td colspan="{len(cols)}" class="muted">Sem itens.</td></tr>'
 return '\n'.join('<tr>'+''.join(f'<td>{esc(i.get(c))}</td>' for c in cols)+'</tr>' for i in items)
def render(r):
 t=r.get('totals') or {}; f=r.get('findings') or []
 high=any(str(x.get('severity')).upper()=='HIGH' for x in f); med=any(str(x.get('severity')).upper()=='MEDIUM' for x in f)
 status='Atenção alta' if high else ('Atenção operacional' if med else 'Saudável'); cls='danger' if high else ('warn' if med else 'ok')
 findings=''.join(f'<div class="finding {esc(str(x.get("severity")).lower())}"><strong>{esc(x.get("severity"))} · {esc(x.get("code"))}</strong><p>{esc(x.get("count") or x.get("detail") or "")}</p></div>' for x in f) or '<div class="finding info"><strong>INFO · sem achados críticos</strong></div>'
 rule_checks=r.get('rule_health',{}).get('checks',{})
 rule_html=''.join(f'<li><span class="dot {"on" if v else "off"}"></span>{esc(k)}</li>' for k,v in rule_checks.items())
 return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Cockpit Marketing OS — João IVS</title><style>
:root{{--bg:#f7f3ec;--ink:#1f2a24;--muted:#68746c;--card:#fffaf2;--line:#e8dccb;--green:#244234;--gold:#b78a42;--warn:#a86b00;--danger:#9c2f2f}}*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(circle at top left,#fffaf2,#efe2cf 70%);font-family:Inter,system-ui,sans-serif;color:var(--ink)}}.wrap{{max-width:1180px;margin:0 auto;padding:42px 24px}}.hero,.card{{background:rgba(255,250,242,.9);border:1px solid var(--line);border-radius:28px;padding:26px;box-shadow:0 20px 60px rgba(50,40,25,.08)}}.hero{{display:flex;justify-content:space-between;gap:20px}}.k{{color:var(--gold);font-weight:950;letter-spacing:.1em;text-transform:uppercase;font-size:12px}}h1{{margin:8px 0;color:var(--green);font-size:38px}}h2{{color:var(--green);font-size:22px}}.sub,.muted{{color:var(--muted)}}.badge{{height:max-content;border-radius:999px;padding:10px 14px;background:#fff;border:1px solid var(--line);font-weight:900}}.badge.ok{{color:var(--green)}}.badge.warn{{color:var(--warn)}}.badge.danger{{color:var(--danger)}}.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:22px 0}}.metric{{font-size:34px;font-weight:950;color:var(--green)}}.label{{font-size:13px;color:var(--muted)}}table{{width:100%;border-collapse:separate;border-spacing:0;border:1px solid var(--line);border-radius:18px;overflow:hidden}}th,td{{padding:12px;border-bottom:1px solid var(--line);font-size:13px;text-align:left;vertical-align:top}}th{{background:#efe5d6;color:var(--green);text-transform:uppercase;font-size:12px}}tr:last-child td{{border-bottom:0}}.section{{margin-top:20px}}.finding{{border-radius:16px;padding:14px;margin:8px 0;background:#fff;border:1px solid var(--line)}}.finding.high{{background:#fff0f0;border-color:#e6a0a0}}.finding.medium{{background:#fff7e8;border-color:#e2b86d}}ul.rules{{columns:2;list-style:none;padding:0;margin:0}}.dot{{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:8px}}.dot.on{{background:var(--green)}}.dot.off{{background:var(--danger)}}.footer{{margin-top:22px;color:var(--muted);font-size:12px}}@media(max-width:900px){{.grid{{grid-template-columns:repeat(2,1fr)}}.hero{{display:block}}}}@media(max-width:560px){{.grid{{grid-template-columns:1fr}}ul.rules{{columns:1}}}}
</style></head><body><main class="wrap"><section class="hero"><div><div class="k">Instituto Vital Slim · Marketing Operating System</div><h1>Cockpit João</h1><p class="sub">Monitor read-only da operação de marketing: backlog, entregáveis HTML, outbound Telegram, regras canônicas e saúde das sessões do João.</p></div><div class="badge {cls}">{esc(status)}</div></section><section class="grid">
<div class="card"><div class="metric">{esc(t.get('marketing_backlog_items'))}</div><div class="label">Backlog marketing</div></div><div class="card"><div class="metric">{esc(t.get('recent_html_deliverables'))}</div><div class="label">HTMLs recentes</div></div><div class="card"><div class="metric">{esc(len(r.get('html_deliverables_not_in_outbound') or []))}</div><div class="label">HTMLs fora do outbound</div></div><div class="card"><div class="metric">{esc(t.get('recent_marketing_docs'))}</div><div class="label">Docs marketing 7d</div></div><div class="card"><div class="metric">{esc(t.get('recent_outbound_files'))}</div><div class="label">Arquivos enviados</div></div><div class="card"><div class="metric">{esc(t.get('joao_session_files'))}</div><div class="label">Sessões João</div></div><div class="card"><div class="metric">{esc(len(r.get('session_risks') or []))}</div><div class="label">Marcadores de risco</div></div><div class="card"><div class="metric">{esc(len((r.get('rule_health') or {}).get('missing') or []))}</div><div class="label">Regras ausentes</div></div></section>
<section class="card section"><h2>Achados</h2>{findings}</section>
<section class="card section"><h2>Regras canônicas monitoradas</h2><ul class="rules">{rule_html}</ul></section>
<section class="card section"><h2>Backlog marketing ativo</h2><table><thead><tr><th>Código</th><th>Título</th><th>Status</th><th>Próximo passo</th></tr></thead><tbody>{rows(r.get('marketing_backlog') or [], ['code','title','status','next_step'])}</tbody></table></section>
<section class="card section"><h2>HTMLs recentes não presentes no outbound</h2><table><thead><tr><th>Arquivo</th><th>Tamanho</th><th>Idade h</th></tr></thead><tbody>{rows(r.get('html_deliverables_not_in_outbound') or [], ['name','size','age_hours'])}</tbody></table></section>
<section class="card section"><h2>Riscos em sessões recentes do João</h2><table><thead><tr><th>Código</th><th>Arquivo</th><th>Severidade</th></tr></thead><tbody>{rows(r.get('session_risks') or [], ['code','file','severity'])}</tbody></table></section>
<section class="card section"><h2>Entregáveis HTML recentes</h2><table><thead><tr><th>Arquivo</th><th>Tamanho</th><th>Idade h</th></tr></thead><tbody>{rows(r.get('recent_html_deliverables') or [], ['name','size','age_hours'])}</tbody></table></section>
<div class="footer">Gerado em {fmt(r.get('generated_at'))}. Rotina não publica em canais externos e não altera configuração do João.</div></main></body></html>'''
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--out',default=str(DEFAULT_OUT)); ap.add_argument('--json-out'); args=ap.parse_args(); r=run(); out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(render(r),encoding='utf-8')
 if args.json_out: Path(args.json_out).write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'ok':True,'html':str(out),'json':args.json_out,'generated_at':r.get('generated_at')},ensure_ascii=False))
if __name__=='__main__': main()
