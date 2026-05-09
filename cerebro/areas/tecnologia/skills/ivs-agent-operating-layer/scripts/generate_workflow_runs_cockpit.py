#!/usr/bin/env python3
import argparse, json, html, time
from pathlib import Path
BASE=Path('/root/.openclaw/workspace/skills/ivs-agent-operating-layer')
RUNS=BASE/'runs'; EVENTS=BASE/'events'
def load(p):
    try: return json.loads(p.read_text(encoding='utf-8'))
    except Exception: return {}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--out', default='/root/deliverables/cockpit-workflow-runs-ivs.html'); ap.add_argument('--json-out', default='/root/deliverables/cockpit-workflow-runs-ivs.json'); args=ap.parse_args()
    runs=sorted([load(p) for p in RUNS.glob('*.json')], key=lambda r:r.get('updated_at',0), reverse=True) if RUNS.exists() else []
    totals={}
    for r in runs: totals[r.get('state','unknown')]=totals.get(r.get('state','unknown'),0)+1
    report={'generated_at':int(time.time()),'totals':{'runs':len(runs),**totals},'runs':runs[:100]}
    Path(args.json_out).parent.mkdir(parents=True, exist_ok=True); Path(args.json_out).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    rows=''.join(f"<tr><td>{html.escape(r.get('run_id',''))}</td><td>{html.escape(r.get('workflow_id',''))}</td><td>{html.escape(r.get('state',''))}</td><td>{html.escape(r.get('subject',''))}</td><td>{r.get('updated_at','')}</td></tr>" for r in runs[:100])
    doc=f"""<!doctype html><html><head><meta charset='utf-8'><title>IVS Workflow Runs</title><style>body{{font-family:Inter,Arial;margin:32px;background:#0f172a;color:#e5e7eb}}.card{{background:#111827;border:1px solid #334155;border-radius:16px;padding:20px;margin:12px 0}}table{{width:100%;border-collapse:collapse}}td,th{{border-bottom:1px solid #334155;padding:10px;text-align:left}}.ok{{color:#86efac}}</style></head><body><h1>IVS Workflow Runner Cockpit</h1><div class='card'><b>Runs:</b> {len(runs)} · <span class='ok'>Read-only cockpit</span></div><div class='card'><table><thead><tr><th>Run</th><th>Workflow</th><th>Estado</th><th>Assunto</th><th>Atualizado</th></tr></thead><tbody>{rows}</tbody></table></div></body></html>"""
    Path(args.out).write_text(doc, encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))
if __name__=='__main__': main()
