#!/usr/bin/env python3
"""Coleta temática Instagram via RapidAPI Stable API para o radar Content OS.
Read-only. Não publica/interage. Não imprime segredo.
"""
from __future__ import annotations
import argparse, json, os, re, time, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path

ENV_PATH=Path('/root/.openclaw/secure/rapidapi.env')
OUT_DIR=Path('/root/.openclaw/reports/social-learning')
OUT_DIR.mkdir(parents=True, exist_ok=True)
HOST='instagram-scraper-stable-api.p.rapidapi.com'

THEME_QUERIES={
  'emagrecimento':['emagrecimento','emagrecimento saudavel','mounjaro emagrecimento','menopausa emagrecimento','emagrecer depois dos 40'],
  'reposicao_hormonal':['reposicao hormonal','reposicaohormonal','terapia hormonal menopausa','hormonios femininos','menopausa sintomas'],
  'saude_preventiva':['saude preventiva','medicina preventiva','checkup medico','exames de rotina','prevencao saude'],
  'longevidade':['longevidade','envelhecimento saudavel','sarcopenia','musculo longevidade','saude apos 40'],
}
FALLBACK_TAGS={
  'emagrecimento':['emagrecimento','emagrecimentosaudavel','emagrecimentofeminino','mounjaro','obesidade','menopausaemagrecimento'],
  'reposicao_hormonal':['reposicaohormonal','terapiahormonal','menopausa','climaterio','hormonios','trh'],
  'saude_preventiva':['saudepreventiva','medicinapreventiva','checkup','prevencao','examesderotina','saudedamulher','checkupmedico','medicinaintegrativa'],
  'longevidade':['longevidade','envelhecimentosaudavel','sarcopenia','musculacao','saudeapos40','qualidadedevida','longevidadesaudavel','musculoelongevidade'],
}
BLACKLIST_TAG_PARTS=('pet','humor','meme','piada','posgravidez')

def load_key():
    key=os.environ.get('RAPIDAPI_KEY')
    if key: return key.strip()
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text().splitlines():
            if line.strip().startswith('RAPIDAPI_KEY='):
                return line.split('=',1)[1].strip().strip('"').strip("'")
    raise SystemExit('RAPIDAPI_KEY ausente')

def req(url, method='GET', data=None, timeout=45):
    headers={'x-rapidapi-host':HOST,'x-rapidapi-key':load_key(),'User-Agent':'IVS-theme-search/1.0'}
    body=None
    if data is not None:
        body=urllib.parse.urlencode(data).encode()
        headers['Content-Type']='application/x-www-form-urlencoded'
    else:
        headers['Content-Type']='application/json'
    request=urllib.request.Request(url, data=body, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=timeout) as r:
        return json.loads(r.read())

def search_ig(query):
    return req(f'https://{HOST}/search_ig.php', method='POST', data={'search_query':query})

def search_hashtag(tag):
    return req(f'https://{HOST}/search_hashtag.php?hashtag='+urllib.parse.quote(tag))

def norm_tag(s):
    s=(s or '').lower().strip().replace('#','')
    s=re.sub(r'[^a-z0-9áàâãéêíóôõúç]+','',s)
    s=(s.replace('á','a').replace('à','a').replace('â','a').replace('ã','a')
        .replace('é','e').replace('ê','e').replace('í','i').replace('ó','o')
        .replace('ô','o').replace('õ','o').replace('ú','u').replace('ç','c'))
    return s

def caption_of(node):
    edges=((node.get('edge_media_to_caption') or {}).get('edges') or [])
    if edges:
        return ((edges[0].get('node') or {}).get('text') or '')[:2500]
    cap=node.get('caption')
    if isinstance(cap,dict): return (cap.get('text') or '')[:2500]
    if isinstance(cap,str): return cap[:2500]
    return ''

