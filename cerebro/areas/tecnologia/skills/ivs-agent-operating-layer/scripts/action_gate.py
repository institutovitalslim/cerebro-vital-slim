#!/usr/bin/env python3
"""IVS Action Gate.
Combines permission gate + approval ledger. It evaluates only; it never executes the sensitive action.
"""
import argparse, json, subprocess, time
from pathlib import Path
BASE=Path('/root/.openclaw/workspace/skills/ivs-agent-operating-layer')
PERM=BASE/'scripts/permission_gate.py'
APP=BASE/'scripts/approval_ledger.py'
def j(cmd):
    out=subprocess.check_output(cmd,text=True,stderr=subprocess.STDOUT,timeout=20)
    return json.loads(out)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--agent',required=True); ap.add_argument('--action',required=True); ap.add_argument('--sensitivity'); ap.add_argument('--approval-id'); ap.add_argument('--evidence', action='append', default=[])
    args=ap.parse_args()
    approval=j(['python3',str(APP),'verify','--agent',args.agent,'--action',args.action]+(['--approval-id',args.approval_id] if args.approval_id else []))
    perm=j(['python3',str(PERM),'--agent',args.agent,'--action',args.action]+(['--sensitivity',args.sensitivity] if args.sensitivity else [])+(['--approved'] if approval.get('ok') else [])+sum([['--evidence',e] for e in args.evidence],[]))
    decision={'ok':bool(perm.get('ok')),'agent':args.agent,'action':args.action,'sensitivity':args.sensitivity,'permission':perm,'approval':approval,'generated_at':int(time.time()),'mode':'action_gate_evaluation_no_execution'}
    if perm.get('decision')=='forbidden': decision['final']='BLOCK_FORBIDDEN'
    elif perm.get('requires_approval') and not approval.get('ok'): decision['final']='BLOCK_APPROVAL_REQUIRED'
    elif perm.get('ok'): decision['final']='ALLOW_BY_POLICY_BUT_NO_EXECUTION'
    else: decision['final']='BLOCK_POLICY'
    print(json.dumps(decision,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
