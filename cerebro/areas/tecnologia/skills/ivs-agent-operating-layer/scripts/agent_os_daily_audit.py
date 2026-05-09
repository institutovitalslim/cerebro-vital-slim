#!/usr/bin/env python3
"""Daily read-only audit for IVS Agent OS layer.
Generates unified cockpit, compares against previous status and writes a short markdown report.
"""
import argparse, json, subprocess, time
from pathlib import Path
BASE=Path('/root/.openclaw/workspace/skills/ivs-agent-operating-layer')
STATE=BASE/'events/agent_os_daily_audit_state.json'
DEL=Path('/root/deliverables')
COCKPIT=BASE/'scripts/generate_agent_os_cockpit.py'

def load(p, default):
    try: return json.loads(p.read_text(encoding='utf-8'))
    except Exception: return default

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--json', action='store_true'); args=ap.parse_args()
    DEL.mkdir(parents=True, exist_ok=True); STATE.parent.mkdir(parents=True, exist_ok=True)
    html=DEL/'cockpit-unico-ivs-agent-os.html'; jout=DEL/'cockpit-unico-ivs-agent-os.json'
    subprocess.check_output(['python3', str(COCKPIT), '--out', str(html), '--json-out', str(jout)], stderr=subprocess.STDOUT, text=True)
    current=load(jout,{})
    prev=load(STATE,{})
    changes=[]
    if prev.get('status') and prev.get('status') != current.get('status'):
        changes.append({'type':'status_changed','from':prev.get('status'),'to':current.get('status')})
    cur_sources=current.get('sources') or {}; prev_sources=prev.get('sources') or {}
    for k,v in cur_sources.items():
        if (prev_sources.get(k) or {}).get('totals') != v.get('totals'):
            changes.append({'type':'source_totals_changed','source':k,'from':(prev_sources.get(k) or {}).get('totals'),'to':v.get('totals')})
    report={'ok':current.get('ok'), 'status':current.get('status'), 'generated_at':int(time.time()), 'mode':'daily_read_only_agent_os_audit', 'changes':changes, 'sources':cur_sources, 'cockpit_html':str(html), 'cockpit_json':str(jout)}
    STATE.write_text(json.dumps({'status':current.get('status'),'sources':cur_sources,'updated_at':report['generated_at']}, ensure_ascii=False, indent=2), encoding='utf-8')
    md=DEL/'agent-os-daily-audit-latest.md'
    lines=['# IVS Agent OS — auditoria diária','',f"Status: **{report['status']}**",f"OK: **{report['ok']}**",f"Gerado em: `{report['generated_at']}`",'', '## Fontes']
    for k,v in cur_sources.items(): lines.append(f"- {k}: ok={v.get('ok')} totals={v.get('totals')} error={v.get('error')}")
    lines += ['', '## Mudanças']
    lines += [f"- {c}" for c in changes] or ['- Sem mudança relevante desde a última execução.']
    lines += ['', f"Cockpit: `{html}`"]
    md.write_text('\n'.join(lines), encoding='utf-8')
    report['markdown']=str(md)
    print(json.dumps(report, ensure_ascii=False, indent=2))
if __name__=='__main__': main()
