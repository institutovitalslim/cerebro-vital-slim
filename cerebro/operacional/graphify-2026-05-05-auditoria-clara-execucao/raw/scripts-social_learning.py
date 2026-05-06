#!/usr/bin/env python3
import argparse, json, os, sys, urllib.parse, urllib.request
from pathlib import Path
from datetime import datetime

ENV_PATH = Path('/root/.openclaw/secure/rapidapi.env')
OUT_DIR = Path('/root/.openclaw/reports/social-learning')
OUT_DIR.mkdir(parents=True, exist_ok=True)

def load_key():
    key=os.environ.get('RAPIDAPI_KEY')
    if key: return key.strip()
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text().splitlines():
            line=line.strip()
            if line.startswith('RAPIDAPI_KEY='):
                return line.split('=',1)[1].strip().strip('"').strip("'")
    raise SystemExit('RAPIDAPI_KEY ausente. Configure /root/.openclaw/secure/rapidapi.env')

def get_json(url, host, timeout=35):
    req=urllib.request.Request(url, headers={
        'x-rapidapi-host': host,
        'x-rapidapi-key': load_key(),
        'User-Agent': 'IVS-social-learning/1.0'
    })
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw=r.read()
    try: return json.loads(raw)
    except Exception: return {'raw': raw.decode('utf-8','replace')[:4000]}

def post_json(url, host, payload, timeout=35):
    body=json.dumps(payload).encode()
    req=urllib.request.Request(url, data=body, headers={
        'content-type':'application/json',
        'x-rapidapi-host': host,
        'x-rapidapi-key': load_key(),
        'User-Agent': 'IVS-social-learning/1.0'
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())
    except Exception as e:
        return {'error': str(e), 'host': host}

def save(label, data):
    ts=datetime.now().strftime('%Y%m%d-%H%M%S')
    path=OUT_DIR / f'{ts}-{label}.json'
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    return str(path)

def instagram_url(args):
    enc=urllib.parse.quote(args.url, safe='')
    host='instagram-scraper-stable-api.p.rapidapi.com'
    url=f'https://{host}/get_media_data.php?reel_post_code_or_url={enc}&type=post'
    data=get_json(url, host)
    path=save('instagram-url', data)
    print(json.dumps({'ok': True, 'source':'instagram-url', 'saved':path, 'summary': summarize_ig_item(data)}, ensure_ascii=False, indent=2))

def instagram_profile(args):
    host='instagram120.p.rapidapi.com'
    url=f'https://{host}/api/instagram/posts'
    data=post_json(url, host, {'username': args.username, 'maxId': ''})
    items=[]
    if data.get('error'):
        out={'username':args.username,'items':[],'error':data.get('error')}
        path=save(f'instagram-profile-{args.username}', out)
        print(json.dumps({'ok': False, 'source':'instagram-profile', 'saved':path, 'error':data.get('error')}, ensure_ascii=False, indent=2))
        return
    result=data.get('result',{})
    edges=(result.get('data',{}).get('user',{}).get('edge_owner_to_timeline_media',{}).get('edges',[])
           or result.get('edges',[])
           or data.get('edges',[]))
    for e in edges[:args.limit]:
        n=e.get('node',{})
        cap_edges=n.get('edge_media_to_caption',{}).get('edges',[])
        cap=cap_edges[0].get('node',{}).get('text','') if cap_edges else ''
        items.append({'shortcode':n.get('shortcode'),'caption':cap[:1200],'likes':n.get('edge_liked_by',{}).get('count'),'comments':n.get('edge_media_to_comment',{}).get('count'),'taken_at':n.get('taken_at_timestamp')})
    out={'username':args.username,'items':items,'raw_available': bool(data)}
    path=save(f'instagram-profile-{args.username}', out)
    print(json.dumps({'ok': True, 'source':'instagram-profile', 'saved':path, 'items':items}, ensure_ascii=False, indent=2))

def x_top(args):
    host='twitter-api45.p.rapidapi.com'
    q=urllib.parse.urlencode({'type':args.type,'country':args.country,'period':args.period})
    url=f'https://{host}/top_posts.php?{q}'
    data=get_json(url, host)
    path=save('x-top-posts', data)
    timeline=data.get('timeline') or data.get('data') or []
    print(json.dumps({'ok': True, 'source':'x-top', 'saved':path, 'count': len(timeline) if isinstance(timeline,list) else None, 'sample': timeline[:5] if isinstance(timeline,list) else timeline}, ensure_ascii=False, indent=2))

def summarize_ig_item(data):
    cap=data.get('caption') or ''
    if not cap:
        edges=data.get('edge_media_to_caption',{}).get('edges',[])
        if edges: cap=edges[0].get('node',{}).get('text','')
    owner=(data.get('owner') or {}).get('username') or (data.get('user') or {}).get('username')
    return {'owner':owner,'caption':cap[:1000],'shortcode':data.get('shortcode')}

def daily_plan(args):
    plan={
      '07:10': {'fonte':'Instagram', 'buscar':'1 post/reel recente de vendas consultivas, WhatsApp, atendimento premium ou clínica premium', 'objetivo':'extrair 1 pergunta melhor para abrir conversas'},
      '12:40': {'fonte':'X/Twitter', 'buscar':'posts de alto engajamento sobre persuasão, objeções, atendimento, negócios locais, experiência do cliente', 'objetivo':'extrair 1 frase curta ou ângulo de objeção'},
      '17:40': {'fonte':'Instagram', 'buscar':'1 conteúdo de referência em SPIN, negociação ou social selling', 'objetivo':'transformar em 2 scripts WhatsApp: antes/depois'},
      '21:20': {'fonte':'Relatório interno', 'buscar':'conversas do dia e aprendizados coletados', 'objetivo':'decidir o treino de amanhã e propor atualização se houver padrão recorrente'}
    }
    print(json.dumps({'ok':True,'rotina_diaria_clara':plan,'perfis_semente':DEFAULT_SEEDS}, ensure_ascii=False, indent=2))

DEFAULT_SEEDS={
 'instagram_vendas_whatsapp':['camilaporto','leandroladeira','pedrosobral','icaro.de.carvalho'],
 'vendas_consultivas':['thiagoconcer','g4educacao'],
 'premium_experiencia':['willguidara','shephyken'],
 'medicina_premium_validar_antes':['dr.marlonbatista','dra.camilapaes']
}

def main():
    ap=argparse.ArgumentParser()
    sub=ap.add_subparsers(dest='cmd', required=True)
    p=sub.add_parser('instagram-url'); p.add_argument('--url', required=True); p.set_defaults(func=instagram_url)
    p=sub.add_parser('instagram-profile'); p.add_argument('--username', required=True); p.add_argument('--limit', type=int, default=5); p.set_defaults(func=instagram_profile)
    p=sub.add_parser('x-top'); p.add_argument('--type', default='Likes'); p.add_argument('--country', default='ALL'); p.add_argument('--period', default='Daily'); p.set_defaults(func=x_top)
    p=sub.add_parser('daily-plan'); p.set_defaults(func=daily_plan)
    args=ap.parse_args(); args.func(args)
if __name__=='__main__': main()
