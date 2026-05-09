#!/usr/bin/env python3
"""Local CI for IVS Agent OS. Runs registry, tests, cockpit generation and guard smoke checks."""
import argparse, json, subprocess, time
from pathlib import Path
BASE=Path('/root/.openclaw/workspace/skills/ivs-agent-operating-layer')
DEL=Path('/root/deliverables')
def cmd(name, c, allow_fail=False):
    p=subprocess.run(c,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=180)
    return {'name':name,'ok':p.returncode==0 or allow_fail,'exit_code':p.returncode,'log':p.stdout[-4000:]}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--json',action='store_true'); args=ap.parse_args()
    checks=[]
    checks.append(cmd('workflow_registry',['python3',str(BASE/'scripts/workflow_registry.py'),'--json']))
    checks.append(cmd('regression_tests',['python3',str(BASE/'tests/test_agent_os_regression.py')]))
    checks.append(cmd('cockpit_generation',['python3',str(BASE/'scripts/generate_agent_os_cockpit.py'),'--out',str(DEL/'cockpit-unico-ivs-agent-os.html'),'--json-out',str(DEL/'cockpit-unico-ivs-agent-os.json')]))
    checks.append(cmd('cli_status',['python3',str(BASE/'scripts/agent_os_cli.py'),'status']))
    checks.append(cmd('secrets_scan',['python3',str(BASE/'scripts/agent_os_secrets_scanner.py'),'--json']))
    checks.append(cmd('integrity_manifest',['python3',str(BASE/'scripts/agent_os_integrity_manifest.py')]))
    checks.append(cmd('cron_audit',['python3',str(BASE/'scripts/agent_os_cron_auditor.py'),'--json']))
    checks.append(cmd('cockpit_service_status',['python3',str(BASE/'scripts/agent_os_cockpit_service.py'),'status']))
    checks.append(cmd('offsite_backup_readiness',['python3',str(BASE/'scripts/agent_os_offsite_backup.py'),'--json']))
    checks.append(cmd('production_activation_plan',['python3',str(BASE/'scripts/agent_os_activation_plan.py'),'--json','--skip-ci']))
    checks.append(cmd('clara_action_gate_shadow',['python3',str(BASE/'scripts/clara_action_gate_shadow.py'),'--json']))
    checks.append(cmd('clara_enforcement_phase2_preflight',['python3',str(BASE/'scripts/clara_enforcement_preflight.py'),'--json']))
    checks.append(cmd('pedro_omie_write_preflight',['python3',str(BASE/'scripts/pedro_omie_write_preflight.py'),'--json']))
    checks.append(cmd('approval_queue',['python3',str(BASE/'scripts/generate_approval_queue.py'),'--json']))
    checks.append(cmd('gate_blocks_pedro_without_approval',['python3',str(BASE/'scripts/sensitive_action_guard.py'),'--agent','pedro-controller-ivs','--action','omie_write','--sensitivity','financial'], allow_fail=True))
    # guard smoke is expected to exit non-zero. OK only if it blocked.
    if checks[-1]['exit_code']==0: checks[-1]['ok']=False; checks[-1]['log']+='\nExpected block did not happen.'
    else: checks[-1]['ok']=True
    report={'ok':all(c['ok'] for c in checks),'generated_at':int(time.time()),'checks':checks,'mode':'local_ci_no_external_side_effects'}
    DEL.mkdir(parents=True,exist_ok=True)
    (DEL/'agent-os-ci-latest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    (DEL/'agent-os-ci-latest.log').write_text('\n\n'.join(f"## {c['name']} ok={c['ok']} exit={c['exit_code']}\n{c['log']}" for c in checks),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    raise SystemExit(0 if report['ok'] else 2)
if __name__=='__main__': main()
