#!/usr/bin/env python3
"""Publish encrypted IVS Agent OS backup behind authenticated backup subdomain.
No raw .tar.gz is exposed. Secrets are read from /root/secrets only.
"""
import argparse, json, os, subprocess, time, hashlib
from pathlib import Path
BASE=Path('/root/.openclaw/workspace/skills/ivs-agent-operating-layer')
BACKUP=BASE/'scripts/agent_os_retention_backup.py'
VERIFY=BASE/'scripts/agent_os_backup_verify.py'
SECRETS=Path('/root/secrets/ivs-backup-publication-latest.json')
PUB=Path('/srv/ivs-agent-os-backups/agent-os')
DEL=Path('/root/deliverables')

def run(cmd, **kw):
    return subprocess.run(cmd, text=True, capture_output=True, timeout=kw.pop('timeout',120), **kw)

def latest_backup():
    files=sorted((BASE/'backups').glob('agent-os-backup-*.tar.gz'), key=lambda p:p.stat().st_mtime, reverse=True)
    return files[0] if files else None

def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1024*1024), b''): h.update(b)
    return h.hexdigest()

def prune(retain):
    encs=sorted(PUB.glob('agent-os-backup-*.tar.gz.enc'), key=lambda p:p.stat().st_mtime, reverse=True)
    removed=[]
    for p in encs[retain:]:
        for q in [p, Path(str(p)+'.sha256')]:
            if q.exists():
                removed.append(str(q)); q.unlink()
    return removed

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--retain',type=int,default=7)
    ap.add_argument('--no-new-backup',action='store_true')
    ap.add_argument('--json',action='store_true')
    args=ap.parse_args()
    if not SECRETS.exists():
        raise SystemExit('missing /root/secrets/ivs-backup-publication-latest.json')
    secret=json.loads(SECRETS.read_text())
    passphrase=secret.get('encryption_passphrase')
    if not passphrase:
        raise SystemExit('missing encryption passphrase')
    if not args.no_new_backup:
        b=run(['python3',str(BACKUP),'--json'], timeout=180)
    backup=latest_backup()
    if not backup: raise SystemExit('backup_missing')
    v=run(['python3',str(VERIFY),'--archive',str(backup),'--json'], timeout=180)
    try: verify=json.loads(v.stdout)
    except Exception: verify={'ok':False,'raw':v.stdout[-500:]}
    if not verify.get('ok'):
        raise SystemExit('backup_verify_failed')
    PUB.mkdir(parents=True,exist_ok=True)
    enc=PUB/(backup.name+'.enc')
    tmp=PUB/(backup.name+'.enc.tmp')
    cmd=['openssl','enc','-aes-256-cbc','-salt','-pbkdf2','-iter','310000','-in',str(backup),'-out',str(tmp),'-pass',f'pass:{passphrase}']
    r=run(cmd, timeout=180)
    if r.returncode: raise SystemExit('openssl_failed: '+r.stderr[-300:])
    tmp.replace(enc)
    digest=sha256(enc)
    sha=Path(str(enc)+'.sha256')
    sha.write_text(f'{digest}  {enc.name}\n', encoding='utf-8')
    os.chmod(enc,0o640); os.chmod(sha,0o640)
    try:
        import grp
        gid=grp.getgrnam('www-data').gr_gid
        os.chown(enc,-1,gid); os.chown(sha,-1,gid)
    except Exception: pass
    removed=prune(args.retain)
    manifest={
      'generated_at':int(time.time()),
      'fqdn':'backup.institutovitalslim.com.br',
      'latest':enc.name,
      'latest_url':'https://backup.institutovitalslim.com.br/agent-os/'+enc.name,
      'latest_sha256':digest,
      'encryption':'openssl enc -aes-256-cbc -salt -pbkdf2 -iter 310000',
      'auth_required':True,
      'raw_backup_public':False,
      'retained_encrypted': [p.name for p in sorted(PUB.glob('agent-os-backup-*.tar.gz.enc'), key=lambda p:p.stat().st_mtime, reverse=True)],
    }
    (PUB/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    os.chmod(PUB/'manifest.json',0o640)
    try: os.chown(PUB/'manifest.json',-1,gid)
    except Exception: pass
    report={k:v for k,v in manifest.items() if k!='retained_encrypted'}
    report.update({'ok':True,'source_backup':str(backup),'encrypted_path':str(enc),'checksum_path':str(sha),'removed':removed,'retain':args.retain})
    DEL.mkdir(parents=True,exist_ok=True)
    (DEL/'protected-backup-publication-latest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
