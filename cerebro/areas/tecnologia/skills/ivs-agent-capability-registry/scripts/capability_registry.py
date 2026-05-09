#!/usr/bin/env python3
import argparse, json, re, time
from pathlib import Path

OPENCLAW=Path('/root/.openclaw/openclaw.json')
SKILLS_DIR=Path('/root/.openclaw/workspace/skills')
WF_DIR=SKILLS_DIR/'ivs-agent-operating-layer/workflows'
CORE={'maria-gerente','clara-whatsapp','agente-reels-intel','pedro-controller-ivs','conselho-growth-vital-slim','llm-council'}
EXPECTED={
 'maria-gerente':['ivs-agent-operating-layer'],
 'clara-whatsapp':['ivs-agent-operating-layer'],
 'agente-reels-intel':['ivs-agent-operating-layer','repo-reverse-ivs','openclaw-marketing-os'],
 'pedro-controller-ivs':['ivs-agent-operating-layer'],
}
RISK_HINTS={
 'clara-whatsapp':['whatsapp_real','lead_patient_boundary','patient_safety'],
 'pedro-controller-ivs':['financial_write_gate','omie','approval_required'],
 'agente-reels-intel':['public_marketing','brand_claims','clinical_promise_risk'],
 'maria-gerente':['production_coordination','pausing_guardrails','rc25_required'],
}

def load_json(p):
    try: return json.loads(p.read_text(encoding='utf-8'))
    except Exception as e: return {'_error':str(e)}

def skill_meta(name):
    p=SKILLS_DIR/name/'SKILL.md'
    exists=p.exists()
    desc=''
    if exists:
        txt=p.read_text(encoding='utf-8', errors='ignore')[:2500]
        m=re.search(r'description:\s*(.+)', txt)
        if m: desc=m.group(1).strip()
    return {'name':name,'path':str(SKILLS_DIR/name),'has_skill_md':exists,'description':desc}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--json',action='store_true'); ap.add_argument('--md-out'); args=ap.parse_args()
    cfg=load_json(OPENCLAW); findings=[]; agents=[]
    raw_agents=((cfg.get('agents') or {}).get('list') or []) if isinstance(cfg,dict) else []
    for a in raw_agents:
        aid=a.get('id')
        if not aid: continue
        skills=a.get('skills') or []
        missing=[]; skill_items=[]
        for s in skills:
            meta=skill_meta(s); skill_items.append(meta)
            if not meta['has_skill_md']: missing.append(s)
        for s in EXPECTED.get(aid,[]):
            if s not in skills: findings.append({'severity':'MEDIUM','agent':aid,'code':'expected_skill_missing','skill':s})
        if missing: findings.append({'severity':'LOW','agent':aid,'code':'skill_without_skill_md','skills':missing})
        if aid=='clara-whatsapp' and 'message' in json.dumps(a.get('tools') or {}, ensure_ascii=False).lower():
            findings.append({'severity':'HIGH','agent':aid,'code':'clara_may_have_external_message_tool','note':'validar se não permite Telegram/WhatsApp fora da ponte Z-API'})
        agents.append({'id':aid,'name':(a.get('identity') or {}).get('name'), 'is_core':aid in CORE, 'skills_count':len(skills), 'skills':skill_items, 'subagents':(a.get('subagents') or {}).get('allowAgents') or [], 'risk_hints':RISK_HINTS.get(aid,[])})
    workflows=[]
    if WF_DIR.exists():
        for p in sorted(WF_DIR.glob('*.json')):
            d=load_json(p); workflows.append({'id':d.get('id'), 'name':d.get('name'), 'owner':d.get('owner'), 'executor':d.get('executor'), 'file':str(p)})
    report={'ok':not any(f['severity']=='HIGH' for f in findings),'generated_at':int(time.time()),'mode':'read_only_capability_registry','totals':{'agents':len(agents),'core_agents':sum(1 for a in agents if a['is_core']),'workflows':len(workflows),'findings':len(findings)},'agents':agents,'workflows':workflows,'findings':findings}
    if args.md_out:
        lines=['# IVS Agent Capability Registry','',f"Gerado em: {report['generated_at']}",'',f"Agentes: {len(agents)} · Workflows: {len(workflows)} · Achados: {len(findings)}",'','## Agentes']
        for a in agents:
            lines += [f"### {a['id']}", f"- Nome: {a.get('name') or '-'}", f"- Skills: {a['skills_count']}", f"- Subagentes: {', '.join(a['subagents']) or '-'}", f"- Riscos: {', '.join(a['risk_hints']) or '-'}", '']
        lines += ['## Achados']
        lines += [f"- [{f['severity']}] {f.get('agent','-')} · {f['code']} · {f.get('skill') or f.get('skills') or f.get('note') or ''}" for f in findings] or ['- Sem achados.']
        Path(args.md_out).parent.mkdir(parents=True, exist_ok=True); Path(args.md_out).write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))
if __name__=='__main__': main()
