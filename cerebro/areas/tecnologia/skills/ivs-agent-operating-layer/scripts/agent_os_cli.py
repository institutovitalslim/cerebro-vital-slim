#!/usr/bin/env python3
"""IVS Agent OS Command Center CLI.
Single safe entrypoint for read-only operational routines. Sensitive actions are evaluated only, never executed here.
"""
import argparse, json, subprocess, sys
from pathlib import Path
BASE=Path('/root/.openclaw/workspace/skills/ivs-agent-operating-layer')
DEL=Path('/root/deliverables')

def run(cmd):
    out=subprocess.check_output(cmd,text=True,stderr=subprocess.STDOUT,timeout=120)
    try: return json.loads(out)
    except Exception: return {'ok':True,'raw':out}

def status():
    return {
        'registry': run(['python3',str(BASE/'scripts/workflow_registry.py'),'--json']),
        'cockpit': run(['python3',str(BASE/'scripts/generate_agent_os_cockpit.py'),'--out',str(DEL/'cockpit-unico-ivs-agent-os.html'),'--json-out',str(DEL/'cockpit-unico-ivs-agent-os.json')]),
        'alerts': run(['python3',str(BASE/'scripts/agent_os_critical_alerts.py'),'--json']),
    }

def refresh_all():
    return {
        'cockpit': run(['python3',str(BASE/'scripts/generate_agent_os_cockpit.py'),'--out',str(DEL/'cockpit-unico-ivs-agent-os.html'),'--json-out',str(DEL/'cockpit-unico-ivs-agent-os.json')]),
        'live': run(['python3',str(BASE/'scripts/generate_live_agent_os_cockpit.py')]),
        'trends': run(['python3',str(BASE/'scripts/generate_agent_os_trends.py')]),
        'approval_console': run(['python3',str(BASE/'scripts/generate_approval_console.py')]),
        'runs': run(['python3',str(BASE/'scripts/generate_workflow_runs_cockpit.py'),'--out',str(DEL/'cockpit-workflow-runs-ivs.html'),'--json-out',str(DEL/'cockpit-workflow-runs-ivs.json')]),
    }

def backup(): return run(['python3',str(BASE/'scripts/agent_os_retention_backup.py'),'--json'])
def alerts(): return run(['python3',str(BASE/'scripts/agent_os_critical_alerts.py'),'--json'])
def test():
    p=subprocess.run(['python3',str(BASE/'tests/test_agent_os_regression.py')],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=120)
    return {'ok':p.returncode==0,'exit_code':p.returncode,'log':p.stdout[-4000:]}

def gate(args):
    cmd=['python3',str(BASE/'scripts/action_gate.py'),'--agent',args.agent,'--action',args.action]
    if args.sensitivity: cmd+=['--sensitivity',args.sensitivity]
    if args.approval_id: cmd+=['--approval-id',args.approval_id]
    for e in args.evidence or []: cmd+=['--evidence',e]
    return run(cmd)

def main():
    ap=argparse.ArgumentParser(description='IVS Agent OS Command Center')
    sub=ap.add_subparsers(dest='cmd',required=True)
    sub.add_parser('status'); sub.add_parser('refresh-all'); sub.add_parser('backup'); sub.add_parser('alerts'); sub.add_parser('test')
    g=sub.add_parser('gate'); g.add_argument('--agent',required=True); g.add_argument('--action',required=True); g.add_argument('--sensitivity'); g.add_argument('--approval-id'); g.add_argument('--evidence',action='append',default=[])
    args=ap.parse_args()
    data={'status':status,'refresh-all':refresh_all,'backup':backup,'alerts':alerts,'test':test}.get(args.cmd, lambda: gate(args))()
    print(json.dumps(data,ensure_ascii=False,indent=2))
    if isinstance(data,dict) and data.get('ok') is False: sys.exit(2)
if __name__=='__main__': main()
