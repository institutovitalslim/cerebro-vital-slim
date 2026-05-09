#!/usr/bin/env python3
import argparse,json,subprocess,sys,time
from pathlib import Path
SKILL_DIR=Path('/root/.openclaw/workspace/skills/ivs-agent-operating-layer')
MONITOR=SKILL_DIR/'scripts/preconsulta_safety_monitor.py'
DEFAULT_STATE=Path('/root/ivs-preconsulta-data/.preconsulta_safety_audit_state.json')
DEFAULT_OUT=Path('/root/deliverables/preconsulta-daily-audit-latest.md')

def run(): return json.loads(subprocess.check_output([sys.executable,str(MONITOR),'--json'], text=True))
def load(p):
 try: return json.loads(Path(p).read_text(encoding='utf-8')) if Path(p).exists() else {}
 except Exception: return {}
def save(p,d): Path(p).parent.mkdir(parents=True,exist_ok=True); Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def snap(r):
 return {'generated_at':r.get('generated_at'),'app_ok':(r.get('app_probe') or {}).get('ok') is True,'json_files':(r.get('totals') or {}).get('json_files') or 0,'submissions':(r.get('totals') or {}).get('submissions') or 0,'drafts':(r.get('totals') or {}).get('drafts') or 0,'invalid':(r.get('totals') or {}).get('invalid') or 0,'stale_drafts':r.get('stale_drafts_count') or 0,'missing_markdown':r.get('missing_markdown_count') or 0,'incomplete':r.get('incomplete_count') or 0,'fallback_count':(r.get('fallback_queue') or {}).get('count') or 0,'findings':sorted([f.get('code') for f in r.get('findings') or [] if f.get('code')])}
def diff(prev,cur):
 if not prev: return ['Primeira execução: baseline criado.']
 labels={'app_ok':'App disponível','json_files':'JSONs','submissions':'Submissões','drafts':'Rascunhos','invalid':'JSON inválidos','stale_drafts':'Drafts >2h','missing_markdown':'Submissões sem markdown','incomplete':'Registros incompletos','fallback_count':'Fila fallback Telegram'}
 out=[]
 for k,l in labels.items():
  if prev.get(k)!=cur.get(k): out.append(f'{l}: {prev.get(k)} → {cur.get(k)}')
 return out or ['Sem mudanças relevantes desde a última execução.']
def sev(r,cur):
 if not cur.get('app_ok') or cur.get('invalid') or cur.get('missing_markdown'): return 'ALTA'
 if cur.get('stale_drafts') or cur.get('incomplete') or cur.get('fallback_count'): return 'MÉDIA'
 return 'OK'
def md(r,cur,changes,severity):
 ts=time.strftime('%d/%m/%Y %H:%M UTC',time.gmtime(r.get('generated_at') or time.time()))
 lines=['# Auditoria diária Pré-consulta — IVS','',f'- Gerado em: {ts}',f'- Severidade operacional: **{severity}**','- Modo: read-only; sem contato com paciente; sem alteração de produção.','','## Indicadores',f'- App disponível: {cur["app_ok"]}',f'- JSONs: {cur["json_files"]}',f'- Submissões: {cur["submissions"]}',f'- Rascunhos: {cur["drafts"]}',f'- JSON inválidos: {cur["invalid"]}',f'- Drafts > 2h: {cur["stale_drafts"]}',f'- Submissões sem markdown: {cur["missing_markdown"]}',f'- Registros incompletos: {cur["incomplete"]}',f'- Fila fallback Telegram: {cur["fallback_count"]}','','## Mudanças desde a última execução']
 lines += [f'- {c}' for c in changes]
 lines += ['','## Próxima ação operacional']
 if severity=='ALTA': lines.append('- Investigar imediatamente antes de afirmar que dados de pré-consulta existem ou pedir novo preenchimento.')
 elif severity=='MÉDIA': lines.append('- Revisar drafts/fallbacks e decidir recuperação operacional sem contato automático.')
 else: lines.append('- Sem ação imediata.')
 lines += ['','## Regra mantida','- Nunca pedir ao paciente para preencher novamente antes de validar servidor, drafts, JSON, markdown e logs.']
 return '\n'.join(lines)+'\n'
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--state',default=str(DEFAULT_STATE)); ap.add_argument('--out',default=str(DEFAULT_OUT)); ap.add_argument('--no-save',action='store_true'); ap.add_argument('--json',action='store_true'); args=ap.parse_args()
 r=run(); cur=snap(r); prev=(load(args.state) or {}).get('snapshot') or {}; changes=diff(prev,cur); severity=sev(r,cur); text=md(r,cur,changes,severity); Path(args.out).parent.mkdir(parents=True,exist_ok=True); Path(args.out).write_text(text,encoding='utf-8')
 if not args.no_save: save(args.state,{'snapshot':cur,'last_report':args.out,'updated_at':int(time.time())})
 res={'ok':True,'severity':severity,'changes':changes,'snapshot':cur,'report':args.out,'state':args.state,'saved':not args.no_save}
 print(json.dumps(res,ensure_ascii=False,indent=2) if args.json else text)
if __name__=='__main__': main()
