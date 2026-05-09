#!/usr/bin/env python3
"""Generate read-only Agent OS operations runbook and next-actions matrix."""
import argparse,json,time,html
from pathlib import Path
DEL=Path('/root/deliverables')

def load(p):
    try: return json.load(open(p))
    except Exception as e: return {'ok':False,'error':str(e),'missing':True}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--json',action='store_true'); args=ap.parse_args()
    queue=load('/root/deliverables/approval-queue-ivs-agent-os.json')
    readiness=load('/root/deliverables/agent-os-readiness-scorecard.json')
    clara=load('/root/deliverables/clara-phase2-watch-latest.json')
    offsite=load('/root/deliverables/offsite-local-mirror-export-verify.json')
    pedro=load('/root/deliverables/pedro-omie-payload-validator-latest.json')
    runbook={
      'ok': True,
      'generated_at': int(time.time()),
      'mode': 'read_only_agent_os_operations_runbook',
      'current_state': {
        'readiness': {'status': readiness.get('status'), 'score': readiness.get('score')},
        'clara_phase2_watch_ok': clara.get('ok'),
        'offsite_local_mirror_verified': offsite.get('ok'),
        'pedro_payload_validator_ready': pedro.get('ok'),
        'approval_queue': queue.get('totals')
      },
      'operational_protocols': [
        {'area':'Clara Phase 2','status':'active_watch','do':'monitorar, reportar HIGH/MEDIUM relevante','do_not':'pausar Clara sem ordem explícita; desbloquear paciente; enviar teste real'},
        {'area':'Offsite backup','status':'local_mirror_done','do':'manter cópia local verificada; próximo externo só com destino/credencial revisados','do_not':'usar rclone sem revisão; versionar token; exportar para destino não aprovado'},
        {'area':'Pedro/Omie','status':'payload_required','do':'coletar operation_type, payload_json, business_reason, idempotency_key','do_not':'chamar Omie, emitir/baixar/alterar financeiro sem payload+approval'},
        {'area':'Cockpit/CI','status':'ready','do':'rodar CI/readiness antes/depois de mudança','do_not':'expor token; abrir cockpit publicamente'}
      ],
      'next_action_matrix': [
        {'priority':1,'action':'Finalizar janela Clara 24h','requires':'aguardar checkpoints; nenhum approval','risk':'baixo'},
        {'priority':2,'action':'Coletar payload real Pedro/Omie','requires':'dados concretos da operação','risk':'alto se executar; baixo enquanto read-only'},
        {'priority':3,'action':'Definir backup externo real','requires':'destino rclone/storage + revisão credencial + approval','risk':'médio/alto'},
        {'priority':4,'action':'Transformar Approval Console em UI interativa','requires':'auth forte + token policy + auditoria','risk':'médio'}
      ],
      'blocked_until_input': ['Pedro/Omie write real: payload + idempotency + approval', 'Backup externo/rclone: destino + credencial revisada + approval'],
      'actions_taken': [],
      'guardrails': ['read-only','no patient unlock','no Omie call','no external export','no credential creation']
    }
    DEL.mkdir(parents=True,exist_ok=True)
    (DEL/'agent-os-operations-runbook.json').write_text(json.dumps(runbook,ensure_ascii=False,indent=2),encoding='utf-8')
    rows=''.join(f"<tr><td>{html.escape(str(x['priority']))}</td><td>{html.escape(x['action'])}</td><td>{html.escape(x['requires'])}</td><td>{html.escape(x['risk'])}</td></tr>" for x in runbook['next_action_matrix'])
    prot=''.join(f"<tr><td>{html.escape(p['area'])}</td><td>{html.escape(p['status'])}</td><td>{html.escape(p['do'])}</td><td>{html.escape(p['do_not'])}</td></tr>" for p in runbook['operational_protocols'])
    doc=f"""<!doctype html><html><head><meta charset='utf-8'><title>IVS Agent OS — Operations Runbook</title><style>body{{font-family:Arial;margin:24px}}table{{border-collapse:collapse;width:100%;margin:16px 0}}td,th{{border:1px solid #ddd;padding:8px;vertical-align:top}}th{{background:#111;color:white}}</style></head><body><h1>IVS Agent OS — Operations Runbook</h1><p>Read-only. Não executa ação sensível.</p><h2>Protocolos</h2><table><tr><th>Área</th><th>Status</th><th>Fazer</th><th>Não fazer</th></tr>{prot}</table><h2>Próximas ações</h2><table><tr><th>Prioridade</th><th>Ação</th><th>Requer</th><th>Risco</th></tr>{rows}</table></body></html>"""
    (DEL/'agent-os-operations-runbook.html').write_text(doc,encoding='utf-8')
    print(json.dumps(runbook,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
