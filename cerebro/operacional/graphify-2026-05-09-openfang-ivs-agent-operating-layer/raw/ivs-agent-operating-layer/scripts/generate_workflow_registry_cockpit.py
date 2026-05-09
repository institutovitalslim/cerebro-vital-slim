#!/usr/bin/env python3
import argparse, html, json, subprocess, sys, time
from pathlib import Path
SKILL_DIR=Path('/root/.openclaw/workspace/skills/ivs-agent-operating-layer')
REG=SKILL_DIR/'scripts/workflow_registry.py'
DEFAULT_OUT=Path('/root/deliverables/workflow-registry-ivs-agent-operating-layer.html')

def run(): return json.loads(subprocess.check_output([sys.executable,str(REG),'--json'], text=True))
def esc(v): return html.escape('' if v is None else str(v))
def fmt(ts):
 try: return time.strftime('%d/%m/%Y %H:%M UTC', time.gmtime(float(ts)))
 except Exception: return '—'
def rows(items, cols):
 if not items: return f'<tr><td colspan="{len(cols)}" class="muted">Sem itens.</td></tr>'
 return '\n'.join('<tr>'+''.join(f'<td>{esc(i.get(c))}</td>' for c in cols)+'</tr>' for i in items)
def render(r):
 ok=r.get('ok'); cls='ok' if ok else 'danger'; status='Válido' if ok else 'Atenção'
 workflows=r.get('workflows') or []
 cards=''.join(f'''<div class="card"><div class="label">{esc(w.get('id'))}</div><h2>{esc(w.get('name'))}</h2><p>{esc(w.get('scope'))}</p><small>Dono: {esc(w.get('owner'))} · Executor: {esc(w.get('executor'))}</small></div>''' for w in workflows)
 return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Workflow Registry — IVS Agent Operating Layer</title><style>
:root{{--ink:#1f2a24;--muted:#68746c;--card:#fffaf2;--line:#e8dccb;--green:#244234;--gold:#b78a42;--danger:#9c2f2f}}*{{box-sizing:border-box}}body{{margin:0;background:linear-gradient(135deg,#fffaf2,#efe2cf);font-family:Inter,system-ui,sans-serif;color:var(--ink)}}.wrap{{max-width:1220px;margin:0 auto;padding:44px 24px}}.hero,.card{{background:rgba(255,250,242,.9);border:1px solid var(--line);border-radius:28px;padding:26px;box-shadow:0 22px 70px rgba(50,40,25,.08)}}.hero{{display:flex;justify-content:space-between;gap:24px}}.k,.label{{color:var(--gold);font-weight:950;letter-spacing:.1em;text-transform:uppercase;font-size:12px}}h1{{margin:8px 0;color:var(--green);font-size:42px}}h2{{color:var(--green);font-size:22px;margin:8px 0}}.sub,.muted,small{{color:var(--muted)}}.badge{{border-radius:999px;padding:12px 16px;background:#fff;border:1px solid var(--line);font-weight:950;height:max-content}}.badge.ok{{color:var(--green)}}.badge.danger{{color:var(--danger)}}.grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:16px;margin:24px 0}}.metric{{font-size:38px;font-weight:950;color:var(--green)}}table{{width:100%;border-collapse:separate;border-spacing:0;border:1px solid var(--line);border-radius:18px;overflow:hidden}}th,td{{padding:12px;border-bottom:1px solid var(--line);font-size:13px;text-align:left;vertical-align:top}}th{{background:#efe5d6;color:var(--green);text-transform:uppercase;font-size:12px}}tr:last-child td{{border-bottom:0}}.section{{margin-top:20px}}.footer{{margin-top:22px;color:var(--muted);font-size:12px}}@media(max-width:800px){{.grid{{grid-template-columns:1fr}}.hero{{display:block}}}}
</style></head><body><main class="wrap"><section class="hero"><div><div class="k">Instituto Vital Slim · Agent Operating Layer</div><h1>Workflow Registry</h1><p class="sub">Camada formal de workflows operacionais: entrada, preflight, ações permitidas, bloqueios, evidências e severidade. Read-only por padrão.</p></div><div class="badge {cls}">{status}</div></section><section class="grid"><div class="card"><div class="metric">{esc((r.get('totals') or {}).get('workflows'))}</div><div class="label">Workflows registrados</div></div><div class="card"><div class="metric">{esc((r.get('totals') or {}).get('findings'))}</div><div class="label">Findings de validação</div></div></section><section class="grid">{cards}</section><section class="card section"><h2>Índice operacional</h2><table><thead><tr><th>ID</th><th>Nome</th><th>Dono</th><th>Executor</th><th>Entradas</th><th>Preflight</th><th>Bloqueios</th></tr></thead><tbody>{rows(workflows,['id','name','owner','executor','entry_count','preflight_count','blocked_count'])}</tbody></table></section><section class="card section"><h2>Findings de validação</h2><table><thead><tr><th>Workflow</th><th>Severidade</th><th>Código</th><th>Campo</th></tr></thead><tbody>{rows(r.get('findings') or [], ['workflow','severity','code','field'])}</tbody></table></section><div class="footer">Gerado em {fmt(r.get('generated_at'))}. Registro interno; não executa ações de produção.</div></main></body></html>'''
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--out',default=str(DEFAULT_OUT)); ap.add_argument('--json-out'); args=ap.parse_args(); r=run(); out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(render(r),encoding='utf-8')
 if args.json_out: Path(args.json_out).write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'ok':True,'html':str(out),'json':args.json_out,'generated_at':r.get('generated_at'),'valid':r.get('ok')},ensure_ascii=False))
if __name__=='__main__': main()
