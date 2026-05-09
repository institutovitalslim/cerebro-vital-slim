#!/usr/bin/env python3
"""Generate read-only intake packet for external/rclone backup destination. No rclone call, no credential write."""
import argparse,json,time,html,re
from pathlib import Path
DEL=Path('/root/deliverables')
REMOTE_RE=re.compile(r'^[A-Za-z0-9_.-]+:[A-Za-z0-9_./=-]+$')

def validate(dest):
    findings=[]
    if not dest:
        findings.append({'severity':'LOW','code':'destination_missing','detail':'fornecer destino rclone, ex: remote:ivs-agent-os-backups'})
    elif not REMOTE_RE.match(dest):
        findings.append({'severity':'HIGH','code':'destination_format_invalid','expected':'remote:path'})
    if dest and any(x in dest.lower() for x in ['token','secret','key=','password']):
        findings.append({'severity':'HIGH','code':'possible_secret_in_destination'})
    return {'ok':not any(f['severity']=='HIGH' for f in findings),'findings':findings}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--destination',default=''); ap.add_argument('--json',action='store_true'); args=ap.parse_args()
    v=validate(args.destination)
    packet={'ok':v['ok'],'generated_at':int(time.time()),'mode':'external_backup_intake_packet_no_export','destination':args.destination or None,'destination_validation':v,'required_inputs':[{'field':'rclone_remote_name','example':'remote','required':True},{'field':'remote_path','example':'ivs-agent-os-backups','required':True},{'field':'credential_review','description':'confirmar que rclone já está configurado fora do cérebro e sem versionar token','required':True},{'field':'retention_policy','example':'manter últimos 7 diários + 4 semanais','required':True},{'field':'approval_phrase','example':'Autorizo exportar backup Agent OS via rclone para remote:ivs-agent-os-backups agora','required':True}], 'blocked_by_design':['não chama rclone','não exporta backup','não cria credencial','não grava token no cérebro','não registra approval']}
    DEL.mkdir(parents=True,exist_ok=True)
    (DEL/'external-backup-intake-packet.json').write_text(json.dumps(packet,ensure_ascii=False,indent=2),encoding='utf-8')
    rows=''.join(f"<tr><td>{html.escape(i['field'])}</td><td>{html.escape(str(i.get('required')))}</td><td>{html.escape(str(i.get('example') or i.get('description')))}</td></tr>" for i in packet['required_inputs'])
    doc=f"""<!doctype html><html><head><meta charset='utf-8'><title>External Backup Intake</title><style>body{{font-family:Arial;margin:24px}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ddd;padding:8px;vertical-align:top}}th{{background:#111;color:white}}</style></head><body><h1>External/Rclone Backup Intake</h1><p>Read-only. Não chama rclone, não exporta e não grava credenciais.</p><table><tr><th>Campo</th><th>Obrigatório</th><th>Exemplo/Descrição</th></tr>{rows}</table></body></html>"""
    (DEL/'external-backup-intake-packet.html').write_text(doc,encoding='utf-8')
    print(json.dumps(packet,ensure_ascii=False,indent=2))
    raise SystemExit(0 if packet['ok'] else 2)
if __name__=='__main__': main()
