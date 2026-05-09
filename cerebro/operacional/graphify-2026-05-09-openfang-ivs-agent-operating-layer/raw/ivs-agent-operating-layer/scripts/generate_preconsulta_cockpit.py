#!/usr/bin/env python3
import argparse, html, json, subprocess, sys, time
from pathlib import Path
SKILL_DIR=Path('/root/.openclaw/workspace/skills/ivs-agent-operating-layer')
MONITOR=SKILL_DIR/'scripts/preconsulta_safety_monitor.py'
DEFAULT_OUT=Path('/root/deliverables/cockpit-preconsulta-ivs.html')

def run(): return json.loads(subprocess.check_output([sys.executable,str(MONITOR),'--json'], text=True))
def esc(v): return html.escape('' if v is None else str(v))
def fmt(ts):
 try: return time.strftime('%d/%m/%Y %H:%M UTC', time.gmtime(float(ts)))
 except Exception: return '—'
def rows(items, cols):
 if not items: return f'<tr><td colspan="{len(cols)}" class="muted">Sem itens.</td></tr>'
 return '\n'.join('<tr>'+''.join(f'<td>{esc(i.get(c))}</td>' for c in cols)+'</tr>' for i in items)
def render(r):
 totals=r.get('totals') or {}; findings=r.get('findings') or []
 high=any(str(f.get('severity')).upper()=='HIGH' for f in findings); med=any(str(f.get('severity')).upper()=='MEDIUM' for f in findings)
 status='Atenção alta' if high else ('Atenção' if med else 'Saudável'); cls='danger' if high else ('warn' if med else 'ok')
 fc=''.join(f'<div class="finding {str(f.get("severity")).lower()}"><strong>{esc(f.get("severity"))} · {esc(f.get("code"))}</strong><p>Count: {esc(f.get("count"))}</p></div>' for f in findings) or '<div class="finding info"><strong>INFO · sem achados</strong></div>'
 return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Cockpit Pré-consulta — IVS</title><style>
:root{{--bg:#f7f3ec;--ink:#1f2a24;--muted:#68746c;--card:#fffaf2;--line:#e8dccb;--green:#244234;--gold:#b78a42;--warn:#a86b00;--danger:#9c2f2f}}*{{box-sizing:border-box}}body{{margin:0;background:linear-gradient(135deg,#fffaf2,#f0e4d2);font-family:Inter,system-ui,sans-serif;color:var(--ink)}}.wrap{{max-width:1160px;margin:0 auto;padding:42px 24px}}.hero,.card{{background:rgba(255,250,242,.88);border:1px solid var(--line);border-radius:26px;padding:26px;box-shadow:0 20px 60px rgba(50,40,25,.08)}}.hero{{display:flex;justify-content:space-between;gap:20px}}.k{{color:var(--gold);font-weight:900;letter-spacing:.1em;text-transform:uppercase;font-size:12px}}h1{{margin:8px 0;color:var(--green);font-size:38px}}.sub,.muted{{color:var(--muted)}}.badge{{height:max-content;border-radius:999px;padding:10px 14px;background:#fff;border:1px solid var(--line);font-weight:900}}.badge.ok{{color:var(--green)}}.badge.warn{{color:var(--warn)}}.badge.danger{{color:var(--danger)}}.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:22px 0}}.metric{{font-size:34px;font-weight:950;color:var(--green)}}.label{{font-size:13px;color:var(--muted)}}h2{{color:var(--green);font-size:22px}}table{{width:100%;border-collapse:separate;border-spacing:0;border:1px solid var(--line);border-radius:18px;overflow:hidden}}th,td{{padding:12px;border-bottom:1px solid var(--line);font-size:13px;text-align:left;vertical-align:top}}th{{background:#efe5d6;color:var(--green);text-transform:uppercase;font-size:12px}}tr:last-child td{{border-bottom:0}}.section{{margin-top:20px}}.finding{{border-radius:16px;padding:14px;margin:8px 0;background:#fff;border:1px solid var(--line)}}.finding.high{{background:#fff0f0;border-color:#e6a0a0}}.finding.medium{{background:#fff7e8;border-color:#e2b86d}}.footer{{margin-top:22px;color:var(--muted);font-size:12px}}@media(max-width:900px){{.grid{{grid-template-columns:repeat(2,1fr)}}.hero{{display:block}}}}@media(max-width:560px){{.grid{{grid-template-columns:1fr}}}}
</style></head><body><main class="wrap"><section class="hero"><div><div class="k">Instituto Vital Slim · Segurança operacional</div><h1>Cockpit Pré-consulta</h1><p class="sub">Monitor read-only para submissões, rascunhos, markdowns, fila de fallback e disponibilidade do app. Não contata pacientes.</p></div><div class="badge {cls}">{esc(status)}</div></section><section class="grid">
<div class="card"><div class="metric">{esc((r.get('app_probe') or {}).get('status') or '—')}</div><div class="label">App HTTP</div></div><div class="card"><div class="metric">{esc(totals.get('json_files'))}</div><div class="label">JSONs</div></div><div class="card"><div class="metric">{esc(totals.get('submissions'))}</div><div class="label">Submissões</div></div><div class="card"><div class="metric">{esc(totals.get('drafts'))}</div><div class="label">Rascunhos</div></div><div class="card"><div class="metric">{esc(r.get('stale_drafts_count'))}</div><div class="label">Drafts > 2h</div></div><div class="card"><div class="metric">{esc(r.get('missing_markdown_count'))}</div><div class="label">Submissões sem markdown</div></div><div class="card"><div class="metric">{esc(r.get('incomplete_count'))}</div><div class="label">Registros incompletos</div></div><div class="card"><div class="metric">{esc((r.get('fallback_queue') or {}).get('count'))}</div><div class="label">Fallback Telegram</div></div></section>
<section class="card section"><h2>Achados</h2>{fc}</section>
<section class="card section"><h2>Submissões sem Markdown</h2><table><thead><tr><th>Arquivo</th><th>Nome</th><th>Telefone</th><th>Esperado</th></tr></thead><tbody>{rows(r.get('missing_markdown_sample') or [], ['file','nome','phone','expected'])}</tbody></table></section>
<section class="card section"><h2>Drafts antigos</h2><table><thead><tr><th>Arquivo</th><th>Nome</th><th>Telefone</th><th>Idade h</th></tr></thead><tbody>{rows(r.get('stale_drafts_sample') or [], ['file','nome','phone','age_hours'])}</tbody></table></section>
<section class="card section"><h2>Últimos registros</h2><table><thead><tr><th>Arquivo</th><th>Nome</th><th>Draft</th><th>Data</th></tr></thead><tbody>{rows(r.get('latest_records') or [], ['file','nome','draft','updated_or_submitted'])}</tbody></table></section><div class="footer">Gerado em {fmt(r.get('generated_at'))}. Regra: não pedir novo preenchimento sem validação humana e sem checar dados existentes.</div></main></body></html>'''

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--out',default=str(DEFAULT_OUT)); ap.add_argument('--json-out'); args=ap.parse_args(); r=run(); out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(render(r),encoding='utf-8')
 if args.json_out: Path(args.json_out).write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'ok':True,'html':str(out),'json':args.json_out,'generated_at':r.get('generated_at')},ensure_ascii=False))
if __name__=='__main__': main()
