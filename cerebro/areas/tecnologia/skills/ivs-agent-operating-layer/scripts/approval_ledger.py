#!/usr/bin/env python3
"""IVS Approval Ledger.
Records explicit approvals for sensitive actions. Does not execute actions.
"""
import argparse, json, time, uuid, re
from pathlib import Path
BASE=Path('/root/.openclaw/workspace/skills/ivs-agent-operating-layer')
LEDGER=BASE/'approvals/approval-ledger.jsonl'
PHONE=re.compile(r'55\d{8,13}|\b\d{10,13}\b')
def red(s): return PHONE.sub(lambda m:m.group(0)[:4]+'***'+m.group(0)[-2:], str(s))[:2000]
def append(entry):
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open('a',encoding='utf-8') as f: f.write(json.dumps(entry,ensure_ascii=False)+'\n')
def read_all():
    if not LEDGER.exists(): return []
    out=[]
    for line in LEDGER.read_text(encoding='utf-8',errors='ignore').splitlines():
        try: out.append(json.loads(line))
        except Exception: pass
    return out
def main():
    ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest='cmd', required=True)
    a=sub.add_parser('add'); a.add_argument('--agent',required=True); a.add_argument('--action',required=True); a.add_argument('--approved-by',required=True); a.add_argument('--evidence',required=True); a.add_argument('--scope',required=True); a.add_argument('--ttl-minutes',type=int,default=60)
    l=sub.add_parser('list'); l.add_argument('--limit',type=int,default=30)
    v=sub.add_parser('verify'); v.add_argument('--agent',required=True); v.add_argument('--action',required=True); v.add_argument('--approval-id')
    args=ap.parse_args(); now=int(time.time())
    if args.cmd=='add':
        e={'approval_id':'appr-'+uuid.uuid4().hex[:12], 'agent':args.agent,'action':args.action,'approved_by':args.approved_by,'evidence':red(args.evidence),'scope':red(args.scope),'created_at':now,'expires_at':now+args.ttl_minutes*60,'mode':'approval_record_no_execution'}
        append(e); print(json.dumps(e,ensure_ascii=False,indent=2)); return
    if args.cmd=='list': print(json.dumps({'approvals':read_all()[-args.limit:]},ensure_ascii=False,indent=2)); return
    rows=read_all(); ok=[]
    for e in rows:
        if args.approval_id and e.get('approval_id')!=args.approval_id: continue
        if e.get('agent')==args.agent and e.get('action')==args.action and int(e.get('expires_at') or 0)>=now: ok.append(e)
    print(json.dumps({'ok':bool(ok),'matches':ok[-5:],'checked_at':now},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
