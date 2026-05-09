#!/usr/bin/env python3
"""Generate read-only approval queue from Agent OS preflight artifacts.
No approvals are created, edited or executed.
"""
import argparse, json, time, html
from pathlib import Path
DEL=Path('/root/deliverables')
SOURCES=[
 ('clara_phase2','/root/deliverables/clara-enforcement-phase2-preflight-latest.json'),
 ('pedro_omie_write','/root/deliverables/pedro-omie-write-preflight-latest.json'),
 ('offsite_backup','/root/deliverables/agent-os-offsite-backup-latest.json'),
]

def load(p):
    try: return json.load(open(p))
    except Exception as e: return {'ok':False,'missing':True,'error':str(e)}

def item_clara(d):
    ap=d.get('approval_packet',{})
    status_doc=load('/root/deliverables/clara-enforcement-phase2-status-latest.json')
    activated=bool(status_doc.get('ok'))
    return {'id':'clara_phase2_enforcement','title':'Ativar Clara Action Gate Enforcement','status':'activated' if activated else ('pending_explicit_approval' if d.get('ok') and not d.get('approved_to_execute') else 'not_ready'),'risk':'atendimento externo / bloqueio indevido de follow-up administrativo','required_phrase':ap.get('required_phrase'),'scope':ap.get('required_approval_scope'),'preflight_ok':d.get('ok'), 'execution_performed':activated, 'source':'clara-enforcement-phase2-preflight-latest.json'}

def item_pedro(d):
    ap=d.get('approval_packet',{})
    return {'id':'pedro_omie_write','title':'Pedro executar escrita real no Omie','status':'pending_payload_and_explicit_approval' if d.get('ok') and not d.get('approved_to_execute') else 'not_ready','risk':'escrita financeira real no Omie','required_phrase':ap.get('required_phrase'),'scope':ap.get('required_scope'),'preflight_ok':d.get('ok'), 'execution_performed':d.get('execution_performed'), 'source':'pedro-omie-write-preflight-latest.json'}

def item_offsite(d):
    export_doc=load('/root/deliverables/offsite-local-mirror-export-result.json')
    exported=bool(export_doc.get('exported'))
    return {'id':'offsite_backup_export','title':'Exportar backup Agent OS para destino externo/local mirror','status':'executed_local_mirror' if exported else ('pending_destination_and_approval' if d.get('ok') and not d.get('exported') else 'not_ready'),'risk':'movimentação de artefatos para fora do runtime local','required_phrase':'Autorizo exportar o backup Agent OS para este destino aprovado agora','scope':'offsite_backup_export','preflight_ok':d.get('ok'), 'execution_performed':exported or d.get('exported'), 'source':'agent-os-offsite-backup-latest.json'}

def render(items,out):
    rows=''.join(f"<tr><td>{html.escape(i['id'])}</td><td>{html.escape(i['title'])}</td><td>{html.escape(i['status'])}</td><td>{html.escape(str(i.get('preflight_ok')))}</td><td>{html.escape(str(i.get('execution_performed')))}</td><td><code>{html.escape(str(i.get('required_phrase')))}</code></td><td>{html.escape(str(i.get('risk')))}</td></tr>" for i in items)
    doc=f"""<!doctype html><html><head><meta charset='utf-8'><title>Fila de Aprovações IVS Agent OS</title><style>body{{font-family:Arial;margin:24px}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ddd;padding:8px;vertical-align:top}}th{{background:#111;color:white}}code{{white-space:pre-wrap}}</style></head><body><h1>Fila de Aprovações IVS Agent OS</h1><p>Read-only. Este console não registra aprovação, não altera produção e não executa ação sensível.</p><table><thead><tr><th>ID</th><th>Ação</th><th>Status</th><th>Preflight</th><th>Executado</th><th>Frase exigida</th><th>Risco</th></tr></thead><tbody>{rows}</tbody></table></body></html>"""
    Path(out).write_text(doc,encoding='utf-8')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--json-out',default='/root/deliverables/approval-queue-ivs-agent-os.json'); ap.add_argument('--html-out',default='/root/deliverables/approval-queue-ivs-agent-os.html'); ap.add_argument('--json',action='store_true'); args=ap.parse_args()
    raw={k:load(p) for k,p in SOURCES}
    items=[item_clara(raw['clara_phase2']), item_pedro(raw['pedro_omie_write']), item_offsite(raw['offsite_backup'])]
    totals={'items':len(items),'pending':sum(1 for i in items if i['status'].startswith('pending')),'executed':sum(1 for i in items if i.get('execution_performed'))}
    report={'ok':True,'generated_at':int(time.time()),'mode':'read_only_approval_queue_no_execution','totals':totals,'items':items,'blocked_by_design':['does not write Approval Ledger','does not enable Clara enforcement','does not call Omie','does not export backup']}
    Path(args.json_out).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    render(items,args.html_out)
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
