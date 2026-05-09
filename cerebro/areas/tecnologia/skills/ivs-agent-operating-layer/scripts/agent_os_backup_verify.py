#!/usr/bin/env python3
"""Verify IVS Agent OS backup archives. Read-only."""
import argparse, json, tarfile, time
from pathlib import Path
BACK=Path('/root/.openclaw/workspace/skills/ivs-agent-operating-layer/backups')
REQUIRED_PREFIXES=('runs/','events/','policies/','workflows/')
def latest():
    files=sorted(BACK.glob('agent-os-backup-*.tar.gz'), key=lambda p:p.stat().st_mtime, reverse=True)
    return files[0] if files else None
def verify(path):
    names=[]; errors=[]
    try:
        with tarfile.open(path,'r:gz') as tar:
            for m in tar.getmembers():
                names.append(m.name)
                if m.name.startswith('/') or '..' in Path(m.name).parts: errors.append({'code':'unsafe_member','name':m.name})
    except Exception as e:
        return {'ok':False,'archive':str(path),'error':str(e),'files':0,'required_present':{}}
    req={p:any(n.startswith(p) for n in names) for p in REQUIRED_PREFIXES}
    ok=(not errors) and all(req.values())
    return {'ok':ok,'archive':str(path),'files':len(names),'required_present':req,'errors':errors}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--archive'); ap.add_argument('--json',action='store_true'); args=ap.parse_args()
    p=Path(args.archive) if args.archive else latest()
    if not p:
        report={'ok':False,'error':'no_backup_found','generated_at':int(time.time())}
    else:
        report=verify(p); report['generated_at']=int(time.time()); report['mode']='read_only_backup_verify'
    Path('/root/deliverables/agent-os-backup-verify-latest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    raise SystemExit(0 if report.get('ok') else 2)
if __name__=='__main__': main()
