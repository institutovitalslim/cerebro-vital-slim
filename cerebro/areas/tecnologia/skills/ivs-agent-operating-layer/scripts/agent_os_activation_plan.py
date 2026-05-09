#!/usr/bin/env python3
"""Read-only validator for IVS Agent OS production activation plan."""
import argparse, json, subprocess, os, time
from pathlib import Path
BASE=Path('/root/.openclaw/workspace/skills/ivs-agent-operating-layer')
DEL=Path('/root/deliverables')
PLAN=BASE/'activation/production-activation-plan.json'

def run(cmd, timeout=60):
    try:
        p=subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=timeout)
        return {'ok':p.returncode==0,'exit_code':p.returncode,'log':p.stdout[-2000:]}
    except Exception as e:
        return {'ok':False,'error':str(e)}

def j(path):
    try: return json.load(open(path))
    except Exception: return None

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--json',action='store_true'); ap.add_argument('--skip-ci',action='store_true',help='Do not invoke agent_os_ci; used by CI to avoid recursion'); args=ap.parse_args()
    plan=json.load(open(PLAN))
    checks=[]
    checks.append({'name':'plan_parse','ok':bool(plan.get('phases')),'detail':f"{len(plan.get('phases',[]))} phases"})
    
    if args.skip_ci:
        checks.append({'name':'agent_os_ci','ok':True,'detail':'skipped_inside_ci'})
    else:
        ci=run(['python3',str(BASE/'scripts/agent_os_ci.py'),'--json'],timeout=180); checks.append({'name':'agent_os_ci','ok':ci['ok']})
    reg=j('/root/deliverables/workflow-registry-after-offsite-backup.json') or j('/root/deliverables/workflow-registry-after-activation-plan.json') or {}
    checks.append({'name':'workflow_registry_previous','ok':bool(reg.get('ok', True))})
    clara_env=os.environ.get('CLARA_ADMIN_SEND_ENFORCE_ACTION_GATE','0')
    checks.append({'name':'clara_enforcement_not_auto_enabled','ok':clara_env!='1','detail':f'CLARA_ADMIN_SEND_ENFORCE_ACTION_GATE={clara_env}'})
    cs=run(['python3',str(BASE/'scripts/agent_os_cockpit_service.py'),'status'],timeout=30); checks.append({'name':'cockpit_service_status','ok':cs['ok']})
    off=j('/root/deliverables/agent-os-offsite-backup-latest.json') or {}
    checks.append({'name':'offsite_no_export_default','ok':off.get('exported') is False})
    ok=all(c.get('ok') for c in checks)
    report={'ok':ok,'generated_at':int(time.time()),'mode':'read_only_activation_plan_validation','plan':str(PLAN),'phase_count':len(plan.get('phases',[])),'checks':checks,'recommendation':'ready_for_phase_0_and_phase_1_shadow_only' if ok else 'fix_findings_before_activation','blocked_by_design':['phase_2_clara_enforcement requires explicit Tiaro approval','phase_3_pedro_omie_guarded_write requires approval and credential review','no external/offsite export without approval and destination']}
    DEL.mkdir(exist_ok=True); (DEL/'agent-os-production-activation-plan-latest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    raise SystemExit(0 if ok else 2)
if __name__=='__main__': main()
