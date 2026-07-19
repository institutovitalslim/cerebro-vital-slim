#!/usr/bin/env python3
"""Fase 4 Motion Videos: coleta temática governada e ingere exemplos reais.

Read-only em fontes externas; não publica, não envia DM, não baixa mídia e não expõe chaves.
Converte resultados públicos do Instagram em content_format_examples via endpoint interno.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ENV_PATH = Path('/root/.openclaw/secure/rapidapi.env')
OUT_DIR = Path('/root/.openclaw/reports/social-learning')
OUT_DIR.mkdir(parents=True, exist_ok=True)
HOST = 'instagram-scraper-stable-api.p.rapidapi.com'
DEFAULT_TAGS = {
    'menopausa': ['menopausa', 'climaterio', 'fogachos', 'menopausaemagrecimento', 'terapiahormonal', 'saudedamulher', 'mulheres40mais', 'reposicaohormonal'],
}


def load_key() -> str:
    key = os.environ.get('RAPIDAPI_KEY')
    if key:
        return key.strip()
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text().splitlines():
            line = line.strip()
            if line.startswith('RAPIDAPI_KEY='):
                return line.split('=', 1)[1].strip().strip('"').strip("'")
    raise SystemExit('RAPIDAPI_KEY ausente')


def req_json(url: str, timeout: int = 45) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={
        'x-rapidapi-host': HOST,
        'x-rapidapi-key': load_key(),
        'User-Agent': 'IVS-motion-video-phase4/1.0',
        'Content-Type': 'application/json',
    })
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read())


def caption_of(node: dict[str, Any]) -> str:
    edges = ((node.get('edge_media_to_caption') or {}).get('edges') or [])
    if edges:
        return ((edges[0].get('node') or {}).get('text') or '')[:2500]
    cap = node.get('caption')
    if isinstance(cap, dict):
        return (cap.get('text') or '')[:2500]
    if isinstance(cap, str):
        return cap[:2500]
    return ''


def parse_hashtag_posts(topic: str, tag: str, data: dict[str, Any], limit: int) -> list[dict[str, Any]]:
    edges = (((data or {}).get('posts') or {}).get('edges') or [])
    out = []
    for edge in edges[:limit]:
        node = (edge or {}).get('node') or {}
        shortcode = node.get('shortcode') or node.get('code')
        if not shortcode:
            continue
        comments = ((node.get('edge_media_to_comment') or {}).get('count') or node.get('comment_count') or 0)
        likes = ((node.get('edge_liked_by') or {}).get('count') or node.get('like_count') or 0)
        is_video = bool(node.get('is_video') or node.get('video_url'))
        caption = caption_of(node)
        # filtro simples para manter aderência temática e reduzir ruído/idiomas long tail
        searchable = f"{caption} #{tag}".lower()
        if topic.lower() not in searchable and 'climaterio' not in searchable and 'fogacho' not in searchable:
            continue
        out.append({
            'topic': topic,
            'hashtag': tag,
            'shortcode': shortcode,
            'url': f"https://www.instagram.com/reel/{shortcode}/" if is_video else f"https://www.instagram.com/p/{shortcode}/",
            'format': 'reel' if is_video else 'post',
            'caption': caption,
            'likes': int(likes or 0),
            'comments': int(comments or 0),
            'score': int(likes or 0) + 5 * int(comments or 0),
            'taken_at': node.get('taken_at_timestamp') or node.get('taken_at'),
            'is_video': is_video,
        })
    return out


def choose_content_format(caption: str) -> str:
    text = (caption or '').lower()
    if any(term in text for term in ['não é', 'nao e', 'mito', 'frescura', 'normal']):
        return 'sinal_escondido'
    if any(term in text for term in ['antes de', 'posso fazer', 'terapia hormonal', 'reposi']):
        return 'antes_da_decisao'
    if any(term in text for term in ['erro', 'não faça', 'nao faca']):
        return 'erro_comum'
    if any(term in text for term in ['checklist', 'sinais', 'sintomas']):
        return 'checklist_rapido'
    return 'mini_aula_visual'


def compact(text: str, limit: int = 500) -> str:
    clean = re.sub(r'\s+', ' ', (text or '')).strip()
    return clean[:limit]


def build_ingest_payload(item: dict[str, Any], topic: str = 'menopausa') -> dict[str, Any]:
    caption = item.get('caption') or ''
    content_format = choose_content_format(caption)
    shortcode = item.get('shortcode') or ''
    return {
        'tenant_slug': 'demo',
        'content_format': content_format,
        'source_type': 'rapidapi_instagram_theme_search',
        'source_handle_or_url': f"theme_search:{topic}:{item.get('hashtag')}",
        'external_id': f"instagram:{shortcode}",
        'content_url': item.get('url'),
        'transcript_summary': compact(caption, 520) or f"Conteúdo público sobre {topic}; caption ausente no payload.",
        'hook_summary': compact((caption.split('\n')[0] if caption else f"Referência pública sobre {topic}"), 180),
        'why_this_example_works': 'Referência real usada apenas para abstrair mecanismo, hook e retenção; não copiar texto, edição, legenda ou claim clínico.',
        'retention_mechanism': 'theme_search_public_signal',
        'compliance_risk': 'review_required',
        'ivs_applicability_score': max(40, min(95, 65 + int(item.get('score') or 0) // 20)),
        'winner_candidate_type': 'pending',
        'metrics': {'likes': item.get('likes') or 0, 'comments': item.get('comments') or 0, 'score': item.get('score') or 0},
        'raw_payload_summary': json.dumps({'hashtag': item.get('hashtag'), 'format': item.get('format'), 'is_video': item.get('is_video')}, ensure_ascii=False),
    }


def demo_cookie() -> str:
    code = r'''
from app.db import get_conn
from app.auth_core import make_token
with get_conn() as conn, conn.cursor() as cur:
    cur.execute("select u.id::text as id, u.tenant_id::text as tenant_id, u.email from users u join tenants t on t.id=u.tenant_id where t.slug=%s limit 1", ("demo",))
    u=cur.fetchone()
print("cos_session=" + make_token(u["id"], u["tenant_id"], u["email"], ttl=900))
'''
    return subprocess.check_output(['docker', 'exec', 'content-engine-api', 'python', '-c', code], text=True).strip()


def post_internal(base: str, payload: dict[str, Any]) -> dict[str, Any]:
    body = json.dumps(payload).encode()
    req = urllib.request.Request(
        f'{base}/motion-videos/ingest-example',
        data=body,
        method='POST',
        headers={'Content-Type': 'application/json', 'Cookie': demo_cookie(), 'User-Agent': 'IVS-motion-video-phase4/1.0'},
    )
    with urllib.request.urlopen(req, timeout=45) as response:
        return json.loads(response.read())


def collect(topic: str, tags: list[str], posts_per_tag: int) -> list[dict[str, Any]]:
    seen = set()
    items: list[dict[str, Any]] = []
    for tag in tags:
        try:
            data = req_json(f'https://{HOST}/search_hashtag.php?hashtag=' + urllib.parse.quote(tag))
            for item in parse_hashtag_posts(topic, tag, data, posts_per_tag):
                if item['shortcode'] in seen:
                    continue
                seen.add(item['shortcode'])
                items.append(item)
        except Exception as exc:
            items.append({'topic': topic, 'hashtag': tag, 'error': str(exc)[:180], 'score': -1})
        time.sleep(0.55)
    return sorted([x for x in items if not x.get('error')], key=lambda row: row.get('score', 0), reverse=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--topic', default='menopausa')
    parser.add_argument('--tags', default='')
    parser.add_argument('--posts-per-tag', type=int, default=8)
    parser.add_argument('--limit', type=int, default=8)
    parser.add_argument('--base', default='http://127.0.0.1:8010')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    tags = [x.strip().lstrip('#') for x in args.tags.split(',') if x.strip()] or DEFAULT_TAGS.get(args.topic, [args.topic])
    collected = collect(args.topic, tags, args.posts_per_tag)
    selected = collected[:args.limit]
    ingested = []
    for item in selected:
        payload = build_ingest_payload(item, topic=args.topic)
        if args.dry_run:
            ingested.append({'dry_run': True, 'payload': payload})
        else:
            try:
                ingested.append(post_internal(args.base, payload))
            except urllib.error.HTTPError as exc:
                ingested.append({'ok': False, 'status': exc.code, 'error': exc.read().decode('utf-8', 'replace')[:500], 'payload': payload})
            except Exception as exc:
                ingested.append({'ok': False, 'error': str(exc)[:500], 'payload': payload})
    report = {
        'ok': True,
        'topic': args.topic,
        'tags': tags,
        'collected_at': datetime.now(timezone.utc).isoformat(),
        'collected_count': len(collected),
        'selected_count': len(selected),
        'ingested_count': sum(1 for x in ingested if x.get('status') == 'ingested'),
        'top': [{'shortcode': x.get('shortcode'), 'url': x.get('url'), 'score': x.get('score'), 'hashtag': x.get('hashtag'), 'format': x.get('format')} for x in selected],
        'ingested': ingested,
    }
    path = OUT_DIR / f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-motion-video-phase4-{args.topic}.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps({'ok': True, 'saved': str(path), 'topic': args.topic, 'collected': len(collected), 'selected': len(selected), 'ingested': report['ingested_count'], 'top': report['top'][:5]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
