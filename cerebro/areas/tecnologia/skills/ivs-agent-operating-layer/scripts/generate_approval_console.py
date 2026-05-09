#!/usr/bin/env python3
import argparse, json, time, html
from pathlib import Path
BASE=Path('/root/.openclaw/workspace/skills/ivs-agent-operating-layer')
LEDGER=BASE/'approvals/approval-ledger.jsonl'
ACTIONS=['pause_clara','followup_whatsapp','omie_write','publish_external_content']
AGENTS=['maria-gerente','clara-whatsapp','pedro-controller-ivs','agente-reels-intel']
def load():
    out=[]
    if LEDGER.exists():
        for line in LEDGER.read_text(encoding='utf-8',errors='ignore').splitlines():
            try: out.append(json.loads(line))
            except Exception: pass
    return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--out',default='/root/deliverables/approval-console-ivs-agent-os.html'); ap.add_argument('--json-out',default='/root/deliverables/approval-console-ivs-agent-os.json'); args=ap.parse_args()
    rows=load(); now=time.time(); active=[r for r in rows if int(r.get('expires_at') or 0)>=now]
    report={'ok':True,'generated_at':int(now),'totals':{'approvals':len(rows),'active':len(active),'expired':len(rows)-len(active)},'mode':'static_console_no_execution','allowed_actions':ACTIONS,'agents':AGENTS}
    Path(args.json_out).parent.mkdir(parents=True,exist_ok=True); Path(args.json_out).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    trs=''.join(f"<tr><td>{html.escape(r.get('approval_id',''))}</td><td>{html.escape(r.get('agent',''))}</td><td>{html.escape(r.get('action',''))}</td><td>{html.escape(r.get('approved_by',''))}</td><td>{'ativa' if int(r.get('expires_at') or 0)>=now else 'expirada'}</td><td>{html.escape(str(r.get('scope','')))}</td></tr>" for r in rows[-50:]) or '<tr><td colspan="6">Sem aprovações</td></tr>'
    cmd="python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/approval_ledger.py add --agent AGENTE --action ACAO --approved-by Tiaro --evidence 'EVIDENCIA' --scope 'ESCOPO' --ttl-minutes 60"
    doc=f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>IVS Agent OS — Approval Console</title><style>body{{font-family:Inter,Arial,sans-serif;margin:0;background:#0b1020;color:#eef;padding:24px}}.card{{background:#151d36;border:1px solid #2b365d;border-radius:16px;padding:18px;margin:12px 0}}table{{width:100%;border-collapse:collapse}}td,th{{border-bottom:1px solid #2b365d;padding:8px;text-align:left}}code,pre{{background:#080c18;padding:10px;border-radius:10px;display:block;white-space:pre-wrap}}</style></head><body><h1>IVS Agent OS — Approval Console</h1><p>Console estático/read-only. Não cria aprovação e não executa ação.</p><div class="card"><h2>Comando seguro para registrar aprovação</h2><pre>{html.escape(cmd)}</pre></div><div class="card"><h2>Aprovações recentes</h2><table><tr><th>ID</th><th>Agente</th><th>Ação</th><th>Aprovador</th><th>Status</th><th>Escopo</th></tr>{trs}</table></div></body></html>'''
    Path(args.out).write_text(doc,encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
