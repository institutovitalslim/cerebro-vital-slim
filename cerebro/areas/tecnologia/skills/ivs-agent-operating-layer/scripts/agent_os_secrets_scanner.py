#!/usr/bin/env python3
"""Read-only secrets scanner for IVS Agent OS artifacts/canonical files.
Reports suspicious tokens without printing full values.
"""
import argparse, json, re, time
from pathlib import Path
ROOTS=[Path('/root/.openclaw/workspace/skills/ivs-agent-operating-layer'), Path('/root/deliverables'), Path('/root/cerebro-vital-slim/cerebro/areas/tecnologia/skills/ivs-agent-operating-layer')]
IGNORE_PARTS={'backups','__pycache__'}
IGNORE_FILES={'cockpit-token.txt'}
PATTERNS=[
 ('openai_key', re.compile(r'sk-[A-Za-z0-9_\-]{20,}')),
 ('generic_secret_assignment', re.compile(r'(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*["\']?([A-Za-z0-9_\-\.]{16,})')),
 ('bearer_token', re.compile(r'Bearer\s+[A-Za-z0-9_\-\.]{20,}', re.I)),
 ('url_token_query', re.compile(r'(?i)[?&](token|key|secret|mcp_token)=[^\s"\']{8,}')),
]
TEXT_SUFFIX={'.py','.json','.jsonl','.md','.html','.txt','.log','.csv','.yml','.yaml'}
def mask(s):
    s=str(s)
    if len(s)<=10: return '<redacted>'
    return s[:4]+'***'+s[-4:]
def scan_file(p):
    out=[]
    try:
        if p.suffix.lower() not in TEXT_SUFFIX or p.stat().st_size>2_000_000: return out
        text=p.read_text(encoding='utf-8',errors='ignore')
    except Exception: return out
    for name,rx in PATTERNS:
        for m in rx.finditer(text):
            val=m.group(0)
            # Avoid known placeholders/redacted strings
            if '<redacted>' in val or '{H.token}' in val or 'APPROVAL_ID' in val or 'AGENTE' in val or 'EVIDENCIA' in val: continue
            line=text.count('\n',0,m.start())+1
            out.append({'severity':'HIGH' if name!='generic_secret_assignment' else 'MEDIUM','code':name,'file':str(p),'line':line,'preview':mask(val)})
    return out
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--json',action='store_true'); ap.add_argument('--out',default='/root/deliverables/agent-os-secrets-scan-latest.json'); args=ap.parse_args()
    findings=[]; scanned=0
    for r in ROOTS:
        if not r.exists(): continue
        for p in r.rglob('*'):
            if not p.is_file(): continue
            if p.name in IGNORE_FILES or any(part in IGNORE_PARTS for part in p.parts): continue
            scanned+=1; findings.extend(scan_file(p))
    report={'ok':not any(f['severity']=='HIGH' for f in findings),'generated_at':int(time.time()),'mode':'read_only_secrets_scan','totals':{'files_scanned':scanned,'findings':len(findings)},'findings':findings[:200]}
    Path(args.out).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    raise SystemExit(0 if report['ok'] else 2)
if __name__=='__main__': main()
