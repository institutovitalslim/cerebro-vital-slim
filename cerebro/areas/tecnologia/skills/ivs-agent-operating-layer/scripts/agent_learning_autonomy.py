#!/usr/bin/env python3
"""IVS Agent Learning Autonomy — read-only learning brief generator."""
import argparse, json, subprocess, sys, time
from pathlib import Path
from datetime import datetime, timezone

BASE=Path('/root/.openclaw/workspace/skills/ivs-agent-operating-layer')
REG=BASE/'learning/agent-learning-registry.json'
OUT_DIR=Path('/root/.openclaw/reports/ivs-agent-learning')
SOCIAL=Path('/root/.openclaw/workspace/skills/rapidapi-social-learning/scripts/social_learning.py')
YOUTUBE=Path('/root/.openclaw/workspace/skills/youtube-learning-ivs/scripts/youtube_learning.py')

def run_cmd(cmd, timeout=60):
    try:
        p=subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)
        return {'ok':p.returncode==0,'returncode':p.returncode,'stdout':p.stdout[-4000:],'stderr':p.stderr[-2000:]}
    except Exception as e:
        return {'ok':False,'error':str(e)}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--agent', help='Filtra um agente por id')
    ap.add_argument('--collect', action='store_true', help='Executa planos locais social/youtube quando disponíveis')
    ap.add_argument('--json', action='store_true')
    args=ap.parse_args()
    reg=json.loads(REG.read_text(encoding='utf-8'))
    agents=[a for a in reg['agents'] if not args.agent or a['id']==args.agent]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ts=int(time.time()); stamp=datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
    external={}
    if args.collect:
        if SOCIAL.exists(): external['social_daily_plan']=run_cmd([sys.executable,str(SOCIAL),'daily-plan'], timeout=120)
        if YOUTUBE.exists(): external['youtube_plan']=run_cmd([sys.executable,str(YOUTUBE),'plan'], timeout=120)
    briefs=[]
    weekday=datetime.now().strftime('%A')
    for a in agents:
        brief={
            'agent_id':a['id'], 'name':a['name'], 'domain':a['domain'],
            'learning_focus_today': a['learning_goals'][ts % len(a['learning_goals'])] if a.get('learning_goals') else None,
            'source_plan': {
                'research': a.get('learning_goals',[])[:3],
                'instagram_x': a.get('instagram_x_topics',[])[:4],
                'youtube': a.get('youtube_channels_or_queries',[])[:4]
            },
            'operational_hypothesis': f"Buscar um aprendizado aplicável a {a['domain']} e converter em teste pequeno, seguro e mensurável.",
            'application': a.get('output_use'),
            'metric': '1 evidência operacional antes/depois ou 1 decisão melhor suportada por dados',
            'risk_filter': reg['governance']['filters'],
            'classification_required': reg['governance']['classification'],
            'promotion_rule': reg['governance']['promotion_rule']
        }
        briefs.append(brief)
    report={'ok':True,'generated_at':ts,'weekday':weekday,'mode':'read_only_learning_autonomy','registry_version':reg['version'],'governance':reg['governance'],'external_collections':external,'briefs':briefs}
    json_path=OUT_DIR/f'{stamp}-agent-learning-autonomy.json'
    md_path=OUT_DIR/f'{stamp}-agent-learning-autonomy.md'
    latest_json=OUT_DIR/'latest-agent-learning-autonomy.json'
    latest_md=OUT_DIR/'latest-agent-learning-autonomy.md'
    json_path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    latest_json.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    lines=['# IVS Agent Learning Autonomy','',f'Gerado em: `{stamp} UTC`','',f'Modo: `{report["mode"]}`','', '## Governança', f'- {reg["governance"]["principle"]}', f'- Promoção: {reg["governance"]["promotion_rule"]}', '', '## Briefs por agente']
    for b in briefs:
        lines += ['', f'### {b["name"]} (`{b["agent_id"]}`)', f'- Domínio: {b["domain"]}', f'- Foco de hoje: **{b["learning_focus_today"]}**', f'- Instagram/X: {", ".join(b["source_plan"]["instagram_x"])}', f'- YouTube: {", ".join(b["source_plan"]["youtube"])}', f'- Aplicação: {b["application"]}', f'- Métrica: {b["metric"]}', '- Classificação obrigatória: aplicar amanhã / testar 3 dias / descartar / propor RC-25']
    if external:
        lines += ['', '## Coletas locais', '```json', json.dumps(external,ensure_ascii=False,indent=2)[:6000], '```']
    md_path.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    latest_md.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({'ok':True,'json':str(json_path),'md':str(md_path),'briefs':len(briefs)},ensure_ascii=False))
if __name__=='__main__': main()
