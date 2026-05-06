#!/usr/bin/env python3
import argparse, json, subprocess, datetime, calendar, os
from pathlib import Path
OUT=Path('/root/.openclaw/reports/clara-learning'); OUT.mkdir(parents=True, exist_ok=True)
SOC='/root/.openclaw/workspace/skills/rapidapi-social-learning/scripts/social_learning.py'
YT='/root/.openclaw/workspace/skills/youtube-learning-ivs/scripts/youtube_learning.py'
WEEK={0:('Patrick Dang','sales scripts discovery questions follow up'),1:('Alex Hormozi','value proposition offer sales objections'),2:('Gong','objection handling sales call review discovery questions'),3:('Chris Voss Shep Hyken','tactical empathy customer experience premium service'),4:('Camila Porto Thiago Concer G4 Educação','WhatsApp vendas vendas consultivas cadência follow-up'),5:('Grant Cardone Jordan Belfort','follow up tonality objection handling ethical closing'),6:('Will Guidara HubSpot','unreasonable hospitality sales process customer experience')}
IG_MORNING=['camilaporto','thiagoconcer','g4educacao','leandroladeira','pedrosobral']
IG_AFTERNOON=['dr.marlonbatista','dra.camilapaes','camilaporto','leandroladeira','thiagoconcer']

def run(cmd, timeout=80):
    try:
        cp=subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)
        return {'cmd':' '.join(cmd), 'returncode':cp.returncode, 'stdout':cp.stdout[-6000:], 'stderr':cp.stderr[-2000:]}
    except Exception as e:
        return {'cmd':' '.join(cmd), 'error':str(e)}

def save(slot, data):
    ts=datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    path=OUT/f'{ts}-{slot}.json'
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    latest=OUT/f'latest-{slot}.json'; latest.write_text(path.read_text())
    return str(path)

def day_index(): return datetime.datetime.now().weekday()

def slot(args):
    slot=args.slot; today=datetime.datetime.now(); idx=day_index()
    base={'slot':slot,'date':today.isoformat(),'weekday':calendar.day_name[idx],'regra':'Não copiar. Converter em abertura, pergunta, objeção, follow-up ou fechamento premium.'}
    if slot=='instagram_manha':
        user=IG_MORNING[today.timetuple().tm_yday % len(IG_MORNING)]
        base.update({'fonte':'Instagram','perfil':user,'buscar':'vendas consultivas, WhatsApp, atendimento premium','entrega':'1 insight + 1 pergunta curta de abertura + 1 frase proibida'})
        base['coleta']=run(['python3',SOC,'instagram-profile','--username',user,'--limit','3'])
    elif slot=='youtube':
        ch,topic=WEEK[idx]
        base.update({'fonte':'YouTube','canal_ou_busca':ch,'buscar':topic,'entrega':'ideia central + aplicação WhatsApp + script antes/depois + métrica + risco'})
        base['coleta']=run(['python3',YT,'search','--topic',f'{ch} {topic}','--limit','3'])
    elif slot=='x_twitter':
        base.update({'fonte':'X/Twitter','buscar':'posts de alto engajamento sobre persuasão, objeções, atendimento, negócios locais ou experiência do cliente','entrega':'1 frase curta + 1 ângulo de objeção + 1 cuidado contra agressividade'})
        base['coleta']=run(['python3',SOC,'x-top','--period','Daily','--type','Likes'])
    elif slot=='instagram_tarde':
        user=IG_AFTERNOON[(today.timetuple().tm_yday+2) % len(IG_AFTERNOON)]
        base.update({'fonte':'Instagram','perfil':user,'buscar':'SPIN, negociação, social selling ou clínica premium','entrega':'1 resposta ruim + 1 resposta Clara premium + 1 pergunta de avanço'})
        base['coleta']=run(['python3',SOC,'instagram-profile','--username',user,'--limit','3'])
    elif slot=='revisao':
        latest=[]
        for p in sorted(OUT.glob('latest-*.json')):
            try: latest.append(json.loads(p.read_text()))
            except Exception: pass
        base.update({'fonte':'Revisão interna','buscar':'aprendizados do dia','entrega':'classificar aplicar amanhã / descartar / testar 3 dias / propor memória','latest':latest})
    else:
        raise SystemExit('slot inválido')
    path=save(slot, base)
    print(json.dumps({'ok':True,'saved':path,'slot':slot,'entrega':base.get('entrega'),'buscar':base.get('buscar'),'fonte':base.get('fonte')}, ensure_ascii=False, indent=2))

ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest='cmd', required=True)
p=sub.add_parser('slot'); p.add_argument('--slot', required=True, choices=['instagram_manha','youtube','x_twitter','instagram_tarde','revisao']); p.set_defaults(func=slot)
args=ap.parse_args(); args.func(args)
