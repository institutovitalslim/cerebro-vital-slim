#!/usr/bin/env python3
"""
fetch_top_reels.py — pega os top N reels de um perfil do Instagram via instagram120 + Stable API.

Uso:
    python3 fetch_top_reels.py <username> [--top 11] [--max-pages 12]

Output:
    - JSON em /tmp/reels/<username>_top.json com top N reels (sorted por plays)
    - Caption COMPLETA via Stable API quando truncada na listagem
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

def load_rapidapi_key():
    key = os.environ.get("RAPIDAPI_KEY")
    if key:
        return key
    env_path = Path("/root/.openclaw/secure/rapidapi.env")
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.startswith("RAPIDAPI_KEY="):
                return line.split("=", 1)[1].strip().strip("\"").strip("'")
    return ""

KEY = load_rapidapi_key()
LEGACY_HOST = "instagram120.p.rapidapi.com"
STABLE_HOST = "instagram-scraper-stable-api.p.rapidapi.com"

OUT_DIR = Path("/tmp/reels")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def http_post(url, payload, headers, timeout=30):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def http_get(url, headers, timeout=20):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def list_profile_posts(username, max_pages=12):
    """Pagina por todos os posts do perfil via instagram120."""
    cursor = ""
    all_edges = []
    headers = {
        "Content-Type": "application/json",
        "x-rapidapi-host": LEGACY_HOST,
        "x-rapidapi-key": KEY,
    }
    for page in range(1, max_pages + 1):
        try:
            data = http_post(
                f"https://{LEGACY_HOST}/api/instagram/posts",
                {"username": username, "maxId": cursor},
                headers,
                timeout=30,
            )
        except Exception as e:
            print(f"[warn] page {page} failed: {e}", file=sys.stderr)
            break
        edges = data.get("result", {}).get("edges", [])
        if not edges:
            break
        all_edges.extend(edges)
        pi = data.get("result", {}).get("page_info", {})
        if not pi.get("has_next_page"):
            break
        cursor = pi.get("end_cursor", "")
        if not cursor:
            break
        print(f"[info] page {page}: +{len(edges)} (total {len(all_edges)})", file=sys.stderr)
        time.sleep(1)
    return all_edges


def extract_video_summary(node):
    """Extrai metadata de um post de vídeo/reel."""
    if not (node.get("media_type") == 2 or node.get("product_type") == "clips"):
        return None
    cap = node.get("caption") or {}
    if isinstance(cap, dict):
        text = cap.get("text", "") or ""
    elif isinstance(cap, str):
        text = cap
    else:
        text = ""
    return {
        "code": node.get("code"),
        "id": node.get("id"),
        "pk": node.get("pk"),
        "product_type": node.get("product_type"),
        "media_type": node.get("media_type"),
        "like_count": node.get("like_count") or node.get("fb_like_count") or 0,
        "comment_count": node.get("comment_count") or 0,
        "view_count": node.get("view_count") or 0,
        "play_count": node.get("play_count") or 0,
        "duration": node.get("video_duration") or 0,
        "taken_at": node.get("taken_at"),
        "caption": text,
        "url": f"https://instagram.com/reel/{node.get('code')}/",
    }


def fetch_full_caption_via_stable(code):
    """Tenta pegar caption mais completa via Stable API (que retorna text não-truncado)."""
    headers = {
        "x-rapidapi-host": STABLE_HOST,
        "x-rapidapi-key": KEY,
    }
    for typ in ("reel", "post"):
        try:
            url = f"https://{STABLE_HOST}/get_media_data.php?reel_post_code_or_url={code}&type={typ}"
            data = http_get(url, headers, timeout=15)
            if not data.get("shortcode"):
                continue
            cap_edges = data.get("edge_media_to_caption", {}).get("edges", [])
            if cap_edges:
                return cap_edges[0].get("node", {}).get("text", "") or ""
        except Exception as e:
            print(f"[warn] stable fetch {code}/{typ} failed: {e}", file=sys.stderr)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("username", help="Instagram username sem @")
    ap.add_argument("--top", type=int, default=11)
    ap.add_argument("--max-pages", type=int, default=12)
    ap.add_argument("--enrich", action="store_true", help="Buscar caption completa via Stable API quando curta")
    args = ap.parse_args()

    print(f"[info] paginating posts for @{args.username} (max {args.max_pages} pages)...", file=sys.stderr)
    edges = list_profile_posts(args.username, max_pages=args.max_pages)
    print(f"[info] total posts fetched: {len(edges)}", file=sys.stderr)

    videos = []
    for e in edges:
        node = e.get("node") or {}
        v = extract_video_summary(node)
        if v:
            videos.append(v)
    print(f"[info] videos/reels found: {len(videos)}", file=sys.stderr)

    # Sort: prefer play_count, fallback to view_count, then engagement
    def sort_key(v):
        plays = v["play_count"] or v["view_count"] or 0
        eng = v["like_count"] * 5 + v["comment_count"] * 20
        return (plays, eng)

    videos.sort(key=sort_key, reverse=True)
    top = videos[:args.top]

    # Enrich captions if requested
    if args.enrich:
        for v in top:
            if len(v["caption"]) < 200:
                full = fetch_full_caption_via_stable(v["code"])
                if full and len(full) > len(v["caption"]):
                    v["caption_short"] = v["caption"]
                    v["caption"] = full
                time.sleep(0.6)

    out = {
        "username": args.username,
        "fetched_at": int(time.time()),
        "total_posts": len(edges),
        "total_videos": len(videos),
        "top": top,
    }
    out_path = OUT_DIR / f"{args.username}_top.json"
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[ok] saved {out_path}")
    print(f"[ok] top {len(top)} reels ready for analysis")
    # Quick summary to stdout
    for i, v in enumerate(top, 1):
        cap_one = (v["caption"] or "").replace("\n", " ")[:80]
        print(f"{i:2d}. {v['code']} likes={v['like_count']} cmts={v['comment_count']} plays={v['play_count']} dur={v['duration']:.0f}s | {cap_one}")


if __name__ == "__main__":
    main()
