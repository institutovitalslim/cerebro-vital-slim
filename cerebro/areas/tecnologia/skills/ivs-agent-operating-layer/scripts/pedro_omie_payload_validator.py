#!/usr/bin/env python3
"""Read-only validator/templates for Pedro/Omie guarded write payloads. No Omie call."""
import argparse,json,time,hashlib,re
from pathlib import Path
DEL=Path('/root/deliverables')
OPS={
 'emitir_boleto': ['cliente_id','valor','vencimento','descricao'],
 'baixar_titulo': ['titulo_id','data_baixa','valor_baixado','forma_pagamento'],
 'criar_conta_receber': ['cliente_id','valor','vencimento','categoria','descricao'],
 'atualizar_cliente': ['cliente_id','campos']
}
OPTIONAL={'emitir_boleto':['observacao','numero_pedido'],'baixar_titulo':['observacao'],'criar_conta_receber':['observacao'],'atualizar_cliente':['motivo']}

def template(op):
    req=OPS[op]
    obj={k:('<preencher>' if k not in ('valor','valor_baixado','campos') else (0 if k!='campos' else {'campo':'valor'})) for k in req}
    return {'operation_type':op,'business_reason':'<motivo operacional>','idempotency_key':f'ivs-{op}-YYYYMMDD-001','payload_json':obj}

def validate(doc):
    findings=[]
    op=doc.get('operation_type')
    payload=doc.get('payload_json') or doc.get('payload') or {}
    if op not in OPS: findings.append({'severity':'HIGH','code':'operation_type_invalid','allowed':list(OPS)})
    if not isinstance(payload,dict): findings.append({'severity':'HIGH','code':'payload_not_object'})
    if op in OPS and isinstance(payload,dict):
        for k in OPS[op]:
            if k not in payload or payload.get(k) in ('',None,'<preencher>'):
                findings.append({'severity':'HIGH','code':'missing_required_field','field':k})
    idem=doc.get('idempotency_key')
    if not idem or not re.match(r'^[a-zA-Z0-9_.:-]{8,120}$',str(idem)):
        findings.append({'severity':'HIGH','code':'invalid_idempotency_key'})
    if not doc.get('business_reason') or doc.get('business_reason')=='<motivo operacional>':
        findings.append({'severity':'MEDIUM','code':'business_reason_missing'})
    raw=json.dumps(payload,sort_keys=True,ensure_ascii=False)
    return {'ok':not any(f['severity']=='HIGH' for f in findings),'findings':findings,'payload_sha256':hashlib.sha256(raw.encode()).hexdigest(),'mode':'read_only_validation_no_omie_call','operation_type':op,'execution_performed':False}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--operation-type',choices=list(OPS)); ap.add_argument('--payload-file'); ap.add_argument('--templates',action='store_true'); ap.add_argument('--json',action='store_true'); args=ap.parse_args()
    if args.templates or not args.payload_file:
        report={'ok':True,'generated_at':int(time.time()),'mode':'pedro_omie_payload_templates_no_execution','templates':{op:template(op) for op in OPS},'blocked_by_design':['no Omie call','no credential use','no approval write']}
        if args.operation_type: report={'ok':True,'generated_at':int(time.time()),'mode':'pedro_omie_payload_template_no_execution','template':template(args.operation_type),'blocked_by_design':['no Omie call','no credential use','no approval write']}
    else:
        doc=json.load(open(args.payload_file))
        report=validate(doc); report['generated_at']=int(time.time()); report['source_file']=args.payload_file
    DEL.mkdir(parents=True,exist_ok=True)
    (DEL/'pedro-omie-payload-validator-latest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    raise SystemExit(0 if report.get('ok') else 2)
if __name__=='__main__': main()
