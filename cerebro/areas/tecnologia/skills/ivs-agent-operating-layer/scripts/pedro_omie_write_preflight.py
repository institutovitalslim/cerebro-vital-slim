#!/usr/bin/env python3
"""Pedro/Omie guarded write preflight.
Does not call Omie. Validates guards, approval requirements, credential placeholders and rollback/evidence plan.
"""
import argparse, json, os, subprocess, time
from pathlib import Path
BASE=Path('/root/.openclaw/workspace/skills/ivs-agent-operating-layer')
PEDRO=Path('/root/.openclaw/workspace/skills/pedro-controller-ivs')
DEL=Path('/root/deliverables')
ACTION_GATE=BASE/'scripts/action_gate.py'
PEDRO_GUARD=PEDRO/'scripts/pedro_omie_action_guard.py'
APPROVAL=BASE/'scripts/approval_ledger.py'

def run(cmd, timeout=30):
    try:
        p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=timeout)
        try: js=json.loads(p.stdout)
        except Exception: js={'raw':p.stdout[-2000:]}
        return {'ok':p.returncode==0,'exit_code':p.returncode,'json':js}
    except Exception as e: return {'ok':False,'error':str(e)}

def env_present(names):
    return {n: bool(os.environ.get(n)) for n in names}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--approval-id'); ap.add_argument('--json',action='store_true'); args=ap.parse_args()
    checks=[]
    checks.append({'name':'pedro_guard_exists','ok':PEDRO_GUARD.exists(),'detail':str(PEDRO_GUARD)})
    gate_no=run(['python3',str(ACTION_GATE),'--agent','pedro-controller-ivs','--action','omie_write','--sensitivity','financial'])
    gj=gate_no.get('json',{}) if isinstance(gate_no.get('json'),dict) else {}
    blocked = (not gate_no.get('ok')) or gj.get('final') in {'BLOCK_APPROVAL_REQUIRED','BLOCKED_BY_POLICY','BLOCK_FORBIDDEN'}
    checks.append({'name':'action_gate_blocks_without_approval','ok':bool(blocked),'detail':gate_no})
    pg=run(['python3',str(PEDRO_GUARD),'--action','omie_write','--json']) if PEDRO_GUARD.exists() else {'ok':False,'error':'missing guard'}
    pgj=pg.get('json',{}) if isinstance(pg.get('json'),dict) else {}
    guard_blocked = (not pg.get('ok')) or pgj.get('guard')=='blocked' or pgj.get('final') in {'BLOCK_APPROVAL_REQUIRED','BLOCKED_BY_POLICY'}
    checks.append({'name':'pedro_guard_blocks_without_approval','ok':bool(guard_blocked),'detail':pg})
    creds=env_present(['OMIE_APP_KEY','OMIE_APP_SECRET'])
    checks.append({'name':'omie_credentials_not_required_for_preflight','ok':True,'detail':{'present_masked':creds}})
    approval_status={'ok':False,'reason':'not_supplied'}
    if args.approval_id:
        approval_status=run(['python3',str(APPROVAL),'check','--approval-id',args.approval_id,'--json'])
    checks.append({'name':'explicit_approval_present_for_write','ok':bool(args.approval_id and approval_status.get('ok')),'detail':approval_status})
    preflight_ok=all(c['ok'] for c in checks if c['name']!='explicit_approval_present_for_write')
    approved=checks[-1]['ok']
    report={
        'ok':preflight_ok,
        'approved_to_execute':approved,
        'execution_performed':False,
        'generated_at':int(time.time()),
        'mode':'pedro_omie_guarded_write_preflight_no_omie_call',
        'checks':checks,
        'approval_packet':{
            'action':'pedro_omie_write',
            'required_phrase':'Autorizo Pedro executar escrita Omie com este payload aprovado agora',
            'required_scope':'pedro_omie_write',
            'payload_requirements':['tipo de operação', 'valor/cliente/documento quando aplicável', 'idempotency key', 'rollback/manual correction plan'],
            'risk':'Escrita financeira real no Omie; pode gerar cobrança/lançamento incorreto se payload estiver errado.'
        },
        'activation_steps_when_approved':['registrar approval no Approval Ledger','validar payload e idempotency key','rodar Pedro/Omie guard com approval','executar conector Omie apenas se guard liberar','registrar resposta Omie redigida','gerar RC-25'],
        'rollback_steps':['não há rollback automático universal em financeiro','se escrita indevida, acionar Pedro/Tiaro para correção manual no Omie','registrar ocorrência e bloqueio preventivo do payload'],
        'recommendation':'ready_for_explicit_approval_and_credential_review' if preflight_ok and not approved else ('approval_present_but_manual_payload_review_required' if approved else 'fix_preflight')
    }
    DEL.mkdir(exist_ok=True); (DEL/'pedro-omie-write-preflight-latest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2)); raise SystemExit(0 if report['ok'] else 2)
if __name__=='__main__': main()
