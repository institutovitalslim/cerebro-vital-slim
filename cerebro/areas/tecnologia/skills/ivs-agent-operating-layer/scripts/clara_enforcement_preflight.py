#!/usr/bin/env python3
"""Phase 2 preflight for Clara Action Gate enforcement.
Does not enable enforcement. Produces approval packet and rollback checklist.
"""
import argparse, json, os, subprocess, time
from pathlib import Path
BASE=Path('/root/.openclaw/workspace/skills/ivs-agent-operating-layer')
DEL=Path('/root/deliverables')
SHADOW=BASE/'scripts/clara_action_gate_shadow.py'
PLAN=BASE/'activation/production-activation-plan.json'
APPROVAL=BASE/'scripts/approval_ledger.py'

def run(cmd, timeout=90):
    try:
        p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=timeout)
        try: js=json.loads(p.stdout)
        except Exception: js={'raw':p.stdout[-2000:]}
        return {'ok':p.returncode==0,'exit_code':p.returncode,'json':js}
    except Exception as e:
        return {'ok':False,'error':str(e)}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--approval-id'); ap.add_argument('--json',action='store_true'); args=ap.parse_args()
    env=os.environ.get('CLARA_ADMIN_SEND_ENFORCE_ACTION_GATE','0')
    checks=[]
    checks.append({'name':'activation_plan_exists','ok':PLAN.exists()})
    shadow=run(['python3',str(SHADOW),'--json'],timeout=120)
    checks.append({'name':'phase1_shadow_ok','ok':shadow.get('ok'), 'detail':shadow.get('json',{})})
    checks.append({'name':'enforcement_currently_off','ok':env!='1','detail':f'CLARA_ADMIN_SEND_ENFORCE_ACTION_GATE={env}'})
    approval_status={'ok':False,'reason':'not_supplied'}
    if args.approval_id:
        approval_status=run(['python3',str(APPROVAL),'check','--approval-id',args.approval_id,'--json'],timeout=30)
    checks.append({'name':'explicit_approval_present_for_activation','ok':bool(args.approval_id and approval_status.get('ok')), 'detail':approval_status})
    phase2_ready_without_execution=all(c['ok'] for c in checks if c['name']!='explicit_approval_present_for_activation')
    approved=checks[-1]['ok']
    packet={
        'ok':phase2_ready_without_execution,
        'approved_to_execute':approved,
        'generated_at':int(time.time()),
        'mode':'phase2_preflight_no_toggle_change',
        'checks':checks,
        'approval_packet':{
            'action':'enable_clara_admin_send_action_gate_enforcement',
            'required_phrase':'Autorizo ativar CLARA_ADMIN_SEND_ENFORCE_ACTION_GATE=1 na Clara agora',
            'required_approval_scope':'clara_enforcement_phase2',
            'risk':'Pode bloquear envios administrativos de follow-up se Approval Ledger não estiver correto; não deve afetar recepção de leads.',
            'expected_env':'CLARA_ADMIN_SEND_ENFORCE_ACTION_GATE=1',
            'must_not_do':['pausar Clara','desbloquear paciente','enviar WhatsApp real durante ativação']
        },
        'activation_steps_when_approved':[ 
            'registrar approval no Approval Ledger',
            'setar CLARA_ADMIN_SEND_ENFORCE_ACTION_GATE=1 no ambiente do zapi bridge',
            'restart controlado do zapi bridge',
            'validar /healthz',
            'rodar clara_action_gate_shadow.py --json',
            'rodar /admin/send dry_run em lead sintético e paciente bloqueado',
            'monitorar 30-60min logs sem envio bloqueado indevido'
        ],
        'rollback_steps':[ 
            'setar CLARA_ADMIN_SEND_ENFORCE_ACTION_GATE=0',
            'restart controlado do zapi bridge',
            'validar /healthz',
            'rodar clara_action_gate_shadow.py --json',
            'registrar evidência no Workflow Runner/RC-25'
        ],
        'execution_performed':False,
        'recommendation':'ready_for_explicit_approval' if phase2_ready_without_execution and not approved else ('approval_present_but_manual_activation_required' if approved else 'fix_preflight_before_approval')
    }
    DEL.mkdir(exist_ok=True)
    (DEL/'clara-enforcement-phase2-preflight-latest.json').write_text(json.dumps(packet,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(packet,ensure_ascii=False,indent=2))
    raise SystemExit(0 if packet['ok'] else 2)
if __name__=='__main__': main()
