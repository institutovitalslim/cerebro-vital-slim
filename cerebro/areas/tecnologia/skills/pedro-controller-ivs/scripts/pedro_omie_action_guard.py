#!/usr/bin/env python3
"""Pedro Omie write guard.
Evaluates whether a proposed Omie write has approval. Does not call Omie.
"""
import argparse, json, subprocess, sys
from pathlib import Path
GUARD=Path('/root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/sensitive_action_guard.py')
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--approval-id'); ap.add_argument('--evidence',action='append',default=[]); ap.add_argument('--operation',default='omie_write'); ap.add_argument('--mode',choices=['enforce','report'],default='enforce')
    args=ap.parse_args()
    cmd=['python3',str(GUARD),'--agent','pedro-controller-ivs','--action','omie_write','--sensitivity','financial','--mode',args.mode]
    if args.approval_id: cmd += ['--approval-id', args.approval_id]
    for e in args.evidence or []: cmd += ['--evidence', e]
    out=subprocess.run(cmd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    try: decision=json.loads(out.stdout)
    except Exception: decision={'ok':False,'raw':out.stdout}
    result={'ok':out.returncode==0 and decision.get('ok'), 'operation':args.operation, 'guard':decision, 'mode':'pedro_omie_guard_no_execution'}
    print(json.dumps(result,ensure_ascii=False,indent=2))
    sys.exit(0 if result['ok'] else 2)
if __name__=='__main__': main()
