#!/usr/bin/env python3
"""IVS Agent OS retention/backup. Read-only backup + optional prune with explicit flag."""
import argparse, json, tarfile, time
from pathlib import Path
BASE=Path('/root/.openclaw/workspace/skills/ivs-agent-operating-layer')
BACK=BASE/'backups'
TARGETS=[BASE/'runs', BASE/'events', BASE/'approvals', BASE/'policies', BASE/'workflows']
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--retention-days',type=int,default=90); ap.add_argument('--prune',action='store_true'); ap.add_argument('--json',action='store_true'); args=ap.parse_args()
    BACK.mkdir(parents=True,exist_ok=True); ts=time.strftime('%Y%m%d-%H%M%S')
    archive=BACK/f'agent-os-backup-{ts}.tar.gz'
    included=[]
    with tarfile.open(archive,'w:gz') as tar:
        for t in TARGETS:
            if t.exists(): tar.add(t, arcname=t.relative_to(BASE)); included.append(str(t))
    cutoff=time.time()-args.retention_days*86400; pruned=[]
    if args.prune:
        for p in list((BASE/'runs').glob('*.json'))+list((BASE/'events').glob('*.json*')):
            try:
                if p.stat().st_mtime < cutoff: pruned.append(str(p)); p.unlink()
            except Exception: pass
    report={'ok':True,'mode':'backup_read_only' if not args.prune else 'backup_then_prune','archive':str(archive),'included':included,'retention_days':args.retention_days,'pruned':pruned,'generated_at':int(time.time())}
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
