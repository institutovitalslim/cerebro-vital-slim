#!/usr/bin/env python3
"""Generate integrity manifest for IVS Agent OS important artifacts."""
import argparse, hashlib, json, time
from pathlib import Path
ROOTS=[Path('/root/.openclaw/workspace/skills/ivs-agent-operating-layer'), Path('/root/deliverables')]
IGNORE_PREFIX=('backups/','server/cockpit-token.txt')
def should_skip(root,p):
    rel=str(p.relative_to(root))
    return rel.startswith(IGNORE_PREFIX) or '__pycache__' in p.parts or p.stat().st_size>16_000_000
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--out',default='/root/deliverables/agent-os-integrity-manifest.json'); args=ap.parse_args()
    items=[]
    for root in ROOTS:
        if not root.exists(): continue
        for p in sorted(root.rglob('*')):
            if not p.is_file() or should_skip(root,p): continue
            try: h=hashlib.sha256(p.read_bytes()).hexdigest(); st=p.stat()
            except Exception as e: h='ERR:'+str(e); st=p.stat()
            items.append({'root':str(root),'rel':str(p.relative_to(root)),'path':str(p),'sha256':h,'size':st.st_size,'mtime':int(st.st_mtime)})
    root_hash=hashlib.sha256('\n'.join(i['sha256']+' '+i['path'] for i in items).encode()).hexdigest()
    report={'ok':True,'generated_at':int(time.time()),'mode':'integrity_manifest','totals':{'files':len(items)},'root_hash':root_hash,'files':items}
    Path(args.out).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'ok':True,'generated_at':report['generated_at'],'totals':report['totals'],'root_hash':root_hash,'out':args.out},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
