#!/usr/bin/env python3
"""IVS Agent Operating Layer consolidated monitor — read-only."""
import argparse, json, subprocess, sys, time
from pathlib import Path

SKILL_DIR=Path('/root/.openclaw/workspace/skills/ivs-agent-operating-layer')
SCRIPTS=SKILL_DIR/'scripts'
MONITORS={
 'clara': SCRIPTS/'clara_safety_monitor.py',
 'preconsulta': SCRIPTS/'preconsulta_safety_monitor.py',
 'marketing_os': SCRIPTS/'marketing_os_monitor.py',
}
AUDIT_STATE={
 'clara': Path('/root/.openclaw/workspace/ops/zapi_bridge/clara_safety_audit_state.json'),
 'preconsulta': Path('/root/ivs-preconsulta-data/.preconsulta_safety_audit_state.json'),
 'marketing_os': Path('/root/.openclaw/workspace/ops/marketing_os/marketing_os_audit_state.json'),
}

def run_monitor(name,path):
    try:
        out=subprocess.check_output([sys.executable,str(path),'--json'], text=True, stderr=subprocess.STDOUT, timeout=45)
        return {'ok': True, 'data': json.loads(out)}
    except subprocess.CalledProcessError as e:
        return {'ok': False, 'error': e.output[-4000:]}
    except Exception as e:
        return {'ok': False, 'error': str(e)}

def load_state(path):
    try:
        if path.exists():
            s=json.loads(path.read_text(encoding='utf-8'))
            return {'exists': True, 'updated_at': s.get('updated_at'), 'snapshot': s.get('snapshot')}
    except Exception as e:
        return {'exists': True, 'error': str(e)}
    return {'exists': False}

def normalize_findings(name, res):
    if not res.get('ok'):
        return [{'area':name,'severity':'HIGH','code':f'{name}_monitor_failed','detail':res.get('error')}]
    data=res.get('data') or {}
    out=[]
    for f in data.get('findings') or []:
        item=dict(f); item['area']=name; item['severity']=str(item.get('severity') or 'LOW').upper(); out.append(item)
    return out

def area_summary(name, res):
    if not res.get('ok'):
        return {'area':name,'status':'FALHA','severity':'HIGH','error':res.get('error')}
    d=res.get('data') or {}; findings=normalize_findings(name,res)
    sev='OK'
    if any(f.get('severity')=='HIGH' for f in findings): sev='HIGH'
    elif any(f.get('severity')=='MEDIUM' for f in findings): sev='MEDIUM'
    elif findings: sev='LOW'
    if name=='clara':
        h=d.get('health') or d.get('bridge_health') or d.get('app_probe') or {}
        totals=d.get('totals') or {}
        return {'area':'Clara/Z-API','key':'clara','severity':sev,'status':'Atenção' if sev!='OK' else 'OK','headline':f"Bridge {'OK' if h.get('ok', True) else 'falha'} · exclusões {totals.get('exclusions') or d.get('exclusions_count') or '—'}",'totals':totals,'findings_count':len(findings)}
    if name=='preconsulta':
        totals=d.get('totals') or {}
        return {'area':'Pré-consulta','key':'preconsulta','severity':sev,'status':'Atenção' if sev!='OK' else 'OK','headline':f"App {'OK' if (d.get('app_probe') or {}).get('ok') else 'falha'} · submissões {totals.get('submissions')} · drafts {totals.get('drafts')}",'totals':totals,'findings_count':len(findings)}
    if name=='marketing_os':
        totals=d.get('totals') or {}
        return {'area':'Marketing OS / João','key':'marketing_os','severity':sev,'status':'Atenção' if sev!='OK' else 'OK','headline':f"Backlog {totals.get('marketing_backlog_items')} · HTMLs {totals.get('recent_html_deliverables')} · regras ausentes {len((d.get('rule_health') or {}).get('missing') or [])}",'totals':totals,'findings_count':len(findings)}
    return {'area':name,'key':name,'severity':sev,'status':sev,'headline':'—','findings_count':len(findings)}

def overall_severity(findings):
    if any(f.get('severity')=='HIGH' for f in findings): return 'ALTA'
    if any(f.get('severity')=='MEDIUM' for f in findings): return 'MÉDIA'
    if findings: return 'BAIXA'
    return 'OK'

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--json', action='store_true'); args=ap.parse_args()
    results={k:run_monitor(k,p) for k,p in MONITORS.items()}
    findings=[]
    for k,r in results.items(): findings.extend(normalize_findings(k,r))
    summaries=[area_summary(k,r) for k,r in results.items()]
    states={k:load_state(p) for k,p in AUDIT_STATE.items()}
    report={
        'ok': all(r.get('ok') for r in results.values()),
        'generated_at': int(time.time()),
        'mode':'read_only_consolidated_no_patient_contact_no_external_posting',
        'overall_severity': overall_severity(findings),
        'areas': summaries,
        'findings': findings,
        'states': states,
        'raw': {k:v.get('data') for k,v in results.items() if v.get('ok')},
        'errors': {k:v.get('error') for k,v in results.items() if not v.get('ok')},
        'next_actions': [
            'Tratar achados ALTA antes de novas promessas operacionais.',
            'Manter monitores read-only; qualquer ação de estado exige ordem explícita.',
            'Usar cockpit geral para priorizar Clara, Pré-consulta e João sem misturar escopos.'
        ]
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
if __name__=='__main__': main()
