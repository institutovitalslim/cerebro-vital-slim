#!/usr/bin/env python3
"""Read-only packet for rclone remote setup. No credential write, no rclone config create, no export."""
import argparse,json,time,html,shutil,subprocess,re
from pathlib import Path
DEL=Path('/root/deliverables')
SUPPORTED=['s3','drive','b2','sftp','webdav']

def list_remotes():
    if not shutil.which('rclone'):
        return {'installed':False,'remotes':[]}
    out=subprocess.getoutput('rclone listremotes 2>/dev/null')
    return {'installed':True,'remotes':[x.strip().rstrip(':') for x in out.splitlines() if x.strip() and not x.startswith('<')]}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--remote-name',default='remote'); ap.add_argument('--remote-type',default=''); ap.add_argument('--json',action='store_true'); args=ap.parse_args()
    findings=[]
    if not re.match(r'^[A-Za-z0-9_.-]{2,40}$', args.remote_name): findings.append({'severity':'HIGH','code':'invalid_remote_name'})
    if args.remote_type and args.remote_type not in SUPPORTED: findings.append({'severity':'MEDIUM','code':'remote_type_not_in_recommended_list','supported':SUPPORTED})
    rc=list_remotes()
    if not rc['installed']: findings.append({'severity':'HIGH','code':'rclone_not_installed'})
    packet={'ok':not any(f['severity']=='HIGH' for f in findings),'generated_at':int(time.time()),'mode':'rclone_remote_intake_no_credentials_no_export','remote_name':args.remote_name,'remote_type':args.remote_type or None,'rclone':rc,'recommended_remote_types':SUPPORTED,'required_inputs':[{'field':'remote_type','examples':SUPPORTED,'required':True},{'field':'provider/account','description':'qual storage será usado; sem colar tokens no Telegram/cérebro','required':True},{'field':'credential_setup_method','examples':['rclone config no terminal seguro','env vars fora do cérebro','arquivo config fora do repositório'],'required':True},{'field':'test_command_expected','example':f'rclone lsd {args.remote_name}:','required':True},{'field':'destination_path','example':f'{args.remote_name}:ivs-agent-os-backups','required':True}], 'safe_commands_after_credentials_configured':[f'rclone listremotes',f'rclone lsd {args.remote_name}:',f'rclone copy --dry-run /root/agent-os-offsite/ivs-agent-os {args.remote_name}:ivs-agent-os-backups'], 'blocked_by_design':['não executa rclone config create','não pede token no chat','não grava credencial no cérebro','não executa rclone copy real','não registra approval'], 'findings':findings}
    DEL.mkdir(parents=True,exist_ok=True)
    (DEL/'rclone-remote-intake-packet.json').write_text(json.dumps(packet,ensure_ascii=False,indent=2),encoding='utf-8')
    rows=''.join(f"<tr><td>{html.escape(i['field'])}</td><td>{html.escape(str(i.get('required')))}</td><td>{html.escape(str(i.get('examples') or i.get('example') or i.get('description')))}</td></tr>" for i in packet['required_inputs'])
    doc=f"""<!doctype html><html><head><meta charset='utf-8'><title>Rclone Remote Intake</title><style>body{{font-family:Arial;margin:24px}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ddd;padding:8px;vertical-align:top}}th{{background:#111;color:white}}code{{white-space:pre-wrap}}</style></head><body><h1>Rclone Remote Intake</h1><p>Read-only. Não cria remote, não grava credencial, não exporta.</p><table><tr><th>Campo</th><th>Obrigatório</th><th>Exemplo/Descrição</th></tr>{rows}</table><h2>Comandos seguros depois da configuração manual</h2><pre>{html.escape(chr(10).join(packet['safe_commands_after_credentials_configured']))}</pre></body></html>"""
    (DEL/'rclone-remote-intake-packet.html').write_text(doc,encoding='utf-8')
    print(json.dumps(packet,ensure_ascii=False,indent=2)); raise SystemExit(0 if packet['ok'] else 2)
if __name__=='__main__': main()
