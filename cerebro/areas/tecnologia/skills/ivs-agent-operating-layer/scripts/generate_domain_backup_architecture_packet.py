#!/usr/bin/env python3
"""Read-only architecture packet for using IVS domain/subdomain with Agent OS backup/cockpit. No DNS changes, no hosting changes."""
import argparse,json,time,html,subprocess
from pathlib import Path
DEL=Path('/root/deliverables')
DOMAIN='institutovitalslim.com.br'
WWW='www.institutovitalslim.com.br'

def dig(name):
    try:
        out=subprocess.check_output(['getent','hosts',name],text=True,stderr=subprocess.STDOUT,timeout=10)
        return out.strip()
    except Exception as e:
        return ''

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--json',action='store_true'); args=ap.parse_args()
    options=[
      {'id':'recommended_private_backup','subdomain':'backup.institutovitalslim.com.br','purpose':'endpoint privado para backup externo ou gateway reverso autenticado','public_access':'não','notes':'não hospedar tarball publicamente; usar auth forte, allowlist/VPN ou storage privado atrás do subdomínio'},
      {'id':'operations_cockpit','subdomain':'ops.institutovitalslim.com.br','purpose':'cockpit protegido do Agent OS','public_access':'não, apenas via token + allowlist/VPN','notes':'cockpit atual deve continuar local até proxy seguro estar pronto'},
      {'id':'status_readonly','subdomain':'status.institutovitalslim.com.br','purpose':'status sanitizado/read-only, sem dados sensíveis','public_access':'possível','notes':'somente métricas agregadas; sem backups, tokens, pacientes ou logs'},
      {'id':'not_recommended_public_backup','subdomain':'www.institutovitalslim.com.br/backups','purpose':'servir backups pelo site principal','public_access':'sim','notes':'não recomendado: risco de exposição de dados e indexação'}]
    report={'ok':True,'generated_at':int(time.time()),'mode':'domain_backup_architecture_packet_no_dns_change','domain':DOMAIN,'www_lookup':dig(WWW),'recommendation':'usar subdomínio separado backup.institutovitalslim.com.br apontando para storage/proxy privado; não usar www para hospedar arquivos de backup','options':options,'required_inputs':['provedor DNS atual do domínio','acesso para criar CNAME/A record','destino privado real do backup/storage','política de autenticação: VPN/allowlist/token','confirmação de que nada será público/indexável'],'blocked_by_design':['não altera DNS','não cria subdomínio','não publica backup','não abre cockpit publicamente','não grava credenciais']}
    DEL.mkdir(parents=True,exist_ok=True)
    (DEL/'domain-backup-architecture-packet.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    rows=''.join(f"<tr><td>{html.escape(o['id'])}</td><td>{html.escape(o['subdomain'])}</td><td>{html.escape(o['purpose'])}</td><td>{html.escape(o['public_access'])}</td><td>{html.escape(o['notes'])}</td></tr>" for o in options)
    doc=f"""<!doctype html><html><head><meta charset='utf-8'><title>IVS Domain Backup Architecture</title><style>body{{font-family:Arial;margin:24px}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ddd;padding:8px;vertical-align:top}}th{{background:#111;color:white}}</style></head><body><h1>IVS Domain Backup Architecture</h1><p>Read-only. Não altera DNS e não publica backup.</p><p><b>Recomendação:</b> usar <code>backup.institutovitalslim.com.br</code> privado, não o <code>www</code>.</p><table><tr><th>ID</th><th>Subdomínio</th><th>Uso</th><th>Acesso público</th><th>Notas</th></tr>{rows}</table></body></html>"""
    (DEL/'domain-backup-architecture-packet.html').write_text(doc,encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
