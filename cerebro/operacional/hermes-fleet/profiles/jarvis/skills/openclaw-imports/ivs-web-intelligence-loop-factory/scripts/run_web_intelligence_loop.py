#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess
from datetime import datetime, timezone
from pathlib import Path
LOOP_APPLICATIONS={
"revenue":["Detectar lead parado, follow-up perdido, etapa travada e queda de agendamentos.","Transformar evidência em alerta executivo para Maria, sem expor PII."],
"content":["Converter páginas/referências públicas em hooks, ângulos, objeções, CTA e variações para João.","Registrar o que funcionou e empurrar ângulos fortes para múltiplos formatos."],
"seo-aeo":["Auditar intenção, gaps, páginas decadentes, atualizações e visibilidade em respostas de IA.","Comparar site/blog IVS com concorrentes públicos e gerar oportunidades editoriais."],
"outbound":["Pesquisar parceiros/listas públicas e gerar drafts internos de abordagem.","Parar antes de qualquer envio externo para aprovação humana."],
"finance":["Sinalizar gasto duplicado, ferramenta sem uso, renovação arriscada e vazamento de margem.","Manter read-only; escrita financeira exige gate."],
"repo-skill":["Identificar rotinas recorrentes que devem virar skill/script.","Auditar skills com ausência de evidência, gates ou critérios de aceite."],
"continuation":["Manter estado entre agentes/crons, reduzir drift e falsa conclusão.","Exigir status, stop_reason, real_evidence e next_action."]}
HUMAN_GATES=["envio externo por WhatsApp/Telegram/e-mail/DM","publicação de conteúdo","alteração de site, anúncio, orçamento, credencial ou permissão","escrita em Omie, QuarkClinic, financeiro ou sistemas sensíveis","ingestão canônica no cérebro/GBrain sem RC-25/Graphify","uso de login, cookies, paywall, dados de paciente/lead ou PII"]

def run_crawl(targets,out_dir):
    crawl_out=out_dir/"crawl"; cmd=["uv","run","python","-m","ivs_crawl4ai_sandbox.runner","--out",str(crawl_out)]
    for t in targets: cmd += ["--target",t]
    p=subprocess.run(cmd,cwd="/opt/ivs/ivs-crawl4ai-sandbox",text=True,capture_output=True,timeout=300)
    out_dir.mkdir(parents=True,exist_ok=True)
    (out_dir/"crawl.stdout.txt").write_text(p.stdout,encoding="utf-8"); (out_dir/"crawl.stderr.txt").write_text(p.stderr,encoding="utf-8")
    sp=crawl_out/"summary.json"
    if p.returncode or not sp.exists(): return {"status":"BLOCKED","error":p.stderr[-1000:] or "summary.json não gerado","summary_path":str(sp)}
    d=json.loads(sp.read_text(encoding="utf-8")); d["summary_path"]=str(sp); return d

def make_report(loop_type,goal,targets,out_dir,crawl):
    evidence=[]; status="DONE_WITH_CONCERNS"; stop="success_with_human_gate"
    if crawl.get("status")=="BLOCKED": status="BLOCKED"; stop="blocked"; evidence.append(f"Crawl bloqueado: {crawl.get('error','')}")
    else:
        ok=crawl.get("ok",0); blocked=crawl.get("blocked",0); status="DONE" if ok and not blocked else "DONE_WITH_CONCERNS"
        evidence += [f"Crawl summary: {crawl.get('summary_path')}", f"Targets OK: {ok}; bloqueados: {blocked}"]
        for r in crawl.get("results",[]): evidence.append(f"- {r.get('domain')} | {r.get('status')} | engine={r.get('engine')} | chars={r.get('markdown_chars')} | risk={(r.get('risk') or {}).get('medical_claim_risk')}")
    next_action="Definir dono/frequência e aprovar qualquer ação externa; até lá, manter como relatório interno read-only."
    state={"status":status,"stop_reason":stop,"loop_type":loop_type,"goal":goal,"targets":targets,"captured_at":datetime.now(timezone.utc).isoformat(),"evidence":evidence,"applications":LOOP_APPLICATIONS[loop_type],"human_gates":HUMAN_GATES,"next_action":next_action}
    lines=[f"# IVS Web Intelligence Loop — {loop_type}","",f"Status: {status}",f"Loop: {loop_type}",f"Stop reason: {stop}",f"Goal: {goal}","","## Evidence","",*evidence,"","## Applications","",*[f"- {x}" for x in LOOP_APPLICATIONS[loop_type]],"","## Human gates","",*[f"- {x}" for x in HUMAN_GATES],"","## Next action","",next_action,""]
    out_dir.mkdir(parents=True,exist_ok=True); (out_dir/"loop-state.json").write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding="utf-8"); (out_dir/"report.md").write_text("\n".join(lines),encoding="utf-8"); return state

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--loop-type",required=True,choices=sorted(LOOP_APPLICATIONS)); ap.add_argument("--goal",required=True); ap.add_argument("--target",action="append",default=[]); ap.add_argument("--out",required=True); a=ap.parse_args()
    out=Path(a.out); targets=a.target or ["https://blog.institutovitalslim.com.br/"]; state=make_report(a.loop_type,a.goal,targets,out,run_crawl(targets,out)); print(json.dumps({"status":state["status"],"out":str(out),"report":str(out/"report.md")},ensure_ascii=False)); return 0 if state["status"]!="BLOCKED" else 2
if __name__=="__main__": raise SystemExit(main())
