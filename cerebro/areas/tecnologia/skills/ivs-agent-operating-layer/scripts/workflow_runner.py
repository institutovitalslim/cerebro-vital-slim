#!/usr/bin/env python3
"""IVS Workflow Runner + Event Store (read-only by default).
Records workflow executions with state, evidence, owner and redacted event feed.
"""
import argparse, json, os, re, time, uuid
from pathlib import Path
from typing import Any, Dict, List

BASE=Path('/root/.openclaw/workspace/skills/ivs-agent-operating-layer')
WF_DIR=BASE/'workflows'
RUNS_DIR=BASE/'runs'
EVENTS_DIR=BASE/'events'
PHONE=re.compile(r'55\d{8,13}|\b\d{10,13}\b')
VALID_STATES=['started','in_progress','blocked','completed','failed','cancelled']


def now(): return int(time.time())
def red(s: Any) -> str:
    return PHONE.sub(lambda m: m.group(0)[:4]+'***'+m.group(0)[-2:], str(s))[:2000]
def ensure():
    RUNS_DIR.mkdir(parents=True, exist_ok=True); EVENTS_DIR.mkdir(parents=True, exist_ok=True)
def load_json(p: Path, default):
    try: return json.loads(p.read_text(encoding='utf-8'))
    except Exception: return default
def save_json(p: Path, data):
    p.parent.mkdir(parents=True, exist_ok=True); p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
def workflow(wid: str) -> Dict[str,Any]:
    p=WF_DIR/f'{wid}.json'
    if not p.exists(): raise SystemExit(f'workflow_not_found: {wid}')
    return load_json(p,{})
def append_event(evt: Dict[str,Any]):
    ensure(); evt.setdefault('event_id', str(uuid.uuid4())); evt.setdefault('ts', now()); evt['message']=red(evt.get('message',''))
    day=time.strftime('%Y%m%d', time.gmtime(evt['ts']))
    with (EVENTS_DIR/f'{day}.jsonl').open('a', encoding='utf-8') as f: f.write(json.dumps(evt, ensure_ascii=False)+'\n')
    return evt
def run_path(rid): return RUNS_DIR/f'{rid}.json'
def latest_runs(limit=20):
    ensure(); files=sorted(RUNS_DIR.glob('*.json'), key=lambda p:p.stat().st_mtime, reverse=True)[:limit]
    return [load_json(p,{}) for p in files]

def start(args):
    wf=workflow(args.workflow)
    rid=args.run_id or f"ivr-{time.strftime('%Y%m%d-%H%M%S', time.gmtime())}-{uuid.uuid4().hex[:8]}"
    run={'run_id':rid,'workflow_id':wf.get('id'),'workflow_name':wf.get('name'),'owner':args.owner or wf.get('owner'),'executor':args.executor or wf.get('executor'),'state':'started','started_at':now(),'updated_at':now(),'subject':red(args.subject or ''),'context':red(args.context or ''),'mode':wf.get('mode'),'sensitivity':args.sensitivity,'steps':[{'state':'started','at':now(),'message':'Workflow execution started'}],'evidence':[],'findings':[],'blocked_actions':wf.get('blocked_actions') or [],'allowed_actions':wf.get('allowed_actions') or []}
    save_json(run_path(rid), run)
    append_event({'source':'workflow-runner','kind':'run_started','severity':'OK','run_id':rid,'workflow_id':wf.get('id'),'message':f"Started {wf.get('id')} · {args.subject or ''}"})
    print(json.dumps(run, ensure_ascii=False, indent=2))

def update(args):
    p=run_path(args.run_id); run=load_json(p, None)
    if not run: raise SystemExit(f'run_not_found: {args.run_id}')
    if args.state not in VALID_STATES: raise SystemExit('invalid_state')
    prev=run.get('state'); run['state']=args.state; run['updated_at']=now()
    step={'state':args.state,'at':now(),'message':red(args.message or '')}
    if args.evidence: step['evidence']=args.evidence; run.setdefault('evidence',[]).extend(args.evidence)
    if args.finding: step['finding']=red(args.finding); run.setdefault('findings',[]).append({'at':now(),'state':args.state,'message':red(args.finding)})
    run.setdefault('steps',[]).append(step)
    if args.state in ['completed','failed','cancelled','blocked']: run.setdefault(f'{args.state}_at', now())
    save_json(p, run)
    sev='OK' if args.state in ['in_progress','completed'] else ('HIGH' if args.state in ['failed','blocked'] else 'LOW')
    append_event({'source':'workflow-runner','kind':f'run_{args.state}','severity':sev,'run_id':args.run_id,'workflow_id':run.get('workflow_id'),'message':args.message or f'{prev}->{args.state}'})
    print(json.dumps(run, ensure_ascii=False, indent=2))

def show(args):
    if args.run_id: print(json.dumps(load_json(run_path(args.run_id),{}), ensure_ascii=False, indent=2)); return
    print(json.dumps({'runs':latest_runs(args.limit)}, ensure_ascii=False, indent=2))

def events(args):
    ensure(); files=sorted(EVENTS_DIR.glob('*.jsonl'), reverse=True)[:args.days]
    ev=[]
    for p in files:
        for line in p.read_text(encoding='utf-8', errors='ignore').splitlines():
            try: ev.append(json.loads(line))
            except Exception: pass
    ev=sorted(ev, key=lambda x:x.get('ts',0), reverse=True)[:args.limit]
    print(json.dumps({'events':ev,'totals':{'events':len(ev)}}, ensure_ascii=False, indent=2))

def main():
    ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest='cmd', required=True)
    s=sub.add_parser('start'); s.add_argument('--workflow', required=True); s.add_argument('--subject'); s.add_argument('--context'); s.add_argument('--owner'); s.add_argument('--executor'); s.add_argument('--sensitivity', default='internal'); s.add_argument('--run-id')
    u=sub.add_parser('update'); u.add_argument('--run-id', required=True); u.add_argument('--state', required=True); u.add_argument('--message'); u.add_argument('--evidence', action='append'); u.add_argument('--finding')
    sh=sub.add_parser('show'); sh.add_argument('--run-id'); sh.add_argument('--limit', type=int, default=20)
    e=sub.add_parser('events'); e.add_argument('--limit', type=int, default=50); e.add_argument('--days', type=int, default=7)
    args=ap.parse_args(); ensure(); {'start':start,'update':update,'show':show,'events':events}[args.cmd](args)
if __name__=='__main__': main()
