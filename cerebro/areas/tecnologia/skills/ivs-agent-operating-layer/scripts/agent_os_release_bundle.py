#!/usr/bin/env python3
"""Create sanitized IVS Agent OS release bundle. Excludes secrets/backups/token files."""
import argparse, json, tarfile, time, hashlib
from pathlib import Path
BASE=Path('/root/.openclaw/workspace/skills/ivs-agent-operating-layer')
DEL=Path('/root/deliverables')
OUT=Path('/root/deliverables/releases')
EXCLUDE_PARTS={'backups','server','__pycache__'}
EXCLUDE_NAMES={'cockpit-token.txt'}
INCLUDE_DELIVERABLE_PREFIX=('cockpit-','agent-os-','approval-console-','runbook-','workflow-registry-')
def safe_add(tar, path, arc):
    if path.name in EXCLUDE_NAMES or any(part in EXCLUDE_PARTS for part in path.parts): return False
    if path.is_file() and path.stat().st_size <= 8_000_000:
        tar.add(path, arcname=arc); return True
    return False
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--json',action='store_true'); args=ap.parse_args()
    OUT.mkdir(parents=True,exist_ok=True); ts=time.strftime('%Y%m%d-%H%M%S')
    bundle=OUT/f'ivs-agent-os-release-{ts}.tar.gz'
    included=[]
    with tarfile.open(bundle,'w:gz') as tar:
        for p in BASE.rglob('*'):
            if safe_add(tar,p,'skill/'+str(p.relative_to(BASE))): included.append('skill/'+str(p.relative_to(BASE)))
        for p in DEL.iterdir() if DEL.exists() else []:
            if p.is_file() and p.name.startswith(INCLUDE_DELIVERABLE_PREFIX) and p.name!='cockpit-server-token-info.json':
                if safe_add(tar,p,'deliverables/'+p.name): included.append('deliverables/'+p.name)
    report={'ok':True,'generated_at':int(time.time()),'bundle':str(bundle),'sha256':sha(bundle),'files':len(included),'mode':'sanitized_release_bundle_no_secrets','included_sample':included[:50]}
    (DEL/'agent-os-release-bundle-latest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
