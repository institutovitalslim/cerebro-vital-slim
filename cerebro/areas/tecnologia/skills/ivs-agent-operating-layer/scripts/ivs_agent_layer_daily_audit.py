#!/usr/bin/env python3
import argparse,json,subprocess,sys,time
from pathlib import Path
SKILL_DIR=Path('/root/.openclaw/workspace/skills/ivs-agent-operating-layer')
MONITOR=SKILL_DIR/'scripts/ivs_agent_layer_monitor.py'
DEFAULT_STATE=Path('/root/.openclaw/workspace/ops/ivs_agent_layer/ivs_agent_layer_audit_state.json')
DEFAULT_OUT=Path('/root/deliverables/ivs-agent-layer-daily-audit-latest.md')

def run(): return json.loads(subprocess.check_output([sys.executable,str(MONITOR),'--json'], text=True))
def load(p):
 try: return json.loads(Path(p).read_text(encoding='utf-8')) if Path(p).exists() else {}
 except Exception: return {}
def save(p,d): Path(p).parent.mkdir(parents=True,exist_ok=True); Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def snap(r):
 f=r.get('findings') or []
 counts={}
 for x in f: counts[x.get('severity','LOW')]=counts.get(x.get('severity','LOW'),0)+1
 areas={a.get('key'):{'severity':a.get('severity'),'findings_count':a.get('findings_count')} for a in r.get('areas') or []}
 return {'generated_at':r.get('generated_at'),'overall_severity':r.get('overall_severity'),'findings_total':len(f),'high':counts.get('HIGH',0),'medium':counts.get('MEDIUM',0),'low':counts.get('LOW',0),'areas':areas,'codes':sorted([f"{x.get('area')}:{x.get('code')}" for x in f])}
def diff(prev,cur):
 if not prev: return ['Primeira execução: baseline consolidado criado.']
 out=[]
 for k in ['overall_severity','findings_total','high','medium','low']:
  if prev.get(k)!=cur.get(k): out.append(f'{k}: {prev.get(k)} → {cur.get(k)}')
 if prev.get('codes')!=cur.get('codes'):
  out.append('Lista de achados mudou.')
 return out or ['Sem mudanças relevantes desde a última execução.']
def md(r,cur,changes):
 ts=time.strftime('%d/%m/%Y %H:%M UTC',time.gmtime(r.get('generated_at') or time.time()))
 lines=['# Auditoria diária consolidada — IVS Agent Operating Layer','',f'- Gerado em: {ts}',f'- Severidade consolidada: **{cur["overall_severity"]}**','- Modo: read-only; sem contato com paciente; sem publicação externa; sem alteração de produção.','','## Indicadores',f'- Achados totais: {cur["findings_total"]}',f'- HIGH: {cur["high"]}',f'- MEDIUM: {cur["medium"]}',f'- LOW: {cur["low"]}','','## Áreas']
 for a in r.get('areas') or []:
  lines.append(f'- {a.get("area")}: {a.get("severity")} — {a.get("headline")}')
 lines += ['','## Mudanças desde a última execução'] + [f'- {c}' for c in changes]
 lines += ['','## Achados']
 for f in r.get('findings') or []:
  lines.append(f'- {f.get("area")} · {f.get("severity")} · {f.get("code")} · count={f.get("count") or "—"}')
 lines += ['','## Regra mantida','- Monitores consolidam evidência. Ações de estado continuam exigindo autorização explícita quando houver risco operacional.']
 return '\n'.join(lines)+'\n'
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--state',default=str(DEFAULT_STATE)); ap.add_argument('--out',default=str(DEFAULT_OUT)); ap.add_argument('--no-save',action='store_true'); ap.add_argument('--json',action='store_true'); args=ap.parse_args()
 r=run(); cur=snap(r); prev=(load(args.state) or {}).get('snapshot') or {}; changes=diff(prev,cur); text=md(r,cur,changes); Path(args.out).parent.mkdir(parents=True,exist_ok=True); Path(args.out).write_text(text,encoding='utf-8')
 if not args.no_save: save(args.state,{'snapshot':cur,'last_report':args.out,'updated_at':int(time.time())})
 res={'ok':True,'severity':cur['overall_severity'],'changes':changes,'snapshot':cur,'report':args.out,'state':args.state,'saved':not args.no_save}
 print(json.dumps(res,ensure_ascii=False,indent=2) if args.json else text)
if __name__=='__main__': main()
