#!/usr/bin/env python3
"""Offsite backup readiness/export adapter for IVS Agent OS.
Default is dry-run/readiness. Real export requires --apply, configured destination, and approval id.
Supported destination modes:
- local_mirror: copy to explicitly allowed local path (still requires --apply + approval)
- rclone: dry-run command plan only unless --apply + approval (rclone must be configured)
"""
import argparse, json, os, shutil, subprocess, time
from pathlib import Path
BASE=Path('/root/.openclaw/workspace/skills/ivs-agent-operating-layer')
DEL=Path('/root/deliverables')
ACTION_GATE=BASE/'scripts/action_gate.py'
BACKUP=BASE/'scripts/agent_os_retention_backup.py'
VERIFY=BASE/'scripts/agent_os_backup_verify.py'

def latest_backup():
    files=sorted((BASE/'backups').glob('agent-os-backup-*.tar.gz'), key=lambda p:p.stat().st_mtime, reverse=True)
    return files[0] if files else None

def gate(approval_id):
    cmd=['python3',str(ACTION_GATE),'--agent','maria-gerente','--action','offsite_backup_export','--sensitivity','tech']
    if approval_id: cmd += ['--approval-id', approval_id]
    try: return json.loads(subprocess.check_output(cmd,text=True,stderr=subprocess.STDOUT,timeout=30))
    except Exception as e: return {'ok':False,'error':str(e)}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--destination',default=os.getenv('IVS_AGENT_OS_OFFSITE_DEST','')); ap.add_argument('--mode',choices=['readiness','local_mirror','rclone'],default=os.getenv('IVS_AGENT_OS_OFFSITE_MODE','readiness')); ap.add_argument('--apply',action='store_true'); ap.add_argument('--approval-id'); ap.add_argument('--json',action='store_true'); args=ap.parse_args()
    # Ensure backup exists and is verified
    subprocess.run(['python3',str(BACKUP),'--json'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=120)
    backup=latest_backup()
    verify=None
    if backup:
        p=subprocess.run(['python3',str(VERIFY),'--archive',str(backup),'--json'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=120)
        try: verify=json.loads(p.stdout)
        except Exception: verify={'ok':False,'raw':p.stdout[-500:]}
    configured=bool(args.destination)
    report={'ok':True,'generated_at':int(time.time()),'mode':'offsite_backup_readiness_no_export','backup':str(backup) if backup else None,'backup_verified':bool(verify and verify.get('ok')),'destination_configured':configured,'destination_mode':args.mode,'destination_preview':(args.destination[:8]+'***') if args.destination else None,'apply_requested':args.apply,'exported':False}
    if not backup or not report['backup_verified']:
        report['ok']=False; report['error']='backup_missing_or_invalid'
    if not args.apply:
        report['plan']=['configure IVS_AGENT_OS_OFFSITE_MODE and IVS_AGENT_OS_OFFSITE_DEST','register approval for offsite_backup_export','run with --apply --approval-id','verify remote/local copy checksum']
    else:
        g=gate(args.approval_id); report['gate']=g
        if not g.get('ok') or g.get('final')!='ALLOW_BY_POLICY_BUT_NO_EXECUTION':
            report['ok']=False; report['blocked']='approval_required_or_policy_block'
        elif not configured:
            report['ok']=False; report['blocked']='destination_not_configured'
        elif args.mode=='local_mirror':
            dest=Path(args.destination).expanduser().resolve()
            allowed=Path('/root/agent-os-offsite').resolve()
            if not str(dest).startswith(str(allowed)):
                report['ok']=False; report['blocked']='local_destination_not_under_allowed_path'; report['allowed_prefix']=str(allowed)
            else:
                dest.mkdir(parents=True,exist_ok=True); out=dest/backup.name; shutil.copy2(backup,out); report['exported']=True; report['mode']='offsite_backup_local_mirror'; report['export_path']=str(out)
        elif args.mode=='rclone':
            cmd=['rclone','copy',str(backup),args.destination]
            report['rclone_command_plan']=' '.join(cmd)
            # By design, leave real rclone apply disabled until operator config is reviewed.
            report['ok']=False; report['blocked']='rclone_apply_requires_manual_operator_review'
    DEL.mkdir(parents=True,exist_ok=True); (DEL/'agent-os-offsite-backup-latest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    raise SystemExit(0 if report.get('ok') else 2)
if __name__=='__main__': main()
