#!/usr/bin/env python3
"""Generate a read-only destination decision packet for IVS Agent OS offsite backup.
No export, no credentials, no approval write.
"""
import argparse, json, time, html
from pathlib import Path
DEL=Path('/root/deliverables')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--json',action='store_true'); args=ap.parse_args()
    options=[
        {'id':'local_mirror','label':'Local mirror controlado','destination_example':'/root/agent-os-offsite/ivs-agent-os','requires':'approval_id + --apply + destino sob /root/agent-os-offsite','risk':'baixo/médio: cópia local no servidor, sem saída externa','recommendation':'bom primeiro passo para testar restore sem expor dados'},
        {'id':'rclone','label':'Storage externo via rclone','destination_example':'remote:ivs-agent-os-backups','requires':'rclone configurado + revisão de credenciais + approval explícito','risk':'médio/alto: exporta artefatos para fora do runtime','recommendation':'usar depois que destino e retenção forem definidos'},
        {'id':'defer','label':'Manter readiness somente','destination_example':None,'requires':'nenhuma ação','risk':'baixo: sem backup offsite real','recommendation':'seguro, mas não fecha DR offsite'}
    ]
    report={'ok':True,'generated_at':int(time.time()),'mode':'read_only_offsite_destination_decision_packet','decision_required':'Escolher destino e autorizar explicitamente antes de qualquer exportação','options':options,'blocked_by_design':['não exporta backup','não cria credencial','não escreve Approval Ledger','não chama rclone','não copia para destino']}
    DEL.mkdir(parents=True,exist_ok=True)
    (DEL/'offsite-destination-decision-packet.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    rows=''.join(f"<tr><td>{html.escape(o['id'])}</td><td>{html.escape(o['label'])}</td><td><code>{html.escape(str(o.get('destination_example')))}</code></td><td>{html.escape(o['requires'])}</td><td>{html.escape(o['risk'])}</td><td>{html.escape(o['recommendation'])}</td></tr>" for o in options)
    doc=f"""<!doctype html><html><head><meta charset='utf-8'><title>Offsite Backup — Decisão de Destino</title><style>body{{font-family:Arial;margin:24px}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ddd;padding:8px;vertical-align:top}}th{{background:#111;color:white}}code{{white-space:pre-wrap}}</style></head><body><h1>Offsite Backup — Decisão de Destino</h1><p>Read-only. Não exporta, não cria credencial e não registra aprovação.</p><table><thead><tr><th>ID</th><th>Opção</th><th>Exemplo destino</th><th>Requer</th><th>Risco</th><th>Recomendação</th></tr></thead><tbody>{rows}</tbody></table></body></html>"""
    (DEL/'offsite-destination-decision-packet.html').write_text(doc,encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
