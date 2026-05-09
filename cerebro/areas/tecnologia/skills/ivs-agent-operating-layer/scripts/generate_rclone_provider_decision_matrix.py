#!/usr/bin/env python3
"""Read-only provider decision matrix for rclone external backup. No remote creation, no credentials, no export."""
import argparse,json,time,html
from pathlib import Path
DEL=Path('/root/deliverables')
OPTIONS=[
 {'id':'s3_compatible','rclone_type':'s3','fit':'recommended','why':'bom para backup versionado, lifecycle/retention, baixo acoplamento','requires':['bucket','endpoint/region','access_key_id e secret configurados fora do cérebro'],'test':'rclone lsd remote:','destination':'remote:ivs-agent-os-backups'},
 {'id':'backblaze_b2','rclone_type':'b2','fit':'recommended','why':'custo previsível para backup frio','requires':['account id','application key fora do cérebro','bucket'],'test':'rclone lsd remote:','destination':'remote:ivs-agent-os-backups'},
 {'id':'sftp','rclone_type':'sftp','fit':'acceptable','why':'simples se já houver servidor backup','requires':['host','user','ssh key fora do cérebro','path'],'test':'rclone lsd remote:','destination':'remote:/ivs-agent-os-backups'},
 {'id':'google_drive','rclone_type':'drive','fit':'acceptable_with_care','why':'fácil, mas OAuth/quotas e organização exigem cuidado','requires':['OAuth em terminal seguro','shared drive/pasta'],'test':'rclone lsd remote:','destination':'remote:ivs-agent-os-backups'},
 {'id':'webdav','rclone_type':'webdav','fit':'fallback','why':'útil com Nextcloud/servidor existente, menos ideal para retenção pesada','requires':['url','user','password/app token fora do cérebro'],'test':'rclone lsd remote:','destination':'remote:ivs-agent-os-backups'}
]

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--recommended',default='s3_compatible'); ap.add_argument('--json',action='store_true'); args=ap.parse_args()
 rec=next((o for o in OPTIONS if o['id']==args.recommended), OPTIONS[0])
 report={'ok':True,'generated_at':int(time.time()),'mode':'rclone_provider_decision_matrix_no_credentials_no_export','recommended':rec,'options':OPTIONS,'proposed_remote_name':'remote','proposed_retention':'7 daily + 4 weekly + 6 monthly','required_decision':'Tiaro escolher provider/conta antes de configurar credenciais','blocked_by_design':['não cria remote','não grava token','não chama rclone config','não exporta backup','não registra approval']}
 DEL.mkdir(parents=True,exist_ok=True)
 (DEL/'rclone-provider-decision-matrix.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 rows=''.join(f"<tr><td>{html.escape(o['id'])}</td><td>{html.escape(o['rclone_type'])}</td><td>{html.escape(o['fit'])}</td><td>{html.escape(o['why'])}</td><td>{html.escape(', '.join(o['requires']))}</td><td><code>{html.escape(o['destination'])}</code></td></tr>" for o in OPTIONS)
 doc=f"""<!doctype html><html><head><meta charset='utf-8'><title>Rclone Provider Decision Matrix</title><style>body{{font-family:Arial;margin:24px}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ddd;padding:8px;vertical-align:top}}th{{background:#111;color:white}}code{{white-space:pre-wrap}}</style></head><body><h1>Rclone Provider Decision Matrix</h1><p>Read-only. Não cria remote, não grava credenciais e não exporta.</p><p>Recomendado: <b>{html.escape(rec['id'])}</b></p><table><tr><th>ID</th><th>Tipo rclone</th><th>Fit</th><th>Por quê</th><th>Requer</th><th>Destino</th></tr>{rows}</table></body></html>"""
 (DEL/'rclone-provider-decision-matrix.html').write_text(doc,encoding='utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
