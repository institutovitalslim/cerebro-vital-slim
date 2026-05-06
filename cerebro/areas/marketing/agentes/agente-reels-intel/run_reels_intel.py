#!/usr/bin/env python3
import json, sys, urllib.parse, urllib.request, pathlib, datetime, re

BASE = pathlib.Path('/root/cerebro-vital-slim/cerebro/areas/marketing/agentes/agente-reels-intel')
INPUTS = BASE / 'inputs'
OUTPUTS = BASE / 'outputs'
INPUTS.mkdir(parents=True, exist_ok=True)
OUTPUTS.mkdir(parents=True, exist_ok=True)

API_URL = 'https://instagram-scraper-stable-api.p.rapidapi.com/get_media_data.php'
API_HOST = 'instagram-scraper-stable-api.p.rapidapi.com'
API_KEY = 'cf7bd568f0msh846185e42b5253bp1d7915jsne0d2cb9e3b56'


def normalize_instagram_url(url: str) -> str:
    url = (url or '').strip()
    if not url:
        return url
    parsed = urllib.parse.urlparse(url)
    path = parsed.path.rstrip('/')
    m = re.search(r'/(reel|p)/([^/]+)$', path)
    if m:
        kind, code = m.group(1), m.group(2)
        return f"https://www.instagram.com/{kind}/{code}/"
    return url


def fetch_media(url: str):
    clean_url = normalize_instagram_url(url)
    errors = []
    for candidate in [clean_url, url]:
        if not candidate:
            continue
        enc = urllib.parse.quote(candidate, safe='')
        full = f"{API_URL}?reel_post_code_or_url={enc}&type=reel"
        req = urllib.request.Request(full, headers={
            'x-rapidapi-host': API_HOST,
            'x-rapidapi-key': API_KEY,
            'User-Agent': 'Mozilla/5.0'
        })
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read().decode('utf-8')
                data = json.loads(body)
                if isinstance(data, dict) and not data.get('error'):
                    return data
                errors.append({'candidate': candidate, 'body': body[:500]})
        except Exception as e:
            errors.append({'candidate': candidate, 'error': str(e)})
    raise RuntimeError(json.dumps(errors, ensure_ascii=False))


def first_caption_text(data):
    try:
        return data['edge_media_to_caption']['edges'][0]['node']['text']
    except Exception:
        return ''


def infer_hook(caption):
    if not caption:
        return ''
    first_para = caption.strip().split('\n\n')[0].strip()
    first_line = first_para.split('\n')[0].strip()
    return first_line[:220]


def infer_cta(caption):
    text = (caption or '').lower()
    for marker in ['follow @', 'comente', 'salve', 'clique', 'me chama', 'agende', 'envie']:
        if marker in text:
            return marker
    return ''


def build_output(data, request_payload):
    caption = first_caption_text(data)
    hook = infer_hook(caption)
    cta = infer_cta(caption)
    author = data.get('owner', {}).get('username', '')
    shortcode = data.get('shortcode', '')
    duration = data.get('video_duration', '')
    plays = data.get('video_play_count', '') or data.get('video_view_count', '')
    now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')

    md = f'''# Output — Agente Reels Intel

Gerado em: {now}

## Referência analisada
- URL: {request_payload.get('url','')}
- Shortcode: {shortcode}
- Autor: @{author}
- Tipo: {'reel' if data.get('is_video') else 'post'}
- Duração: {duration}
- Views/Plays: {plays}

## Hook
{hook}

## Tese
[preencher análise]

## Emoção dominante
[preencher análise]

## CTA
{cta or '[não inferido automaticamente]'}

## Estrutura
[preencher análise]

## Padrão visual
[preencher análise]

## Por que funciona
[preencher análise]

## Classificação IVS
- Dominante: [preencher]
- Secundária: [opcional]

## Como adaptar para o IVS
[preencher análise]

## 3 hooks IVS
1. 
2. 
3. 

## Roteiro de reel
[preencher]

## Ideia de carrossel
[preencher]

## Ângulo de anúncio
[preencher]

## Nota de compliance
[preencher]

## Promoção de aprendizado
- [ ] há padrão novo a promover para doc canônico
- Observações:

---

## Caption bruta
{caption}
'''
    return md


def main():
    if len(sys.argv) != 2:
        print('Uso: run_reels_intel.py <input.json>', file=sys.stderr)
        sys.exit(1)
    in_path = pathlib.Path(sys.argv[1])
    payload = json.loads(in_path.read_text())
    data = fetch_media(payload['url'])
    stem = datetime.datetime.utcnow().strftime('%Y%m%d-%H%M%S') + '-' + (data.get('shortcode') or 'sem-shortcode')
    raw_path = INPUTS / f'{stem}.raw.json'
    out_path = OUTPUTS / f'{stem}.md'
    raw_path.write_text(json.dumps({'request': payload, 'response': data}, ensure_ascii=False, indent=2))
    out_path.write_text(build_output(data, payload))
    print(out_path)

if __name__ == '__main__':
    main()
