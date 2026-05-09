#!/usr/bin/env python3
"""Read-only extended watch summary for Clara Phase 2."""
import argparse,json,glob,time
from pathlib import Path
DEL=Path('/root/deliverables')

def load(p):
    try: return json.load(open(p))
    except Exception: return None

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--json',action='store_true'); args=ap.parse_args()
    files=sorted(glob.glob('/root/deliverables/clara-phase2-watch-*.json'))[-50:]
    docs=[load(f) for f in files]; docs=[d for d in docs if d]
    findings=[]
    for d in docs:
        for f in d.get('findings',[]):
            findings.append(f)
    high=sum(1 for f in findings if f.get('severity')=='HIGH')
    medium=sum(1 for f in findings if f.get('severity')=='MEDIUM')
    latest=load('/root/deliverables/clara-phase2-watch-latest.json') or {}
    report={'ok':high==0,'generated_at':int(time.time()),'mode':'read_only_clara_phase2_watch_summary','totals':{'snapshots':len(docs),'findings':len(findings),'high':high,'medium':medium},'latest_ok':latest.get('ok'),'latest_counts':latest.get('log_counts',{}),'recommendation':'continue_watch' if high==0 else 'escalate_to_tiaro_no_auto_pause','actions_taken':[]}
    (DEL/'clara-phase2-watch-summary-latest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2)); raise SystemExit(0 if report['ok'] else 2)
if __name__=='__main__': main()
