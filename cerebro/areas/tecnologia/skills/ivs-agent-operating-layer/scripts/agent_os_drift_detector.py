#!/usr/bin/env python3
"""Detect drift between runtime IVS Agent OS skills and canonical cerebro copies.
Read-only: compares file hashes; does not sync or modify files.
"""
import argparse, hashlib, json, time
from pathlib import Path
RUNTIME=Path('/root/.openclaw/workspace/skills')
CANON=Path('/root/cerebro-vital-slim/cerebro/areas/tecnologia/skills')
SKILLS=['ivs-agent-operating-layer','ivs-agent-capability-registry','ivs-agent-handoff-guard','ivs-agent-observability-events','pedro-controller-ivs']
IGNORE={'server/cockpit-token.txt','backups','.DS_Store'}
IGNORE_PREFIXES=('runs/','events/','backups/','alerts/','approvals/approval-ledger.jsonl')
def files(root):
    out={}
    if not root.exists(): return out
    for p in root.rglob('*'):
        if not p.is_file(): continue
        rel=str(p.relative_to(root))
        if rel in IGNORE or rel.startswith(IGNORE_PREFIXES) or any(part in {'__pycache__'} for part in p.parts): continue
        try: out[rel]=hashlib.sha256(p.read_bytes()).hexdigest()
        except Exception as e: out[rel]='ERR:'+str(e)
    return out
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--json',action='store_true'); ap.add_argument('--out',default='/root/deliverables/agent-os-drift-report.json'); args=ap.parse_args()
    findings=[]; details={}
    for s in SKILLS:
        rf=files(RUNTIME/s); cf=files(CANON/s)
        missing_c=sorted(set(rf)-set(cf)); missing_r=sorted(set(cf)-set(rf)); changed=sorted(k for k in set(rf)&set(cf) if rf[k]!=cf[k])
        details[s]={'runtime_files':len(rf),'canonical_files':len(cf),'missing_in_canonical':missing_c,'missing_in_runtime':missing_r,'changed':changed}
        for k in changed: findings.append({'severity':'MEDIUM','skill':s,'code':'hash_mismatch','file':k})
        for k in missing_c: findings.append({'severity':'MEDIUM','skill':s,'code':'missing_in_canonical','file':k})
        for k in missing_r: findings.append({'severity':'LOW','skill':s,'code':'missing_in_runtime','file':k})
    report={'ok':not any(f['severity'] in ('HIGH','MEDIUM') for f in findings),'generated_at':int(time.time()),'mode':'read_only_drift_detector','totals':{'skills':len(SKILLS),'findings':len(findings)},'findings':findings,'details':details}
    Path(args.out).parent.mkdir(parents=True,exist_ok=True); Path(args.out).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
