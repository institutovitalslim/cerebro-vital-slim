#!/usr/bin/env python3
"""IVS Agent OS readiness scorecard. Read-only."""
import json, subprocess, time, argparse
from pathlib import Path
BASE=Path('/root/.openclaw/workspace/skills/ivs-agent-operating-layer')
DEL=Path('/root/deliverables')
def load(p):
    try: return json.loads(Path(p).read_text(encoding='utf-8'))
    except Exception as e: return {'ok':False,'_error':str(e)}
def run(cmd):
    try:
        out=subprocess.check_output(cmd,text=True,stderr=subprocess.STDOUT,timeout=240)
        return json.loads(out)
    except Exception as e: return {'ok':False,'_error':str(e)}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--json',action='store_true'); args=ap.parse_args()
    data={}
    data['ci']=run(['python3',str(BASE/'scripts/agent_os_ci.py'),'--json'])
    data['workflow']=run(['python3',str(BASE/'scripts/workflow_registry.py'),'--json'])
    data['drift']=run(['python3',str(BASE/'scripts/agent_os_drift_detector.py'),'--json'])
    data['secrets']=run(['python3',str(BASE/'scripts/agent_os_secrets_scanner.py'),'--json'])
    data['backup_verify']=run(['python3',str(BASE/'scripts/agent_os_backup_verify.py'),'--json'])
    data['restore_plan']=run(['python3',str(BASE/'scripts/agent_os_restore_planner.py'),'--json'])
    data['alerts']=run(['python3',str(BASE/'scripts/agent_os_critical_alerts.py'),'--json'])
    criteria=[]
    def add(name, ok, weight, detail=''):
        criteria.append({'name':name,'ok':bool(ok),'weight':weight,'detail':detail})
    add('CI local verde', data['ci'].get('ok'), 20)
    add('Workflow Registry sem findings', data['workflow'].get('ok') and data['workflow'].get('totals',{}).get('findings')==0, 15)
    add('Drift zero', data['drift'].get('ok') and data['drift'].get('totals',{}).get('findings')==0, 15)
    add('Secrets scan zero', data['secrets'].get('ok') and data['secrets'].get('totals',{}).get('findings')==0, 15)
    add('Backup verificado', data['backup_verify'].get('ok'), 10)
    add('Restore dry-run OK', data['restore_plan'].get('ok'), 10)
    add('Alertas críticos zerados', data['alerts'].get('ok') and len(data['alerts'].get('alerts',[]))==0, 10)
    add('Cockpit protegido disponível', Path(BASE/'scripts/agent_os_cockpit_server.py').exists(), 5)
    score=sum(c['weight'] for c in criteria if c['ok'])
    status='READY' if score>=95 else 'ATTENTION' if score>=80 else 'NOT_READY'
    report={'ok':status=='READY','status':status,'score':score,'max_score':sum(c['weight'] for c in criteria),'generated_at':int(time.time()),'criteria':criteria,'mode':'read_only_readiness_scorecard'}
    DEL.mkdir(parents=True,exist_ok=True)
    (DEL/'agent-os-readiness-scorecard.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    md=['# IVS Agent OS — Readiness Scorecard','',f"Status: **{status}**",f"Score: **{score}/{report['max_score']}**",'', '## Critérios']
    for c in criteria: md.append(f"- {'OK' if c['ok'] else 'FALHA'} · {c['name']} ({c['weight']} pts)")
    (DEL/'agent-os-readiness-scorecard.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    raise SystemExit(0 if report['ok'] else 2)
if __name__=='__main__': main()
