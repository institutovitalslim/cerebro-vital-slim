#!/usr/bin/env python3
"""Read-only auditor for Gateway crons vs IVS Agent OS registry."""
import argparse, json, subprocess, time, re, sys
from pathlib import Path
BASE=Path('/root/.openclaw/workspace/skills/ivs-agent-operating-layer')
DEL=Path('/root/deliverables')
CONTEXT_COMPRESSOR=Path('/root/cerebro-vital-slim/tools/ivs-context-compressor/ivs_context_compressor.py')
REG=BASE/'crons/active-crons.json'
WORKFLOWS=BASE/'workflows'
AGENT_OS_PREFIX='IVS Agent OS'

def load(p, default):
    try: return json.loads(Path(p).read_text(encoding='utf-8'))
    except Exception: return default

def fetch_gateway():
    try:
        out=subprocess.check_output(['openclaw','cron','list','--json'], text=True, stderr=subprocess.STDOUT, timeout=60)
        return json.loads(out)
    except Exception as e:
        return {'_error':str(e), 'jobs':[]}

def workflow_ids():
    ids=set()
    for p in WORKFLOWS.glob('*.json'):
        try: ids.add(json.load(open(p)).get('id'))
        except Exception: pass
    return ids


def compress_context(path, kind='cron-log'):
    if not CONTEXT_COMPRESSOR.exists():
        return {'ok': False, 'error': f'compressor not found: {CONTEXT_COMPRESSOR}'}
    try:
        raw=subprocess.check_output([sys.executable, str(CONTEXT_COMPRESSOR), '--input', str(path), '--type', kind, '--format', 'json'], text=True, stderr=subprocess.STDOUT, timeout=120)
        payload=json.loads(raw)
        return {'ok': bool(payload.get('ok')), 'sha256': payload.get('sha256'), 'outputs': payload.get('outputs'), 'evidence': payload.get('evidence'), 'critical_line_count': (payload.get('summary') or {}).get('critical_line_count'), 'redactions': (payload.get('summary') or {}).get('redactions')}
    except Exception as e:
        return {'ok': False, 'error': str(e)[:500]}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--json',action='store_true'); ap.add_argument('--gateway-json'); ap.add_argument('--compress-context', action='store_true', help='Run IVS Context Compressor on the generated cron audit (read-only, optional).'); args=ap.parse_args()
    gw=load(args.gateway_json, {}) if args.gateway_json else fetch_gateway()
    jobs=gw.get('jobs', gw if isinstance(gw,list) else [])
    reg=load(REG, [])
    reg_jobs=reg if isinstance(reg,list) else reg.get('jobs',[])
    reg_ids={j.get('id') for j in reg_jobs if isinstance(j,dict)}
    wf=workflow_ids(); findings=[]
    enabled=[j for j in jobs if j.get('enabled')]
    disabled=[j for j in jobs if not j.get('enabled')]
    names={}
    for j in jobs: names.setdefault(j.get('name',''), []).append(j.get('id'))
    for name,ids in names.items():
        if name and len(ids)>1: findings.append({'severity':'LOW','code':'duplicate_cron_name','name':name,'ids':ids})
    for j in jobs:
        jid=j.get('id'); name=j.get('name','')
        if name.startswith(AGENT_OS_PREFIX) and jid not in reg_ids:
            findings.append({'severity':'MEDIUM','code':'agent_os_cron_missing_registry','id':jid,'name':name})
        if not j.get('enabled'):
            findings.append({'severity':'LOW','code':'disabled_cron_present','id':jid,'name':name})
        payload=json.dumps(j.get('payload') or {}, ensure_ascii=False).lower()
        delivery=json.dumps(j.get('delivery') or {}, ensure_ascii=False).lower()
        if name.startswith(AGENT_OS_PREFIX) and 'announce' in delivery and 'somente se' not in payload and 'se falhar' not in payload:
            findings.append({'severity':'LOW','code':'agent_os_cron_may_announce_too_much','id':jid,'name':name})
    # Registry workflow references
    for r in reg_jobs:
        if isinstance(r,dict) and r.get('workflow') and r.get('workflow') not in wf:
            findings.append({'severity':'MEDIUM','code':'registry_workflow_missing','id':r.get('id'),'workflow':r.get('workflow')})
    report={'ok':not any(f['severity'] in ('HIGH','MEDIUM') for f in findings),'generated_at':int(time.time()),'mode':'read_only_cron_audit','totals':{'gateway_jobs':len(jobs),'enabled':len(enabled),'disabled':len(disabled),'registry_jobs':len(reg_jobs),'findings':len(findings)},'findings':findings,'agent_os_crons':[{'id':j.get('id'),'name':j.get('name'),'enabled':j.get('enabled'),'schedule':j.get('schedule')} for j in jobs if str(j.get('name','')).startswith(AGENT_OS_PREFIX)]}
    DEL.mkdir(parents=True,exist_ok=True); out=DEL/'agent-os-cron-audit-latest.json'; out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    if args.compress_context:
        report['compressed_context']=compress_context(out, 'cron-log')
        out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    raise SystemExit(0 if report['ok'] else 2)
if __name__=='__main__': main()
