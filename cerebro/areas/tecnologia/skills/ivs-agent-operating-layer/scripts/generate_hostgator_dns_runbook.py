#!/usr/bin/env python3
"""Read-only HostGator DNS runbook for IVS subdomains. No DNS changes."""
import argparse,json,time,html
from pathlib import Path
DEL=Path('/root/deliverables')
DOMAIN='institutovitalslim.com.br'

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--json',action='store_true'); args=ap.parse_args()
    records=[
      {'name':'backup','fqdn':'backup.institutovitalslim.com.br','type':'CNAME','target':'<storage-ou-proxy-privado>','ttl':'300 ou automático','purpose':'backup privado / endpoint autenticado','public':'não'},
      {'name':'ops','fqdn':'ops.institutovitalslim.com.br','type':'A ou CNAME','target':'<proxy-protegido-ou-vpn>','ttl':'300 ou automático','purpose':'cockpit protegido futuro','public':'não'},
      {'name':'status','fqdn':'status.institutovitalslim.com.br','type':'CNAME','target':'<hosting-status-sanitizado>','ttl':'300 ou automático','purpose':'status público sanitizado opcional','public':'sim, sem dados sensíveis'}]
    steps=[
      'Entrar no painel HostGator da conta do domínio.',
      'Abrir gerenciamento de DNS/Zona DNS do domínio institutovitalslim.com.br.',
      'Criar apenas o subdomínio escolhido; recomendação inicial: backup.institutovitalslim.com.br.',
      'Usar CNAME se houver storage/proxy com hostname; usar A record apenas se houver IP fixo.',
      'Não apontar backup para www nem diretório público do site.',
      'Ativar TLS no destino antes de uso operacional.',
      'Testar resolução DNS e acesso autenticado.',
      'Só depois rodar export rclone/proxy com approval explícito.'
    ]
    report={'ok':True,'generated_at':int(time.time()),'mode':'hostgator_dns_runbook_no_dns_change','domain':DOMAIN,'dns_provider':'HostGator','recommended_first_record':records[0],'records':records,'steps':steps,'guardrails':['não altera DNS automaticamente','não publica backup','não usa www para backup','não expõe cockpit sem auth','não cria credencial'],'inputs_still_needed':['target real do CNAME/A para backup privado','confirmação de TLS/auth no destino','aprovação explícita antes de qualquer export externo']}
    DEL.mkdir(parents=True,exist_ok=True)
    (DEL/'hostgator-dns-runbook.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    rows=''.join(f"<tr><td>{html.escape(r['fqdn'])}</td><td>{html.escape(r['type'])}</td><td><code>{html.escape(r['target'])}</code></td><td>{html.escape(r['purpose'])}</td><td>{html.escape(r['public'])}</td></tr>" for r in records)
    li=''.join(f'<li>{html.escape(s)}</li>' for s in steps)
    doc=f"""<!doctype html><html><head><meta charset='utf-8'><title>HostGator DNS Runbook IVS</title><style>body{{font-family:Arial;margin:24px}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ddd;padding:8px;vertical-align:top}}th{{background:#111;color:white}}code{{white-space:pre-wrap}}</style></head><body><h1>HostGator DNS Runbook — {DOMAIN}</h1><p>Read-only. Não altera DNS.</p><h2>Registros propostos</h2><table><tr><th>FQDN</th><th>Tipo</th><th>Target</th><th>Uso</th><th>Público?</th></tr>{rows}</table><h2>Passos</h2><ol>{li}</ol></body></html>"""
    (DEL/'hostgator-dns-runbook.html').write_text(doc,encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
