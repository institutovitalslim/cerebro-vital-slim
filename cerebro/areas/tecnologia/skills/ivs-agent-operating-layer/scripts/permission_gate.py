#!/usr/bin/env python3
"""IVS Agent Permission Gate.
Read-only evaluator for whether an agent/action is read_only, dry_run, write_with_approval or forbidden.
It does not execute the action.
"""
import argparse, json, time
from pathlib import Path
MATRIX=Path('/root/.openclaw/workspace/skills/ivs-agent-operating-layer/policies/agent-permission-matrix.json')
SENSITIVE={'patient','clinical','financial','external_send','production_write','pause_clara'}

def load(): return json.loads(MATRIX.read_text(encoding='utf-8'))
def decide(agent, action, sensitivity=None, approved=False, evidence=None):
    m=load(); a=(m.get('agents') or {}).get(agent)
    findings=[]
    if not a:
        return {'ok':False,'decision':'forbidden','reason':'unknown_agent','findings':[{'severity':'HIGH','code':'unknown_agent'}]}
    level=(a.get('permissions') or {}).get(action, a.get('default','forbidden'))
    if sensitivity in ['patient','clinical'] and agent=='clara-whatsapp' and action not in ['respond_lead_whatsapp','followup_whatsapp','handoff_agent']:
        level='forbidden'; findings.append({'severity':'HIGH','code':'clara_patient_clinical_block'})
    if action in ['pause_clara','unpause_clara'] and not approved:
        findings.append({'severity':'HIGH','code':'tiaro_explicit_approval_required'})
    if level=='write_with_approval' and not approved:
        return {'ok':False,'decision':level,'requires_approval':True,'reason':'approval_required','agent':agent,'action':action,'sensitivity':sensitivity,'findings':findings}
    if level=='write_with_approval' and approved and not evidence:
        findings.append({'severity':'MEDIUM','code':'approval_without_evidence'})
    ok=level in ['read_only','dry_run'] or (level=='write_with_approval' and approved)
    if level=='forbidden': ok=False
    return {'ok':ok,'decision':level,'requires_approval':level=='write_with_approval','approved':bool(approved),'agent':agent,'action':action,'sensitivity':sensitivity,'evidence':evidence or [],'findings':findings,'generated_at':int(time.time()),'mode':'permission_evaluation_no_execution'}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--agent',required=True); ap.add_argument('--action',required=True); ap.add_argument('--sensitivity'); ap.add_argument('--approved',action='store_true'); ap.add_argument('--evidence', action='append', default=[]); ap.add_argument('--json',action='store_true')
    args=ap.parse_args(); print(json.dumps(decide(args.agent,args.action,args.sensitivity,args.approved,args.evidence),ensure_ascii=False,indent=2))
if __name__=='__main__': main()
