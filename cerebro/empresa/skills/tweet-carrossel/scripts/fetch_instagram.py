#!/usr/bin/env python3
"""
fetch_instagram.py — Extrai caption + metadata de post do Instagram via RapidAPI.

Tenta 2 APIs em cascata:
1. instagram-scraper-stable-api (mais rapido, pega direto por URL)
2. instagram120 (pagina por perfil - fallback quando quota da primeira esgota)

Uso:
    python3 fetch_instagram.py --url "https://www.instagram.com/p/<CODE>/" --out /tmp/post.txt
"""
import argparse, os, sys, json, urllib.request, urllib.parse, re
from pathlib import Path

RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY", "cf7bd568f0msh846185e42b5253bp1d7915jsne0d2cb9e3b56")


def extract_shortcode(url: str) -> str:
    m = re.search(r"/(?:p|reel)/([A-Za-z0-9_-]+)", url)
    return m.group(1) if m else ""


def fetch_stable_api(url: str) -> dict:
    """API 1: instagram-scraper-stable-api (endpoint direto por URL)."""
    encoded = urllib.parse.quote(url, safe="")
    api_url = f"https://instagram-scraper-stable-api.p.rapidapi.com/get_media_data.php?reel_post_code_or_url={encoded}&type=post"
    req = urllib.request.Request(api_url, headers={
        "x-rapidapi-host": "instagram-scraper-stable-api.p.rapidapi.com",
        "x-rapidapi-key": RAPIDAPI_KEY,
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except Exception as e:
        return {"error": str(e)}


def fetch_via_profile(username: str, shortcode: str, max_pages: int = 3) -> dict:
    """API 2: instagram120 - busca em posts do perfil ate achar o shortcode."""
    max_id = ""
    for _page in range(max_pages):
        body = json.dumps({"username": username, "maxId": max_id}).encode()
        req = urllib.request.Request(
            "https://instagram120.p.rapidapi.com/api/instagram/posts",
            data=body,
            headers={
                "Content-Type": "application/json",
                "x-rapidapi-host": "instagram120.p.rapidapi.com",
                "x-rapidapi-key": RAPIDAPI_KEY,
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.loads(r.read())
        except Exception as e:
            return {"error": f"profile fetch falhou: {e}"}

        # Procura o shortcode nos posts
        result = data.get("result", {})
        edges = result.get("data", {}).get("user", {}).get("edge_owner_to_timeline_media", {}).get("edges", [])
        for edge in edges:
            node = edge.get("node", {})
            if node.get("shortcode") == shortcode:
                # Achou
                caption_edges = node.get("edge_media_to_caption", {}).get("edges", [])
                caption = caption_edges[0]["node"]["text"] if caption_edges else ""
                return {
                    "owner": node.get("owner", {}).get("username") or username,
                    "caption": caption,
                    "shortcode": shortcode,
                    "taken_at": node.get("taken_at_timestamp"),
                    "source": "instagram120/profile-search",
                }

        # Pagina
        page_info = result.get("data", {}).get("user", {}).get("edge_owner_to_timeline_media", {}).get("page_info", {})
        if not page_info.get("has_next_page"):
            break
        max_id = page_info.get("end_cursor", "")

    return {"error": f"shortcode {shortcode} nao encontrado nas ultimas paginas de @{username}"}


def parse_stable(data: dict) -> dict:
    """Extrai caption + owner do payload da stable-api."""
    if "message" in data:
        return {"error": data["message"]}
    owner = data.get("owner", {}).get("username") or data.get("user", {}).get("username")
    caption_edges = data.get("edge_media_to_caption", {}).get("edges", [])
    caption = caption_edges[0]["node"]["text"] if caption_edges else data.get("caption", "")
    return {
        "owner": owner,
        "caption": caption,
        "shortcode": data.get("shortcode"),
        "source": "stable-api",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--username", default="institutovitalslim",
                    help="Perfil para fallback (default: institutovitalslim)")
    ap.add_argument("--out", help="Salva caption em arquivo")
    ap.add_argument("--format", choices=["text", "json"], default="text")
    args = ap.parse_args()

    shortcode = extract_shortcode(args.url)
    if not shortcode:
        print("ERRO: shortcode nao extraido da URL", file=sys.stderr)
        sys.exit(1)

    # Tentativa 1: stable-api
    print(f"[1/2] stable-api para shortcode {shortcode}...", file=sys.stderr)
    data = fetch_stable_api(args.url)
    result = parse_stable(data)
    if result.get("error"):
        print(f"  falhou: {result['error']}", file=sys.stderr)
        # Tentativa 2: via perfil
        print(f"[2/2] fallback via @{args.username}/posts...", file=sys.stderr)
        result = fetch_via_profile(args.username, shortcode)

    if result.get("error"):
        print(f"\nFALHOU EM AMBAS APIS: {result['error']}", file=sys.stderr)
        sys.exit(2)

    if args.format == "json":
        out = json.dumps(result, ensure_ascii=False, indent=2)
    else:
        out = (
            f"URL: {args.url}\n"
            f"Shortcode: {result.get('shortcode')}\n"
            f"Owner: @{result.get('owner')}\n"
            f"Source: {result.get('source')}\n"
            f"\n--- CAPTION ---\n\n{result.get('caption')}\n"
        )

    if args.out:
        Path(args.out).write_text(out, encoding="utf-8")
        print(f"OK: {args.out}", file=sys.stderr)
    print(out)


if __name__ == "__main__":
    main()
