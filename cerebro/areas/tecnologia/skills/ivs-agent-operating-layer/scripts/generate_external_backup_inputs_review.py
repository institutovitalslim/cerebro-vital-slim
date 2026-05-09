#!/usr/bin/env python3
"""Read-only review/proposal for the 4 inputs required by external backup export. No export, no credential creation."""
import argparse,json,time,shutil,subprocess,re
from pathlib import Path
DEL=Path('/root/deliverables')
REMOTE_RE=re.compile(r'^[A-Za-z0-9_.-]+:[A-Za-z0-9_./=-]+$')

def remotes():
    if not shutil.which('rclone'):
        return {'installed':False,'remotes':[],'error':'rclone_not_installed'}
    try:
        out=subprocess.check_output(['rclone','listremotes'],text=True,stderr=subprocess.STDOUT,timeout=20)
        return {'installed':True,'remotes':[x.strip().rstrip(':') for x in out.splitlines() if x.strip()]}
    except Exception as e:
        return {'installed':True,'remotes':[],'error':str(e)[:500]}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--destination',default=''); ap.add_argument('--retention',default='7 daily + 4 weekly + 6 monthly'); ap.add_argument('--json',action='store_true'); args=ap.parse_args()
    rc=remotes(); proposed=args.destination or 'remote:ivs-agent-os-backups'
    findings=[]
    if not REMOTE_RE.match(proposed): findings.append({'severity':'HIGH','code':'destination_format_invalid','destination':proposed})
    remote_name=proposed.split(':',1)[0] if ':' in proposed else None
    credential_status='not_ready'
    if not rc.get('installed'):
        findings.append({'severity':'HIGH','code':'rclone_not_installed'})
    elif remote_name not in rc.get('remotes',[]):
        findings.append({'severity':'HIGH','code':'rclone_remote_not_configured','remote':remote_name,'available_remotes':rc.get('remotes')})
    else:
        credential_status='configured_remote_detected_not_secret_printed'
    report={'ok':not any(f['severity']=='HIGH' for f in findings),'generated_at':int(time.time()),'mode':'external_backup_four_inputs_review_no_export','inputs':{'destination':proposed,'credential_review':credential_status,'retention_policy':args.retention,'approval_phrase':f'Autorizo exportar backup Agent OS via rclone para {proposed} agora'},'rclone_inspection':rc,'findings':findings,'execution_performed':False,'blocked_by_design':['no rclone copy','no credential creation','no token print','no approval write']}
    DEL.mkdir(parents=True,exist_ok=True); (DEL/'external-backup-four-inputs-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2)); raise SystemExit(0 if report['ok'] else 2)
if __name__=='__main__': main()
