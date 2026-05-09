#!/usr/bin/env python3
"""Workflow Registry validator/index for IVS Agent Operating Layer."""
import argparse, json, time
from pathlib import Path
from typing import Any, Dict, List

WORKFLOWS_DIR=Path('/root/.openclaw/workspace/skills/ivs-agent-operating-layer/workflows')
REQUIRED=['id','name','owner','executor','scope','mode','entry_criteria','preflight','allowed_actions','blocked_actions','outputs','evidence','severity_rules']
LIST_FIELDS=['entry_criteria','preflight','allowed_actions','blocked_actions','outputs','evidence']

def load_workflow(path: Path):
    try:
        data=json.loads(path.read_text(encoding='utf-8'))
        return data, None
    except Exception as e:
        return None, str(e)

def validate(data: Dict[str,Any]):
    issues=[]
    for k in REQUIRED:
        if k not in data or data.get(k) in [None,'',[]]: issues.append({'severity':'HIGH','code':'missing_required_field','field':k})
    for k in LIST_FIELDS:
        if k in data and not isinstance(data[k], list): issues.append({'severity':'HIGH','code':'field_not_list','field':k})
    if 'severity_rules' in data and not isinstance(data['severity_rules'], dict): issues.append({'severity':'HIGH','code':'severity_rules_not_dict'})
    if 'blocked_actions' in data and isinstance(data['blocked_actions'], list):
        text=' '.join(str(x).lower() for x in data['blocked_actions'])
        if data.get('id') in ['followup-seguro','agent-layer-audit'] and 'pausar' not in text and 'despausar' not in text:
            issues.append({'severity':'MEDIUM','code':'pause_guardrail_not_explicit'})
    return issues

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--json', action='store_true'); args=ap.parse_args()
    workflows=[]; findings=[]
    for p in sorted(WORKFLOWS_DIR.glob('*.json')):
        data,err=load_workflow(p)
        if err:
            findings.append({'severity':'HIGH','code':'invalid_workflow_json','file':p.name,'error':err}); continue
        issues=validate(data)
        workflows.append({'id':data.get('id'),'name':data.get('name'),'owner':data.get('owner'),'executor':data.get('executor'),'mode':data.get('mode'),'scope':data.get('scope'),'file':str(p),'entry_count':len(data.get('entry_criteria') or []),'preflight_count':len(data.get('preflight') or []),'blocked_count':len(data.get('blocked_actions') or []),'issues':issues,'severity_rules':data.get('severity_rules') or {}})
        for issue in issues:
            item=dict(issue); item['workflow']=data.get('id'); findings.append(item)
    report={'ok': not any(f.get('severity')=='HIGH' for f in findings),'generated_at':int(time.time()),'mode':'read_only_registry_validation','totals':{'workflows':len(workflows),'findings':len(findings)},'workflows':workflows,'findings':findings}
    print(json.dumps(report, ensure_ascii=False, indent=2))
if __name__=='__main__': main()
