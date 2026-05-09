#!/usr/bin/env python3
"""Unified IVS Agent OS Cockpit.
Consolidates workflows, workflow runs, event feed, permissions and agent capabilities.
Read-only generator: no external sends, no production writes.
"""
import argparse, json, html, subprocess, time
from pathlib import Path
from typing import Any, Dict

BASE=Path('/root/.openclaw/workspace/skills/ivs-agent-operating-layer')
CAP_SCRIPT=Path('/root/.openclaw/workspace/skills/ivs-agent-capability-registry/scripts/capability_registry.py')
EVENT_SCRIPT=Path('/root/.openclaw/workspace/skills/ivs-agent-observability-events/scripts/agent_events.py')
WF_SCRIPT=BASE/'scripts/workflow_registry.py'
RUN_SCRIPT=BASE/'scripts/workflow_runner.py'
PERM=BASE/'policies/agent-permission-matrix.json'


def run_json(cmd):
    try:
        out=subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, timeout=30)
        return json.loads(out), None
    except Exception as e:
        return {}, str(e)

def load_json(p: Path, default=None):
    try: return json.loads(p.read_text(encoding='utf-8'))
    except Exception: return default if default is not None else {}

def esc(x): return html.escape(str(x if x is not None else ''))
def sev_class(sev):
    return {'HIGH':'bad','MEDIUM':'warn','LOW':'low','OK':'ok'}.get(str(sev),'low')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--out', default='/root/deliverables/cockpit-unico-ivs-agent-os.html')
    ap.add_argument('--json-out', default='/root/deliverables/cockpit-unico-ivs-agent-os.json')
    args=ap.parse_args()

    wf,wf_err=run_json(['python3',str(WF_SCRIPT),'--json'])
    cap,cap_err=run_json(['python3',str(CAP_SCRIPT),'--json']) if CAP_SCRIPT.exists() else ({},'capability script missing')
    ev,ev_err=run_json(['python3',str(EVENT_SCRIPT),'--json']) if EVENT_SCRIPT.exists() else ({},'events script missing')
    runs,runs_err=run_json(['python3',str(RUN_SCRIPT),'show','--limit','25'])
    perm=load_json(PERM, {})

    errors=[e for e in [wf_err,cap_err,ev_err,runs_err] if e]
    high=0; med=0; low=0
    for src in [wf,cap,ev]:
        for f in src.get('findings',[]) or []:
            if f.get('severity')=='HIGH': high+=1
            elif f.get('severity')=='MEDIUM': med+=1
            else: low+=1
        for event in src.get('events',[]) or []:
            if event.get('severity')=='HIGH': high+=1
            elif event.get('severity')=='MEDIUM': med+=1
            elif event.get('severity')=='LOW': low+=1
    if errors: med += len(errors)
    status='HIGH' if high else ('MEDIUM' if med else ('LOW' if low else 'OK'))

    report={
        'ok': status in ['OK','LOW'],
        'status': status,
        'generated_at': int(time.time()),
        'mode': 'unified_read_only_agent_os_cockpit',
        'sources': {
            'workflow_registry': {'ok': wf.get('ok'), 'error': wf_err, 'totals': wf.get('totals')},
            'capability_registry': {'ok': cap.get('ok'), 'error': cap_err, 'totals': cap.get('totals')},
            'observability_events': {'ok': ev.get('ok'), 'error': ev_err, 'totals': ev.get('totals')},
            'workflow_runs': {'error': runs_err, 'totals': {'runs': len(runs.get('runs',[]) or [])}},
            'permission_matrix': {'version': perm.get('version'), 'agents': len(perm.get('agents') or {})}
        },
        'workflows': wf.get('workflows',[])[:100],
        'agents': cap.get('agents',[])[:50],
        'runs': runs.get('runs',[])[:25],
        'events': (ev.get('events',[]) or [])[-80:],
        'permission_levels': perm.get('levels') or {},
        'global_rules': perm.get('global_rules') or [],
        'errors': errors
    }
    Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.json_out).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')

    cards=f"""
    <div class='grid'>
      <div class='card'><span>Estado</span><b class='{sev_class(status)}'>{esc(status)}</b></div>
      <div class='card'><span>Workflows</span><b>{esc((wf.get('totals') or {}).get('workflows',0))}</b></div>
      <div class='card'><span>Runs recentes</span><b>{len(report['runs'])}</b></div>
      <div class='card'><span>Agentes</span><b>{esc((cap.get('totals') or {}).get('agents',0))}</b></div>
      <div class='card'><span>Eventos</span><b>{esc((ev.get('totals') or {}).get('events',0))}</b></div>
      <div class='card'><span>Permission Matrix</span><b>{esc(perm.get('version','-'))}</b></div>
    </div>"""
    wf_rows=''.join(f"<tr><td>{esc(w.get('id'))}</td><td>{esc(w.get('owner'))}</td><td>{esc(w.get('mode'))}</td><td>{len(w.get('issues') or [])}</td></tr>" for w in report['workflows'])
    agent_rows=''.join(f"<tr><td>{esc(a.get('id'))}</td><td>{esc(a.get('skills_count'))}</td><td>{esc(', '.join(a.get('risk_hints') or []))}</td></tr>" for a in report['agents'])
    run_rows=''.join(f"<tr><td>{esc(r.get('run_id'))}</td><td>{esc(r.get('workflow_id'))}</td><td>{esc(r.get('state'))}</td><td>{esc(r.get('subject'))}</td></tr>" for r in report['runs'])
    event_rows=''.join(f"<tr><td class='{sev_class(e.get('severity'))}'>{esc(e.get('severity'))}</td><td>{esc(e.get('source'))}</td><td>{esc(e.get('kind'))}</td><td>{esc(e.get('message'))}</td></tr>" for e in report['events'][-50:])
    rules=''.join(f"<li>{esc(x)}</li>" for x in report['global_rules'])
    levels=''.join(f"<li><b>{esc(k)}</b>: {esc(v)}</li>" for k,v in report['permission_levels'].items())
    errs=''.join(f"<li>{esc(e)}</li>" for e in errors) or '<li>Sem erros de coleta.</li>'
    doc=f"""<!doctype html><html lang='pt-BR'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Cockpit Único IVS Agent OS</title><style>
    body{{font-family:Inter,system-ui,Arial;margin:0;background:#0b1120;color:#e5e7eb}}main{{max-width:1320px;margin:auto;padding:32px}}h1{{font-size:34px;margin:0 0 8px}}p{{color:#94a3b8}}.grid{{display:grid;grid-template-columns:repeat(6,1fr);gap:12px;margin:24px 0}}.card{{background:#111827;border:1px solid #273449;border-radius:18px;padding:18px}}.card span{{display:block;color:#94a3b8;font-size:13px}}.card b{{font-size:24px}}section{{background:#0f172a;border:1px solid #273449;border-radius:20px;padding:22px;margin:18px 0}}table{{width:100%;border-collapse:collapse;font-size:13px}}td,th{{border-bottom:1px solid #273449;padding:9px;text-align:left;vertical-align:top}}th{{color:#cbd5e1}}.ok{{color:#86efac}}.low{{color:#93c5fd}}.warn{{color:#fde68a}}.bad{{color:#fca5a5}}ul{{line-height:1.7}}@media(max-width:900px){{.grid{{grid-template-columns:repeat(2,1fr)}}}}</style></head><body><main>
    <h1>Cockpit Único IVS Agent OS</h1><p>Visão read-only de agentes, workflows, runs, eventos e permissões. Não executa ações sensíveis.</p>{cards}
    <section><h2>Regras globais</h2><ul>{rules}</ul><h3>Níveis de permissão</h3><ul>{levels}</ul></section>
    <section><h2>Workflow Registry</h2><table><thead><tr><th>ID</th><th>Dono</th><th>Modo</th><th>Issues</th></tr></thead><tbody>{wf_rows}</tbody></table></section>
    <section><h2>Agentes e capacidades</h2><table><thead><tr><th>Agente</th><th>Skills</th><th>Riscos</th></tr></thead><tbody>{agent_rows}</tbody></table></section>
    <section><h2>Runs recentes</h2><table><thead><tr><th>Run</th><th>Workflow</th><th>Estado</th><th>Assunto</th></tr></thead><tbody>{run_rows}</tbody></table></section>
    <section><h2>Eventos recentes</h2><table><thead><tr><th>Sev</th><th>Fonte</th><th>Tipo</th><th>Mensagem</th></tr></thead><tbody>{event_rows}</tbody></table></section>
    <section><h2>Erros de coleta</h2><ul>{errs}</ul></section>
    </main></body></html>"""
    Path(args.out).write_text(doc, encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))
if __name__=='__main__': main()
