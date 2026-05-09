#!/usr/bin/env python3
"""Restore planner for IVS Agent OS backups.
Default: dry-run plan only. --apply requires approval id and still refuses unless explicitly enabled.
"""
import argparse, json, tarfile, time, subprocess, tempfile
from pathlib import Path
BASE=Path('/root/.openclaw/workspace/skills/ivs-agent-operating-layer')
BACK=BASE/'backups'
ACTION_GATE=BASE/'scripts/action_gate.py'
def latest():
    files=sorted(BACK.glob('agent-os-backup-*.tar.gz'), key=lambda p:p.stat().st_mtime, reverse=True)
    return files[0] if files else None
def inspect(path):
    with tarfile.open(path,'r:gz') as tar:
        members=[m for m in tar.getmembers() if m.isfile()]
    unsafe=[m.name for m in members if m.name.startswith('/') or '..' in Path(m.name).parts]
    return {'files':len(members),'unsafe':unsafe,'top_level':sorted(set(m.name.split('/')[0] for m in members))}
def gate(approval_id):
    cmd=['python3',str(ACTION_GATE),'--agent','maria-gerente','--action','restore_agent_os','--sensitivity','tech']
    if approval_id: cmd+=['--approval-id',approval_id]
    try: return json.loads(subprocess.check_output(cmd,text=True,stderr=subprocess.STDOUT,timeout=30))
    except Exception as e: return {'ok':False,'error':str(e)}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--archive'); ap.add_argument('--apply',action='store_true'); ap.add_argument('--approval-id'); ap.add_argument('--json',action='store_true'); args=ap.parse_args()
    p=Path(args.archive) if args.archive else latest()
    if not p:
        report={'ok':False,'error':'no_backup_found'}
    else:
        info=inspect(p)
        report={'ok':not info['unsafe'],'archive':str(p),'inspection':info,'mode':'dry_run_restore_plan','generated_at':int(time.time()),'plan':['verify archive','stop dependent writers manually if needed','restore to staging temp dir','diff staging vs runtime','apply only with explicit approval and maintenance window']}
        if args.apply:
            g=gate(args.approval_id); report['gate']=g; report['mode']='apply_requested_but_not_executed'; report['ok']=False; report['blocked']='restore_apply_not_implemented_by_design'
    Path('/root/deliverables/agent-os-restore-plan-latest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    raise SystemExit(0 if report.get('ok') else 2)
if __name__=='__main__': main()