def parse_posts(theme, tag, data, per_tag):
    edges=(((data or {}).get('posts') or {}).get('edges') or [])
    out=[]
    for e in edges[:per_tag]:
        n=(e or {}).get('node') or {}
        shortcode=n.get('shortcode') or n.get('code')
        if not shortcode: continue
        comments=((n.get('edge_media_to_comment') or {}).get('count') or n.get('comment_count') or 0)
        likes=((n.get('edge_liked_by') or {}).get('count') or n.get('like_count') or 0)
        is_video=bool(n.get('is_video') or n.get('video_url'))
        out.append({
          'theme':theme,'hashtag':tag,'shortcode':shortcode,
          'url':f'https://www.instagram.com/reel/{shortcode}/' if is_video else f'https://www.instagram.com/p/{shortcode}/',
          'format':'reel' if is_video else 'post',
          'caption':caption_of(n),'likes':int(likes or 0),'comments':int(comments or 0),
          'score':int(likes or 0)+5*int(comments or 0),
          'taken_at':n.get('taken_at_timestamp') or n.get('taken_at'),
          'owner':(n.get('owner') or {}).get('id'),
          'is_video':is_video,
        })
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--tags-per-theme',type=int,default=8)
    ap.add_argument('--posts-per-tag',type=int,default=8)
    args=ap.parse_args()
    trace={'collected_at':datetime.now(timezone.utc).isoformat(),'host':HOST,'themes':{},'items':[]}
    seen_short=set()
    for theme,queries in THEME_QUERIES.items():
        tags=[]; search_payloads=[]
        # Fallback curado vem antes para evitar long tails ruins da busca (ex.: pet/humor).
        for ft in FALLBACK_TAGS[theme]:
            nt=norm_tag(ft)
            if nt and nt not in tags: tags.append(nt)
        for q in queries:
            try:
                data=search_ig(q); search_payloads.append({'query':q,'ok':True,'raw_keys':list(data.keys())[:10]})
                # Stable API retorna keywords em see_more.list; hashtags podem aparecer separado dependendo da query.
                for row in (((data.get('see_more') or {}).get('list')) or []):
                    kw=((row or {}).get('keyword') or {}).get('name')
                    nt=norm_tag(kw)
                    if nt and nt not in tags and not any(b in nt for b in BLACKLIST_TAG_PARTS): tags.append(nt)
                for row in (data.get('hashtags') or []):
                    h=((row or {}).get('hashtag') or {}).get('name') or (row or {}).get('name')
                    nt=norm_tag(h)
                    if nt and nt not in tags and not any(b in nt for b in BLACKLIST_TAG_PARTS): tags.append(nt)
            except Exception as e:
                search_payloads.append({'query':q,'ok':False,'error':str(e)[:180]})
            time.sleep(0.4)
        tags=tags[:args.tags_per_theme]
        theme_items=[]; hashtag_reports=[]
        for tag in tags:
            try:
                data=search_hashtag(tag)
                posts=parse_posts(theme, tag, data, args.posts_per_tag)
                hashtag_reports.append({'hashtag':tag,'ok':True,'post_count':((data.get('posts') or {}).get('count') or data.get('count')),'items':len(posts)})
                for it in posts:
                    if it['shortcode'] in seen_short: continue
                    seen_short.add(it['shortcode']); theme_items.append(it); trace['items'].append(it)
            except Exception as e:
                hashtag_reports.append({'hashtag':tag,'ok':False,'error':str(e)[:180]})
            time.sleep(0.55)
        theme_items.sort(key=lambda x:x['score'], reverse=True)
        trace['themes'][theme]={'queries':queries,'selected_hashtags':tags,'search_payloads':search_payloads,'hashtag_reports':hashtag_reports,'top_shortcodes':[x['shortcode'] for x in theme_items[:10]],'items':len(theme_items)}
    trace['items'].sort(key=lambda x:x['score'], reverse=True)
    path=OUT_DIR/(datetime.now().strftime('%Y%m%d-%H%M%S')+'-instagram-theme-search-content-os.json')
    path.write_text(json.dumps(trace,ensure_ascii=False,indent=2))
    print(json.dumps({'ok':True,'saved':str(path),'themes':{k:v['items'] for k,v in trace['themes'].items()},'total_items':len(trace['items']),'top':[{'theme':x['theme'],'tag':x['hashtag'],'shortcode':x['shortcode'],'score':x['score'],'likes':x['likes'],'comments':x['comments']} for x in trace['items'][:12]]},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
