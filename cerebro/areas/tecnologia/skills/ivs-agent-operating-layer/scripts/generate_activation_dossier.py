#!/usr/bin/env python3
"""Generate executive activation dossier for IVS Agent OS.
Read-only; consolidates status, pending approvals and rollback.
"""
import argparse, json, time, html
from pathlib import Path
DEL=Path('/root/deliverables')
FILES={
 'readiness':'/root/deliverables/agent-os-readiness-scorecard.json',
 'ci':'/root/deliverables/agent-os-ci-latest.json',
 'registry':'/root/deliverables/workflow-registry-after-approval-queue.json',
 'queue':'/root/deliverables/approval-queue-ivs-agent-os.json',
 'clara_shadow':'/root/deliverables/clara-action-gate-shadow-latest.json',
 'clara_phase2':'/root/deliverables/clara-enforcement-phase2-preflight-latest.json',
 'pedro_omie':'/root/deliverables/pedro-omie-write-preflight-latest.json',
 'offsite':'/root/deliverables/agent-os-offsite-backup-latest.json',
 'drift':'/root/deliverables/agent-os-drift-report.json',
}

def load(p):
    try: return json.load(open(p))
    except Exception as e: return {'ok':False,'error':str(e),'missing':True}

def esc(x): return html.escape(str(x))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--json-out',default='/root/deliverables/activation-dossier-ivs-agent-os.json'); ap.add_argument('--html-out',default='/root/deliverables/activation-dossier-ivs-agent-os.html'); ap.add_argument('--json',action='store_true'); args=ap.parse_args()
    data={k:load(v) for k,v in FILES.items()}
    queue=data['queue'].get('items',[])
    critical_ok=all([
        data['readiness'].get('status') in ('READY','ATTENTION'),
        data['drift'].get('ok'),
        data['queue'].get('ok'),
        data['clara_shadow'].get('ok'),
        data['clara_phase2'].get('ok'),
        data['pedro_omie'].get('ok'),
        data['offsite'].get('ok'),
    ])
    recommendations=[
        'Clara Phase 2 enforcement ativada; manter watch por 24h.',
        'Não executar Pedro/Omie write sem payload revisado, approval e credenciais conferidas.',
        'Offsite local_mirror executado; manter export externo/rclone bloqueado sem novo destino explícito e approval.',
        'Usar Approval Queue como painel de pendências; ela não registra aprovação.'
    ]
    report={'ok':critical_ok,'generated_at':int(time.time()),'mode':'read_only_executive_activation_dossier','summary':{
        'readiness_status':data['readiness'].get('status'),
        'readiness_score':data['readiness'].get('score'),
        'pending_approvals':data['queue'].get('totals',{}).get('pending'),
        'executed_sensitive_actions':data['queue'].get('totals',{}).get('executed'),
        'drift_findings':data['drift'].get('totals',{}).get('findings'),
        'recommendation':'operate_shadow_and_wait_explicit_approvals'
    },'pending_approvals':queue,'recommendations':recommendations,'source_files':FILES,'guardrails':['read-only dossier','does not approve','does not execute','does not expose secrets']}
    Path(args.json_out).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    rows=''.join(f"<tr><td>{esc(i.get('id'))}</td><td>{esc(i.get('title'))}</td><td>{esc(i.get('status'))}</td><td><code>{esc(i.get('required_phrase'))}</code></td><td>{esc(i.get('risk'))}</td></tr>" for i in queue)
    rec=''.join(f'<li>{esc(r)}</li>' for r in recommendations)
    s=report['summary']
    doc=f"""<!doctype html><html><head><meta charset='utf-8'><title>Dossier Executivo IVS Agent OS</title><style>body{{font-family:Arial;margin:28px;color:#111}}.card{{display:inline-block;border:1px solid #ddd;border-radius:10px;padding:14px;margin:8px;background:#fafafa}}table{{border-collapse:collapse;width:100%;margin-top:16px}}td,th{{border:1px solid #ddd;padding:8px;vertical-align:top}}th{{background:#111;color:white}}code{{white-space:pre-wrap}}.ok{{color:#087b2f;font-weight:bold}}</style></head><body><h1>Dossier Executivo — IVS Agent OS</h1><p>Documento read-only. Não aprova e não executa ações sensíveis.</p><div class='card'><b>Readiness</b><br><span class='ok'>{esc(s.get('readiness_status'))} {esc(s.get('readiness_score'))}/100</span></div><div class='card'><b>Pendências</b><br>{esc(s.get('pending_approvals'))}</div><div class='card'><b>Ações sensíveis executadas</b><br>{esc(s.get('executed_sensitive_actions'))}</div><div class='card'><b>Drift findings</b><br>{esc(s.get('drift_findings'))}</div><h2>Aprovações pendentes</h2><table><thead><tr><th>ID</th><th>Ação</th><th>Status</th><th>Frase exigida</th><th>Risco</th></tr></thead><tbody>{rows}</tbody></table><h2>Recomendações</h2><ul>{rec}</ul></body></html>"""
    Path(args.html_out).write_text(doc,encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    raise SystemExit(0 if report['ok'] else 2)
if __name__=='__main__': main()
