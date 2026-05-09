#!/usr/bin/env python3
import argparse, json, re, time
from pathlib import Path

OPENCLAW=Path('/root/.openclaw/openclaw.json')
SKILLS_DIRS=[Path('/root/.openclaw/workspace/skills'), Path('/root/.openclaw/skills')]
WF_DIR=Path('/root/.openclaw/workspace/skills/ivs-agent-operating-layer/workflows')
CORE={'maria-gerente','clara-whatsapp','agente-reels-intel','pedro-controller-ivs','conselho-growth-vital-slim','llm-council'}
# Built-ins/legacy aliases exposed by OpenClaw or historical configs. They are not local IVS skills and should not count as findings.
BUILTIN_OR_EXTERNAL={
 'browser','browser-gamecoach','browser-qa','browser-use','browser-sequential-thinking','web-search','summarize','gog','notion','stitch-mcp-operacao',
 'graphify','social-content-vitalslim','content-strategy-vitalslim','copywriting-vitalslim','customer-research-vitalslim','medical-content','video-frames'
}
EXPECTED={
 'maria-gerente':['ivs-agent-operating-layer','ivs-agent-capability-registry','ivs-agent-observability-events'],
 'clara-whatsapp':['ivs-agent-operating-layer','ivs-agent-handoff-guard'],
 'agente-reels-intel':['ivs-agent-operating-layer','repo-reverse-ivs','openclaw-marketing-os','ivs-agent-capability-registry'],
 'pedro-controller-ivs':['ivs-agent-operating-layer','ivs-agent-capability-registry'],
}
RISK_HINTS={
 'clara-whatsapp':['whatsapp_real','lead_patient_boundary','patient_safety'],
 'pedro-controller-ivs':['financial_write_gate','omie','approval_required'],
 'agente-reels-intel':['public_marketing','brand_claims','clinical_promise_risk'],
 'maria-gerente':['production_coordination','pausing_guardrails','rc25_required'],
 'conselho-growth-vital-slim':['internal_only','recommendation_not_execution'],
 'llm-council':['internal_only','recommendation_not_execution'],
}

def load_json(p):
    try: return json.loads(p.read_text(encoding='utf-8'))
    except Exception as e: return {'_error':str(e)}

def skill_meta(name):
    for base in SKILLS_DIRS:
        p=base/name/'SKILL.md'
        if p.exists():
            txt=p.read_text(encoding='utf-8', errors='ignore')[:2500]
            m=re.search(r'description:\s*(.+)', txt)
            return {'name':name,'path':str(base/name),'has_skill_md':True,'kind':'local_skill','description':m.group(1).strip() if m else ''}
    if name in BUILTIN_OR_EXTERNAL:
        return {'name':name,'path':None,'has_skill_md':False,'kind':'builtin_or_legacy_external','description':'Built-in, external, or legacy alias; not governed as local IVS skill.'}
    return {'name':name,'path':str(SKILLS_DIRS[0]/name),'has_skill_md':False,'kind':'missing_local_skill','description':''}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--json',action='store_true'); ap.add_argument('--md-out'); args=ap.parse_args()
    cfg=load_json(OPENCLAW); findings=[]; agents=[]
    raw_agents=((cfg.get('agents') or {}).get('list') or []) if isinstance(cfg,dict) else []
    for a in raw_agents:
        aid=a.get('id')
        if not aid: continue
        skills=a.get('skills') or []
        missing=[]; skill_items=[]; builtin=[]
        for s in skills:
            meta=skill_meta(s); skill_items.append(meta)
            if meta['kind']=='missing_local_skill': missing.append(s)
            if meta['kind']=='builtin_or_legacy_external': builtin.append(s)
        for s in EXPECTED.get(aid,[]):
            if s not in skills: findings.append({'severity':'MEDIUM','agent':aid,'code':'expected_skill_missing','skill':s})
        if missing: findings.append({'severity':'LOW','agent':aid,'code':'missing_local_skill_definition','skills':missing})
        if aid=='clara-whatsapp' and 'message' in json.dumps(a.get('tools') or {}, ensure_ascii=False).lower():
            findings.append({'severity':'HIGH','agent':aid,'code':'clara_may_have_external_message_tool','note':'validar se não permite Telegram/WhatsApp fora da ponte Z-API'})
        agents.append({'id':aid,'name':(a.get('identity') or {}).get('name'), 'is_core':aid in CORE, 'skills_count':len(skills), 'local_skills_count':sum(1 for x in skill_items if x['kind']=='local_skill'), 'builtin_or_legacy_count':len(builtin), 'skills':skill_items, 'subagents':(a.get('subagents') or {}).get('allowAgents') or [], 'risk_hints':RISK_HINTS.get(aid,[])})
    workflows=[]
    if WF_DIR.exists():
        for p in sorted(WF_DIR.glob('*.json')):
            d=load_json(p); workflows.append({'id':d.get('id'), 'name':d.get('name'), 'owner':d.get('owner'), 'executor':d.get('executor'), 'file':str(p)})
    report={'ok':not any(f['severity']=='HIGH' for f in findings),'generated_at':int(time.time()),'mode':'read_only_capability_registry','totals':{'agents':len(agents),'core_agents':sum(1 for a in agents if a['is_core']),'workflows':len(workflows),'findings':len(findings)},'agents':agents,'workflows':workflows,'findings':findings}
    if args.md_out:
        lines=['# IVS Agent Capability Registry','',f"Gerado em: {report['generated_at']}",'',f"Agentes: {len(agents)} · Workflows: {len(workflows)} · Achados: {len(findings)}",'','## Agentes']
        for a in agents:
            lines += [f"### {a['id']}", f"- Nome: {a.get('name') or '-'}", f"- Skills: {a['skills_count']} ({a['local_skills_count']} locais; {a['builtin_or_legacy_count']} built-in/legadas)", f"- Subagentes: {', '.join(a['subagents']) or '-'}", f"- Riscos: {', '.join(a['risk_hints']) or '-'}", '']
        lines += ['## Achados']
        lines += [f"- [{f['severity']}] {f.get('agent','-')} · {f['code']} · {f.get('skill') or f.get('skills') or f.get('note') or ''}" for f in findings] or ['- Sem achados.']
        Path(args.md_out).parent.mkdir(parents=True, exist_ok=True); Path(args.md_out).write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))
if __name__=='__main__': main()
