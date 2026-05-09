#!/usr/bin/env python3
import argparse, json, time, collections, html
from pathlib import Path
BASE=Path('/root/.openclaw/workspace/skills/ivs-agent-operating-layer')
RUNS=BASE/'runs'; EVENTS=BASE/'events'; APPROVALS=BASE/'approvals/approval-ledger.jsonl'

def load_json(p):
    try: return json.loads(p.read_text(encoding='utf-8'))
    except Exception: return None

def load_jsonl(p):
    out=[]
    if not p.exists(): return out
    for line in p.read_text(encoding='utf-8',errors='ignore').splitlines():
        try: out.append(json.loads(line))
        except Exception: pass
    return out

def bucket_day(ts): return time.strftime('%Y-%m-%d', time.localtime(int(ts or time.time())))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--out',default='/root/deliverables/agent-os-trends.html'); ap.add_argument('--json-out',default='/root/deliverables/agent-os-trends.json'); args=ap.parse_args()
    runs=[]
    for p in sorted(RUNS.glob('*.json')):
        d=load_json(p)
        if d: runs.append(d)
    events=[]
    for p in sorted(EVENTS.glob('*.json*')):
        if p.suffix=='.jsonl': events += load_jsonl(p)
        else:
            d=load_json(p)
            if isinstance(d,list): events += d
            elif d: events.append(d)
    approvals=load_jsonl(APPROVALS)
    by_state=collections.Counter(r.get('state','unknown') for r in runs)
    by_workflow=collections.Counter(r.get('workflow_id') or r.get('workflow') or 'unknown' for r in runs)
    by_day=collections.Counter(bucket_day(r.get('created_at') or r.get('started_at') or r.get('generated_at')) for r in runs)
    approvals_by_action=collections.Counter(a.get('action','unknown') for a in approvals)
    expired=sum(1 for a in approvals if int(a.get('expires_at') or 0) < time.time())
    report={'ok':True,'generated_at':int(time.time()),'totals':{'runs':len(runs),'events':len(events),'approvals':len(approvals),'expired_approvals':expired},'runs_by_state':dict(by_state),'runs_by_workflow':dict(by_workflow),'runs_by_day':dict(by_day),'approvals_by_action':dict(approvals_by_action),'mode':'read_only_trends'}
    Path(args.json_out).parent.mkdir(parents=True,exist_ok=True); Path(args.json_out).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    rows=''.join(f'<tr><td>{html.escape(k)}</td><td>{v}</td></tr>' for k,v in sorted(by_workflow.items()))
    states=''.join(f'<tr><td>{html.escape(k)}</td><td>{v}</td></tr>' for k,v in sorted(by_state.items()))
    app=''.join(f'<tr><td>{html.escape(k)}</td><td>{v}</td></tr>' for k,v in sorted(approvals_by_action.items())) or '<tr><td colspan="2">Sem aprovações registradas</td></tr>'
    doc=f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>IVS Agent OS — Trends</title><style>body{{font-family:Inter,Arial,sans-serif;margin:0;background:#0b1020;color:#eef;padding:24px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px}}.card{{background:#151d36;border:1px solid #2b365d;border-radius:16px;padding:18px}}table{{width:100%;border-collapse:collapse}}td,th{{border-bottom:1px solid #2b365d;padding:8px;text-align:left}}.num{{font-size:34px;font-weight:800}}</style></head><body><h1>IVS Agent OS — Tendências</h1><p>Read-only · Gerado em {report['generated_at']}</p><div class="grid"><div class="card"><div class="num">{len(runs)}</div><p>runs</p></div><div class="card"><div class="num">{len(events)}</div><p>eventos</p></div><div class="card"><div class="num">{len(approvals)}</div><p>aprovações</p></div><div class="card"><div class="num">{expired}</div><p>aprovações expiradas</p></div></div><div class="grid"><div class="card"><h2>Runs por estado</h2><table>{states}</table></div><div class="card"><h2>Runs por workflow</h2><table>{rows}</table></div><div class="card"><h2>Aprovações por ação</h2><table>{app}</table></div></div></body></html>'''
    Path(args.out).write_text(doc,encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
