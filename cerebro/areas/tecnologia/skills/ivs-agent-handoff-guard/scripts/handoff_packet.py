#!/usr/bin/env python3
import argparse, json, time
from pathlib import Path
AGENTS={'maria-gerente':'Maria','clara-whatsapp':'Clara','agente-reels-intel':'João','pedro-controller-ivs':'Pedro','conselho-growth-vital-slim':'Conselho Growth','llm-council':'LLM Council'}
SENS={'internal','lead','patient','clinical','financial','marketing','tech'}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--from', dest='from_agent', required=True); ap.add_argument('--to', dest='to_agent', required=True)
    ap.add_argument('--subject', required=True); ap.add_argument('--context', required=True); ap.add_argument('--next-action', required=True)
    ap.add_argument('--sensitivity', choices=sorted(SENS), default='internal'); ap.add_argument('--deadline'); ap.add_argument('--evidence', action='append', default=[])
    ap.add_argument('--json-out'); ap.add_argument('--md-out'); ap.add_argument('--json', action='store_true')
    args=ap.parse_args(); findings=[]
    if args.from_agent not in AGENTS: findings.append({'severity':'MEDIUM','code':'unknown_from_agent','agent':args.from_agent})
    if args.to_agent not in AGENTS: findings.append({'severity':'MEDIUM','code':'unknown_to_agent','agent':args.to_agent})
    if args.to_agent=='clara-whatsapp' and args.sensitivity in ['patient','clinical']:
        findings.append({'severity':'HIGH','code':'clara_patient_or_clinical_handoff_requires_human_review','rule':'Clara não diagnostica/prescreve e não atende paciente externo como Maria.'})
    if args.sensitivity=='financial' and args.to_agent not in ['pedro-controller-ivs','maria-gerente']:
        findings.append({'severity':'MEDIUM','code':'financial_handoff_to_non_financial_agent'})
    packet={'generated_at':int(time.time()),'mode':'handoff_packet_no_delivery','from':args.from_agent,'to':args.to_agent,'subject':args.subject,'context':args.context,'next_action':args.next_action,'sensitivity':args.sensitivity,'deadline':args.deadline,'evidence':args.evidence,'guardrails':['não expor ferramentas/bastidores para lead/paciente','não prometer resultado clínico','não alterar produção sem autorização','usar RC-25/graphify para mudança canônica'],'findings':findings,'ok':not any(f['severity']=='HIGH' for f in findings)}
    if args.json_out: Path(args.json_out).write_text(json.dumps(packet,ensure_ascii=False,indent=2),encoding='utf-8')
    if args.md_out:
        lines=['# IVS Handoff Packet','',f"De: {args.from_agent}",f"Para: {args.to_agent}",f"Assunto: {args.subject}",f"Sensibilidade: {args.sensitivity}",'','## Contexto',args.context,'','## Próxima ação',args.next_action,'','## Guardrails']
        lines += [f"- {g}" for g in packet['guardrails']]
        lines += ['','## Achados'] + ([f"- [{f['severity']}] {f['code']}" for f in findings] or ['- Sem achados.'])
        Path(args.md_out).parent.mkdir(parents=True, exist_ok=True); Path(args.md_out).write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps(packet,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
