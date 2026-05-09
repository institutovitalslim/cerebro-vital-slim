#!/usr/bin/env python3
import argparse, json, time
from pathlib import Path
BASE=Path('/root/.openclaw/workspace/skills/ivs-agent-operating-layer')
DEL=Path('/root/deliverables')
ARTIFACTS=[
('Cockpit Único','/root/deliverables/cockpit-unico-ivs-agent-os.html'),('Cockpit Vivo','/root/deliverables/cockpit-vivo-ivs-agent-os.html'),('Workflow Runs','/root/deliverables/cockpit-workflow-runs-ivs.html'),('Trends','/root/deliverables/agent-os-trends.html'),('Approval Console','/root/deliverables/approval-console-ivs-agent-os.html'),('Critical Alerts','/root/deliverables/agent-os-critical-alerts-latest.json')]
CMDS=[('Status completo','python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/agent_os_cli.py status'),('Atualizar painéis','python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/agent_os_cli.py refresh-all'),('Rodar testes','python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/agent_os_cli.py test'),('Backup read-only','python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/agent_os_cli.py backup'),('Avaliar gate Omie','python3 /root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/agent_os_cli.py gate --agent pedro-controller-ivs --action omie_write --sensitivity financial')]
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--out',default='/root/deliverables/runbook-ivs-agent-os.md'); ap.add_argument('--json-out',default='/root/deliverables/runbook-ivs-agent-os.json'); args=ap.parse_args()
 report={'ok':True,'generated_at':int(time.time()),'artifacts':[{'name':n,'path':p,'exists':Path(p).exists()} for n,p in ARTIFACTS],'commands':[{'name':n,'command':c} for n,c in CMDS],'guardrails':['read-only por padrão','Action Gate não executa ação','Approval Console estático não cria aprovação','Clara/Z-API enforcement forte é opt-in','backup não poda sem --prune']}
 Path(args.json_out).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 lines=['# Runbook IVS Agent OS','',f"Gerado em: `{report['generated_at']}`",'','## Guardrails']+[f"- {x}" for x in report['guardrails']]+['','## Comandos operacionais']
 for c in report['commands']: lines += [f"### {c['name']}", '```bash', c['command'], '```','']
 lines += ['## Artefatos']
 for a in report['artifacts']: lines.append(f"- {a['name']}: `{a['path']}` — {'OK' if a['exists'] else 'faltando'}")
 lines += ['','## Protocolo de incidente','1. Rodar `agent_os_cli.py status`.','2. Se HIGH/MEDIUM, abrir run no Workflow Runner.','3. Não executar ação sensível sem Action Gate + Approval Ledger.','4. Para Clara, nunca pausar sem ordem explícita do Tiaro.','5. Registrar RC-25 para mudança canônica.']
 Path(args.out).write_text('\n'.join(lines)+'\n',encoding='utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
