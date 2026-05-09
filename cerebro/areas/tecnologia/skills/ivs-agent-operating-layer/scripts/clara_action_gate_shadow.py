#!/usr/bin/env python3
"""Clara Action Gate shadow validator.
Read-only/dry-run only. Does not enable CLARA_ADMIN_SEND_ENFORCE_ACTION_GATE and does not send real WhatsApp.
"""
import argparse, json, os, subprocess, time, urllib.request
from pathlib import Path
BASE=Path('/root/.openclaw/workspace/skills/ivs-agent-operating-layer')
DEL=Path('/root/deliverables')
BRIDGE='http://127.0.0.1:8787'
ACTION_GATE=BASE/'scripts/action_gate.py'

def post_json(path, payload, timeout=10):
    data=json.dumps(payload).encode('utf-8')
    req=urllib.request.Request(BRIDGE+path, data=data, headers={'Content-Type':'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body=r.read().decode('utf-8','replace')
            try: js=json.loads(body)
            except Exception: js={'raw':body}
            return {'ok':200<=r.status<300,'status':r.status,'json':js}
    except Exception as e:
        return {'ok':False,'error':str(e)}

def get(path, timeout=5):
    try:
        with urllib.request.urlopen(BRIDGE+path, timeout=timeout) as r:
            body=r.read().decode('utf-8','replace')
            try: js=json.loads(body)
            except Exception: js={'raw':body}
            return {'ok':200<=r.status<300,'status':r.status,'json':js}
    except Exception as e:
        return {'ok':False,'error':str(e)}

def gate(action='clara_admin_send', sensitivity='external_message'):
    cmd=['python3',str(ACTION_GATE),'--agent','clara-whatsapp','--action',action,'--sensitivity',sensitivity]
    try:
        p=subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=30)
        try: js=json.loads(p.stdout)
        except Exception: js={'raw':p.stdout}
        return {'ok':p.returncode==0,'exit_code':p.returncode,'json':js}
    except Exception as e:
        return {'ok':False,'error':str(e)}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--json', action='store_true'); args=ap.parse_args()
    env=os.environ.get('CLARA_ADMIN_SEND_ENFORCE_ACTION_GATE','0')
    checks=[]
    h=get('/healthz'); checks.append({'name':'zapi_bridge_healthz','ok':h.get('ok'), 'detail':h})
    checks.append({'name':'enforcement_not_enabled','ok':env!='1','detail':f'CLARA_ADMIN_SEND_ENFORCE_ACTION_GATE={env}'})
    # Synthetic explicit test lead; dry_run true means no external message.
    lead=post_json('/admin/send', {'phone':'5599999999999','message':'[DRY-RUN IVS] validação shadow Clara Action Gate. Não enviar.','dry_run':True})
    checks.append({'name':'admin_send_synthetic_dry_run','ok':lead.get('ok') and bool(lead.get('json',{}).get('dry_run', True)), 'detail':lead})
    # Known patient/do_not_reply historical Suely/Sueli number from previous safety validation.
    patient=post_json('/admin/send', {'phone':'5571991927242','message':'[DRY-RUN IVS] validação bloqueio paciente. Não enviar.','dry_run':True})
    pj=patient.get('json',{}) if isinstance(patient.get('json'),dict) else {}
    blocked=(not patient.get('ok')) or pj.get('blocked') or pj.get('allowed') is False or 'patient' in json.dumps(pj).lower() or 'do_not_reply' in json.dumps(pj).lower()
    checks.append({'name':'patient_block_dry_run','ok':bool(blocked),'detail':patient})
    g=gate(); gj=g.get('json',{}) if isinstance(g.get('json'),dict) else {}
    expected_block = (not g.get('ok')) or gj.get('final') in {'BLOCK_APPROVAL_REQUIRED','BLOCKED_BY_POLICY','BLOCK_FORBIDDEN'} or gj.get('requires_approval')
    checks.append({'name':'action_gate_shadow_evaluation','ok':bool(expected_block),'detail':g})
    ok=all(c.get('ok') for c in checks)
    report={'ok':ok,'generated_at':int(time.time()),'mode':'clara_action_gate_shadow_read_only_dry_run','checks':checks,'summary':{'external_messages_sent':0,'enforcement_enabled':env=='1','recommendation':'remain_in_phase_1_shadow' if ok else 'fix_before_phase_2'},'blocked_by_design':['no real WhatsApp send','no env toggle change','no patient unblock','no Clara pause']}
    DEL.mkdir(exist_ok=True); (DEL/'clara-action-gate-shadow-latest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    raise SystemExit(0 if ok else 2)
if __name__=='__main__': main()
