#!/usr/bin/env python3
import argparse, json, subprocess, sys
from pathlib import Path
from datetime import datetime

OUT=Path('/root/.openclaw/reports/youtube-learning')
OUT.mkdir(parents=True, exist_ok=True)

CHANNELS={
  'prioridade_1': [
    {'nome':'Alex Hormozi','url':'https://www.youtube.com/@alexhormozi','buscar':['value proposition','offer','sales objections','closing']},
    {'nome':'Patrick Dang','url':'https://www.youtube.com/@patrickdang','buscar':['sales scripts','follow up','discovery questions','objection handling']},
    {'nome':'Gong','url':'https://www.youtube.com/c/Gongio','buscar':['objection handling','sales call review','discovery questions','follow up']},
  ],
  'prioridade_2': [
    {'nome':'HubSpot','url':'https://youtube.com/user/HubSpot','buscar':['sales process','lead qualification','follow up','CRM']},
    {'nome':'Chris Voss / Black Swan Group','url':'buscar no YouTube por Chris Voss / Black Swan Group','buscar':['tactical empathy','mirroring','labeling','negotiation questions']},
    {'nome':'Shep Hyken','url':'buscar no YouTube por Shep Hyken','buscar':['customer service','customer experience','hospitality']},
    {'nome':'Will Guidara','url':'buscar no YouTube por Will Guidara Unreasonable Hospitality','buscar':['unreasonable hospitality','premium service','customer experience']},
  ],
  'prioridade_3_com_filtro': [
    {'nome':'Jordan Belfort','url':'buscar no YouTube por Jordan Belfort official','buscar':['tonality','objection handling','straight line persuasion']},
    {'nome':'Grant Cardone','url':'https://www.youtube.com/@GrantCardone','buscar':['follow up','sales discipline','closing objections']},
  ],
  'brasil_social_selling': [
    {'nome':'Camila Porto','url':'buscar no YouTube por Camila Porto','buscar':['WhatsApp vendas','Instagram vendas','atendimento WhatsApp']},
    {'nome':'Leandro Ladeira','url':'buscar no YouTube por Leandro Ladeira','buscar':['oferta','copy','vendas online','mensagem de vendas']},
    {'nome':'Pedro Sobral','url':'buscar no YouTube por Pedro Sobral','buscar':['tráfego para WhatsApp','leads','funil','remarketing']},
    {'nome':'Ícaro de Carvalho','url':'buscar no YouTube por Ícaro de Carvalho','buscar':['copywriting','persuasão','storytelling']},
    {'nome':'Thiago Concer','url':'buscar no YouTube por Thiago Concer','buscar':['vendas consultivas','prospecção','objeções']},
    {'nome':'César Frazão','url':'buscar no YouTube por César Frazão','buscar':['técnicas de vendas','atendimento','fechamento']},
    {'nome':'G4 Educação','url':'buscar no YouTube por G4 Educação','buscar':['vendas','growth','atendimento','CRM']},
  ]
}

DAY_PLAN={
  'segunda': {'canal':'Patrick Dang', 'tema':'sales scripts + discovery questions', 'entrega':'1 abertura e 1 pergunta SPIN'},
  'terça': {'canal':'Alex Hormozi', 'tema':'valor percebido + oferta', 'entrega':'1 frase para gerar valor antes de preço'},
  'quarta': {'canal':'Gong', 'tema':'objection handling + call review', 'entrega':'2 respostas para objeção'},
  'quinta': {'canal':'Chris Voss / Shep Hyken', 'tema':'perguntas, empatia tática e atendimento premium', 'entrega':'1 pergunta de segurança e 1 frase de acolhimento'},
  'sexta': {'canal':'Camila Porto / Thiago Concer / G4 Educação', 'tema':'WhatsApp, vendas consultivas Brasil e cadência', 'entrega':'1 follow-up premium'},
  'sábado': {'canal':'Grant Cardone / Jordan Belfort com filtro ético', 'tema':'persistência, tonalidade e condução', 'entrega':'1 condução firme sem agressividade'},
  'domingo': {'canal':'Will Guidara / HubSpot', 'tema':'experiência premium + processo', 'entrega':'1 melhoria no SOP da Clara'}
}

def save(label, data):
    p=OUT/(datetime.now().strftime('%Y%m%d-%H%M%S')+'-'+label+'.json')
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    return str(p)

def plan(args):
    data={'channels':CHANNELS,'day_plan':DAY_PLAN,'how_to_extract':['ideia central','como aplicar no WhatsApp IVS','script antes/depois','métrica de teste','risco de uso errado']}
    print(json.dumps(data, ensure_ascii=False, indent=2))

def search(args):
    q=f"ytsearch{args.limit}:{args.topic}"
    cmd=['yt-dlp','--dump-json','--skip-download',q]
    try:
        cp=subprocess.run(cmd, text=True, capture_output=True, timeout=60)
    except Exception as e:
        print(json.dumps({'ok':False,'error':str(e)}, ensure_ascii=False)); return
    items=[]
    for line in cp.stdout.splitlines():
        try:
            d=json.loads(line)
            items.append({'title':d.get('title'),'url':d.get('webpage_url'),'channel':d.get('channel'),'duration':d.get('duration'),'view_count':d.get('view_count')})
        except Exception: pass
    path=save('search', {'topic':args.topic,'items':items,'stderr':cp.stderr[-1000:]})
    print(json.dumps({'ok':cp.returncode==0,'saved':path,'items':items[:args.limit],'stderr':cp.stderr[-500:]}, ensure_ascii=False, indent=2))

def transcript(args):
    # Prefer youtube_transcript_api CLI if available; fallback to yt-dlp auto subtitles metadata.
    cmd=['youtube_transcript_api', args.url]
    try:
        cp=subprocess.run(cmd, text=True, capture_output=True, timeout=60)
        text=cp.stdout.strip()
        if text:
            path=save('transcript', {'url':args.url,'transcript':text[:50000]})
            print(json.dumps({'ok':True,'saved':path,'chars':len(text)}, ensure_ascii=False, indent=2)); return
    except Exception:
        pass
    print(json.dumps({'ok':False,'error':'transcript não disponível automaticamente; usar busca manual/resumo do vídeo.'}, ensure_ascii=False, indent=2))

def main():
    ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest='cmd', required=True)
    p=sub.add_parser('plan'); p.set_defaults(func=plan)
    p=sub.add_parser('search'); p.add_argument('--topic', required=True); p.add_argument('--limit', type=int, default=5); p.set_defaults(func=search)
    p=sub.add_parser('transcript'); p.add_argument('--url', required=True); p.set_defaults(func=transcript)
    args=ap.parse_args(); args.func(args)
if __name__=='__main__': main()
