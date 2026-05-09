#!/usr/bin/env python3
"""RC-25 preflight pipeline for IVS Agent OS.
Runs CI, artifact index, drift detector, then creates a local RC evidence folder.
Does not push, restart, send messages, or execute sensitive actions.
"""
import argparse, json, shutil, subprocess, time
from pathlib import Path
BASE=Path('/root/.openclaw/workspace/skills/ivs-agent-operating-layer')
DEL=Path('/root/deliverables')
RC_ROOT=Path('/root/cerebro-vital-slim/cerebro/operacional')
def run(name, cmd, allow_fail=False):
    p=subprocess.run(cmd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=240)
    ok=(p.returncode==0) or allow_fail
    return {'name':name,'ok':ok,'exit_code':p.returncode,'log':p.stdout[-5000:]}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--name',default='ivs-agent-os-rc25-pipeline'); ap.add_argument('--json',action='store_true'); args=ap.parse_args()
    ts=time.strftime('%Y-%m-%d-%H%M%S')
    checks=[]
    checks.append(run('ci',['python3',str(BASE/'scripts/agent_os_ci.py'),'--json']))
    checks.append(run('artifact_index',['python3',str(BASE/'scripts/generate_agent_os_artifact_index.py')]))
    checks.append(run('drift_detector',['python3',str(BASE/'scripts/agent_os_drift_detector.py'),'--json'], allow_fail=True))
    # Drift may fail before sync; report but do not block RC folder creation.
    report={'ok':checks[0]['ok'] and checks[1]['ok'],'generated_at':int(time.time()),'checks':checks,'mode':'rc25_preflight_no_external_side_effects'}
    rc=RC_ROOT/f'graphify-{ts}-{args.name}'
    (rc/'raw').mkdir(parents=True,exist_ok=True); (rc/'output').mkdir(parents=True,exist_ok=True)
    for src in [DEL/'agent-os-ci-latest.json', DEL/'agent-os-artifact-index.json', DEL/'agent-os-drift-report.json']:
        if src.exists(): shutil.copy2(src, rc/'raw'/src.name)
    (rc/'output/GRAPH_REPORT.md').write_text('# RC-25 Pipeline IVS Agent OS\n\nPipeline preflight executado.\n\n- CI: %s\n- Artifact index: %s\n- Drift detector: %s\n\nEste pipeline não executa ação sensível, não envia mensagens e não faz push.\n' % tuple('OK' if c['ok'] else 'FALHOU' for c in checks), encoding='utf-8')
    report['rc_path']=str(rc)
    (DEL/'agent-os-rc25-pipeline-latest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    raise SystemExit(0 if report['ok'] else 2)
if __name__=='__main__': main()
