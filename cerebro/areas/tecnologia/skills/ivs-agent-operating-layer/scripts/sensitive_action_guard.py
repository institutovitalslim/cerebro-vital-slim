#!/usr/bin/env python3
"""Reusable sensitive action guard for IVS scripts.
Modes:
- enforce: require Action Gate ALLOW_BY_POLICY_BUT_NO_EXECUTION; still does not execute action by itself.
- report: print decision but do not fail unless forbidden.
"""
import argparse, json, subprocess, sys
from pathlib import Path
ACTION_GATE=Path('/root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/action_gate.py')

def check(agent, action, sensitivity=None, approval_id=None, evidence=None, mode='enforce'):
    cmd=['python3',str(ACTION_GATE),'--agent',agent,'--action',action]
    if sensitivity: cmd += ['--sensitivity',sensitivity]
    if approval_id: cmd += ['--approval-id',approval_id]
    for e in evidence or []: cmd += ['--evidence',e]
    d=json.loads(subprocess.check_output(cmd,text=True,stderr=subprocess.STDOUT,timeout=30))
    allowed=d.get('final')=='ALLOW_BY_POLICY_BUT_NO_EXECUTION'
    if mode=='enforce' and not allowed:
        return {'ok':False,'guard':'blocked','decision':d}
    if mode=='report' and d.get('final')=='BLOCK_FORBIDDEN':
        return {'ok':False,'guard':'forbidden','decision':d}
    return {'ok':True,'guard':'allowed' if allowed else 'reported','decision':d}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--agent',required=True); ap.add_argument('--action',required=True); ap.add_argument('--sensitivity'); ap.add_argument('--approval-id'); ap.add_argument('--evidence',action='append',default=[]); ap.add_argument('--mode',choices=['enforce','report'],default='enforce')
    args=ap.parse_args(); res=check(args.agent,args.action,args.sensitivity,args.approval_id,args.evidence,args.mode); print(json.dumps(res,ensure_ascii=False,indent=2)); sys.exit(0 if res.get('ok') else 2)
if __name__=='__main__': main()
