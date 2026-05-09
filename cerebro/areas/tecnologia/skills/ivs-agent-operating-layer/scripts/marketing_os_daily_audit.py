#!/usr/bin/env python3
import argparse,json,subprocess,sys,time
from pathlib import Path
SKILL_DIR=Path('/root/.openclaw/workspace/skills/ivs-agent-operating-layer')
MONITOR=SKILL_DIR/'scripts/marketing_os_monitor.py'
DEFAULT_STATE=Path('/root/.openclaw/workspace/ops/marketing_os/marketing_os_audit_state.json')
DEFAULT_OUT=Path('/root/deliverables/marketing-os-daily-audit-latest.md')

def run(): return json.loads(subprocess.check_output([sys.executable,str(MONITOR),'--json'], text=True))
def load(p):
 try: return json.loads(Path(p).read_text(encoding='utf-8')) if Path(p).exists() else {}
 except Exception: return {}
def save(p,d): Path(p).parent.mkdir(parents=True,exist_ok=True); Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def snap(r):
 t=r.get('totals') or {}
 return {'generated_at':r.get('generated_at'),'marketing_backlog_items':t.get('marketing_backlog_items') or 0,'recent_html_deliverables':t.get('recent_html_deliverables') or 0,'recent_outbound_files':t.get('recent_outbound_files') or 0,'html_not_outbound':len(r.get('html_deliverables_not_in_outbound') or []),'session_risks':len(r.get('session_risks') or []),'rule_missing':len((r.get('rule_health') or {}).get('missing') or []),'findings':sorted([f.get('code') for f in r.get('findings') or [] if f.get('code')])}
def severity(cur):
 if cur.get('rule_missing'): return 'ALTA'
 if cur.get('html_not_outbound') or cur.get('session_risks'): return 'MÉDIA'
 return 'OK'
def diff(prev,cur):
 if not prev: return ['Primeira execução: baseline criado.']
 labels={'marketing_backlog_items':'Backlog marketing','recent_html_deliverables':'HTMLs recentes','recent_outbound_files':'Arquivos outbound','html_not_outbound':'HTMLs fora do outbound','session_risks':'Marcadores de risco em sessão','rule_missing':'Regras ausentes'}
 out=[]
 for k,l in labels.items():
  if prev.get(k)!=cur.get(k): out.append(f'{l}: {prev.get(k)} → {cur.get(k)}')
 return out or ['Sem mudanças relevantes desde a última execução.']
def md(r,cur,changes,sev):
 ts=time.strftime('%d/%m/%Y %H:%M UTC',time.gmtime(r.get('generated_at') or time.time()))
 lines=['# Auditoria diária Marketing OS — João / IVS','',f'- Gerado em: {ts}',f'- Severidade operacional: **{sev}**','- Modo: read-only; sem publicação externa; sem alteração de produção.','','## Indicadores',f'- Backlog marketing: {cur["marketing_backlog_items"]}',f'- HTMLs recentes: {cur["recent_html_deliverables"]}',f'- Arquivos outbound recentes: {cur["recent_outbound_files"]}',f'- HTMLs fora do outbound: {cur["html_not_outbound"]}',f'- Marcadores de risco em sessão: {cur["session_risks"]}',f'- Regras ausentes: {cur["rule_missing"]}','','## Mudanças desde a última execução']
 lines += [f'- {c}' for c in changes]
 lines += ['','## Achados ativos'] + [f'- {c}' for c in cur.get('findings',[])]
 lines += ['','## Próxima ação operacional']
 if sev=='ALTA': lines.append('- Corrigir regra/canon antes de liberar João para entregas críticas.')
 elif sev=='MÉDIA': lines.append('- Revisar entregáveis não enviados e marcadores de sessão antes de cobrar nova produção do João.')
 else: lines.append('- Sem ação imediata.')
 lines += ['','## Regra mantida','- Maria corrige execução, roteamento e continuidade; João continua responsável por marketing/reels no tópico próprio.']
 return '\n'.join(lines)+'\n'
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--state',default=str(DEFAULT_STATE)); ap.add_argument('--out',default=str(DEFAULT_OUT)); ap.add_argument('--no-save',action='store_true'); ap.add_argument('--json',action='store_true'); args=ap.parse_args()
 r=run(); cur=snap(r); prev=(load(args.state) or {}).get('snapshot') or {}; changes=diff(prev,cur); sev=severity(cur); text=md(r,cur,changes,sev); Path(args.out).parent.mkdir(parents=True,exist_ok=True); Path(args.out).write_text(text,encoding='utf-8')
 if not args.no_save: save(args.state,{'snapshot':cur,'last_report':args.out,'updated_at':int(time.time())})
 res={'ok':True,'severity':sev,'changes':changes,'snapshot':cur,'report':args.out,'state':args.state,'saved':not args.no_save}
 print(json.dumps(res,ensure_ascii=False,indent=2) if args.json else text)
if __name__=='__main__': main()
