#!/usr/bin/env python3
"""Read-only critical alert evaluator for IVS Agent OS. Does not send messages by itself."""
import argparse, json, subprocess, time
from pathlib import Path
BASE=Path('/root/.openclaw/workspace/skills/ivs-agent-operating-layer')
DEL=Path('/root/deliverables')
def load(p):
    try: return json.loads(Path(p).read_text(encoding='utf-8'))
    except Exception as e: return {'_error':str(e)}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--json',action='store_true'); args=ap.parse_args()
    subprocess.check_output(['python3',str(BASE/'scripts/agent_os_daily_audit.py'),'--json'], text=True, stderr=subprocess.STDOUT)
    cockpit=load(DEL/'cockpit-unico-ivs-agent-os.json')
    runs=load(DEL/'cockpit-workflow-runs-ivs.json')
    alerts=[]
    if not cockpit.get('ok') or cockpit.get('status') in ('HIGH','MEDIUM'):
        alerts.append({'severity':cockpit.get('status') or 'HIGH','code':'cockpit_not_ok','detail':cockpit.get('sources')})
    for r in (runs.get('runs') or [])[:20]:
        if r.get('state') in ('failed','blocked'):
            alerts.append({'severity':'MEDIUM','code':'workflow_run_problem','run_id':r.get('run_id'),'state':r.get('state')})
    report={'ok':not alerts,'alerts':alerts,'generated_at':int(time.time()),'mode':'read_only_alert_evaluation'}
    (BASE/'alerts').mkdir(parents=True,exist_ok=True)
    (BASE/'alerts/latest-critical-alerts.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    (DEL/'agent-os-critical-alerts-latest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
