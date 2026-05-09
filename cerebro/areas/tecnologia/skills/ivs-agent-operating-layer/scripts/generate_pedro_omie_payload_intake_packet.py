#!/usr/bin/env python3
"""Generate read-only payload intake packet for Pedro/Omie guarded writes. No Omie call."""
import argparse,json,time,html
from pathlib import Path
DEL=Path('/root/deliverables')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--json',action='store_true'); args=ap.parse_args()
    packet={
      'ok':True,'generated_at':int(time.time()),'mode':'pedro_omie_write_payload_intake_packet_no_execution',
      'agent':'pedro-controller-ivs','action':'omie_write','approval_required':True,'execution_performed':False,
      'required_inputs':[{'field':'operation_type','examples':['emitir_boleto','baixar_titulo','criar_conta_receber','atualizar_cliente'],'required':True},{'field':'payload_json','description':'payload exato que seria enviado ao Omie, sem credenciais','required':True},{'field':'business_reason','description':'motivo operacional/financeiro','required':True},{'field':'idempotency_key','description':'chave única para evitar duplicidade','required':True},{'field':'approval_phrase','description':'aprovação explícita depois da revisão do payload','required':True}],
      'required_phrase_template':'Autorizo Pedro executar Omie write <operation_type> com payload revisado e idempotency_key <idempotency_key> agora',
      'blocked_by_design':['não chama Omie','não grava financeiro','não baixa título','não emite boleto/NF','não altera cliente','não usa credenciais']}
    DEL.mkdir(parents=True,exist_ok=True)
    (DEL/'pedro-omie-write-payload-intake-packet.json').write_text(json.dumps(packet,ensure_ascii=False,indent=2),encoding='utf-8')
    rows=''.join(f"<tr><td>{html.escape(i['field'])}</td><td>{html.escape(str(i.get('required')))}</td><td>{html.escape(str(i.get('description') or i.get('examples')))}</td></tr>" for i in packet['required_inputs'])
    doc=f"""<!doctype html><html><head><meta charset='utf-8'><title>Pedro/Omie Write Payload Intake</title><style>body{{font-family:Arial;margin:24px}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ddd;padding:8px}}th{{background:#111;color:white}}code{{white-space:pre-wrap}}</style></head><body><h1>Pedro/Omie Write — Payload Intake</h1><p>Read-only. Não chama Omie e não executa escrita financeira.</p><table><thead><tr><th>Campo</th><th>Obrigatório</th><th>Descrição</th></tr></thead><tbody>{rows}</tbody></table><p>Frase modelo: <code>{html.escape(packet['required_phrase_template'])}</code></p></body></html>"""
    (DEL/'pedro-omie-write-payload-intake-packet.html').write_text(doc,encoding='utf-8')
    print(json.dumps(packet,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
