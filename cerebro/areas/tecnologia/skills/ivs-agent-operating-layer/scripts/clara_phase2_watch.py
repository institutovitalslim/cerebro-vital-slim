#!/usr/bin/env python3
"""Read-only post-activation watch for Clara Phase 2 enforcement.
Checks health/toggle/status and scans recent bridge logs for risky events.
Never pauses Clara, never changes env, never sends WhatsApp.
"""
import argparse, json, re, subprocess, time, urllib.request, datetime
from pathlib import Path
BASE=Path('/root/.openclaw/workspace/skills/ivs-agent-operating-layer')
DEL=Path('/root/deliverables')
LOGS=[Path('/root/.openclaw/workspace/ops/zapi_bridge/zapi_bridge.log'),Path('/root/.openclaw/workspace/ops/zapi_bridge/zapi_clara_bridge.log')]
STATUS=BASE/'scripts/clara_enforcement_phase2_status.py'

def run_json(cmd, timeout=30):
    try:
        out=subprocess.check_output(cmd,text=True,stderr=subprocess.STDOUT,timeout=timeout)
        return json.loads(out)
    except Exception as e:
        return {'ok':False,'error':str(e)}

def tail(path, max_bytes=30000):
    if not path.exists(): return ''
    data=path.read_bytes()[-max_bytes:]
    return data.decode('utf-8','ignore')

def filter_recent(text, since_epoch):
    out=[]
    for line in text.splitlines():
        m=re.match(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]', line)
        if not m:
            continue
        try:
            ts=datetime.datetime.strptime(m.group(1),'%Y-%m-%d %H:%M:%S').replace(tzinfo=datetime.timezone.utc).timestamp()
        except Exception:
            continue
        if ts >= since_epoch:
            out.append(line)
    return '\n'.join(out)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--json',action='store_true'); ap.add_argument('--since-minutes',type=int,default=15); args=ap.parse_args()
    status=run_json(['python3',str(STATUS),'--json'])
    raw_text='\n'.join(tail(p) for p in LOGS)
    since_epoch=time.time()-args.since_minutes*60
    text=filter_recent(raw_text, since_epoch)
    patterns={
        'action_gate_blocks': r'blocked_by_action_gate|BLOCK_APPROVAL|BLOCK_APPROVAL_ID_REQUIRED',
        'admin_send_success': r'admin_send phone=.*status=2\d\d',
        'admin_send_failed': r'admin_send failed|status=5\d\d|status=4\d\d',
        'patient_block': r'patient_do_not_reply|patient_bridge_known|blocked.*patient',
        'traceback': r'Traceback|Exception|RuntimeError',
        'health_errors': r'address already in use|EADDRINUSE|connection refused'
    }
    counts={k:len(re.findall(v,text,re.I)) for k,v in patterns.items()}
    findings=[]
    if not status.get('ok'):
        findings.append({'severity':'HIGH','code':'phase2_status_not_ok','detail':status})
    if counts['traceback']:
        findings.append({'severity':'MEDIUM','code':'recent_exception_in_logs','count':counts['traceback']})
    if counts['admin_send_failed']:
        findings.append({'severity':'MEDIUM','code':'recent_admin_send_failed','count':counts['admin_send_failed']})
    # success is not automatically bad; report because it means a real admin send happened.
    if counts['admin_send_success']:
        findings.append({'severity':'LOW','code':'recent_admin_send_success_detected','count':counts['admin_send_success']})
    ok=not any(f['severity']=='HIGH' for f in findings)
    report={'ok':ok,'generated_at':int(time.time()),'mode':'read_only_clara_phase2_watch','since_minutes':args.since_minutes,'status':status,'log_counts':counts,'findings':findings,'actions_taken':[],'guardrails':['no pause','no env change','no WhatsApp send','report only']}
    DEL.mkdir(exist_ok=True)
    (DEL/'clara-phase2-watch-latest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    stamp=time.strftime('%Y%m%d-%H%M%S')
    (DEL/f'clara-phase2-watch-{stamp}.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    raise SystemExit(0 if ok else 2)
if __name__=='__main__': main()
