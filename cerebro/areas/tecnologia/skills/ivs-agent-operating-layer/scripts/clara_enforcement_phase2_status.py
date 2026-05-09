#!/usr/bin/env python3
"""Read-only status check for Clara Phase 2 enforcement after activation.
Does not call /admin/send with a deliverable non-dry-run payload; validates code/process/Action Gate state.
"""
import argparse,json,subprocess,urllib.request,time
from pathlib import Path
BR=Path('/root/.openclaw/workspace/ops/zapi_bridge/zapi_clara_bridge.py')
DEL=Path('/root/deliverables')
BASE=Path('/root/.openclaw/workspace/skills/ivs-agent-operating-layer')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--json',action='store_true'); args=ap.parse_args()
    checks=[]
    try:
        js=json.loads(urllib.request.urlopen('http://127.0.0.1:8787/healthz',timeout=5).read().decode()); checks.append({'name':'healthz','ok':js.get('ok') is True,'detail':js})
    except Exception as e: checks.append({'name':'healthz','ok':False,'detail':str(e)})
    try:
        pid=subprocess.check_output("pgrep -f 'zapi_clara_bridge.py' | head -1",shell=True,text=True).strip()
        env=open(f'/proc/{pid}/environ','rb').read().split(b'\0')
        toggle=[x.decode(errors='ignore') for x in env if x.startswith(b'CLARA_ADMIN_SEND_ENFORCE_ACTION_GATE=')]
        checks.append({'name':'process_toggle_loaded','ok':toggle==['CLARA_ADMIN_SEND_ENFORCE_ACTION_GATE=1'],'detail':toggle[0] if toggle else None})
    except Exception as e: checks.append({'name':'process_toggle_loaded','ok':False,'detail':str(e)})
    src=BR.read_text(encoding='utf-8',errors='ignore')
    checks.append({'name':'strict_approval_id_patch_present','ok':'BLOCK_APPROVAL_ID_REQUIRED' in src and 'missing_approval_id' in src})
    try:
        out=subprocess.check_output(['python3',str(BASE/'scripts/action_gate.py'),'--agent','clara-whatsapp','--action','followup_whatsapp','--sensitivity','lead'],text=True,stderr=subprocess.STDOUT,timeout=20)
        g=json.loads(out); checks.append({'name':'action_gate_without_approval_blocks','ok':g.get('final')=='BLOCK_APPROVAL_REQUIRED','detail':g.get('final')})
    except Exception as e: checks.append({'name':'action_gate_without_approval_blocks','ok':False,'detail':str(e)})
    ok=all(c.get('ok') for c in checks)
    report={'ok':ok,'generated_at':int(time.time()),'mode':'clara_phase2_enforcement_status_read_only','checks':checks,'external_messages_sent':0}
    DEL.mkdir(exist_ok=True); (DEL/'clara-enforcement-phase2-status-latest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2)); raise SystemExit(0 if ok else 2)
if __name__=='__main__': main()
