"""instagram_ingest.py — Ingestão diária do Instagram da Dra no Content Engine OS.

Usa o scraper RapidAPI (instagram120 — perfil + lista de posts) e grava (idempotente por dia)
em instagram_profile_daily_metrics + instagram_publication_daily_metrics, que o BI e o
Social Selling leem. Métricas privadas (reach/impressions/saves/shares) NÃO vêm de scraper
público — ficam nulas (só o Meta Insights da própria conta as tem).

Rodar dentro do container da API:  docker exec content-engine-api python scripts/instagram_ingest.py
Config por env: IG_HANDLE (default dradaniely.freitas), RAPIDAPI_KEY, IG_TENANT_SLUG (default demo), IG_PAGES (default 3).
"""
from __future__ import annotations

import json
import os
import sys

import httpx

sys.path.insert(0, "/app")
from app.db import get_conn  # noqa: E402

HANDLE = os.environ.get("IG_HANDLE", "dradaniely.freitas")
TENANT_SLUG = os.environ.get("IG_TENANT_SLUG", "demo")
PAGES = int(os.environ.get("IG_PAGES", "20"))
KEY = os.environ.get("RAPIDAPI_KEY", "cf7bd568f0msh846185e42b5253bp1d7915jsne0d2cb9e3b56")
HOST = "instagram120.p.rapidapi.com"
BASE = f"https://{HOST}/api/instagram"
HEADERS = {"Content-Type": "application/json", "x-rapidapi-host": HOST, "x-rapidapi-key": KEY}
SOURCE = "rapidapi:instagram120"


def _fmt(node: dict) -> str:
    if node.get("product_type") == "clips" or node.get("media_type") == 2:
        return "reels"
    if node.get("media_type") == 8 or node.get("carousel_media_count"):
        return "carrossel"
    return "imagem"


_HEAVY = {"video_dash_manifest", "image_versions2", "clips_metadata", "carousel_media",
          "video_versions", "thumbnails", "media_cropping_info", "sharing_friction_info"}


def _slim(node: dict) -> dict:
    """Remove campos pesados (manifest de vídeo, versões de imagem) p/ raw_payload enxuto e válido."""
    return {k: v for k, v in node.items() if k not in _HEAVY}


def _caption(node: dict) -> str:
    cap = node.get("caption")
    txt = cap.get("text", "") if isinstance(cap, dict) else (cap or "")
    return (txt or node.get("accessibility_caption") or "")[:280]


def fetch_profile(cli: httpx.Client) -> dict:
    r = cli.post(f"{BASE}/profile", headers=HEADERS, json={"username": HANDLE}, timeout=30)
    r.raise_for_status()
    return r.json().get("result", {})


def fetch_posts(cli: httpx.Client, pages: int) -> list[dict]:
    nodes, cursor = [], ""
    for _ in range(pages):
        r = cli.post(f"{BASE}/posts", headers=HEADERS, json={"username": HANDLE, "maxId": cursor}, timeout=40)
        r.raise_for_status()
        res = r.json().get("result", {})
        edges = res.get("edges") or []
        nodes += [e.get("node", {}) for e in edges if e.get("node")]
        cursor = (res.get("page_info") or {}).get("end_cursor") or ""
        if not cursor:
            break
    return nodes


def main() -> None:
    with httpx.Client() as cli:
        prof = fetch_profile(cli)
        nodes = fetch_posts(cli, PAGES)

    followers = (prof.get("edge_followed_by") or {}).get("count")
    following = (prof.get("edge_follow") or {}).get("count")
    posts_count = (prof.get("edge_owner_to_timeline_media") or {}).get("count")
    handle = "@" + HANDLE

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("select id from tenants where slug=%s", (TENANT_SLUG,))
        row = cur.fetchone()
        if not row:
            raise SystemExit(f"tenant '{TENANT_SLUG}' não encontrado")
        tid = row["id"]

        # PERFIL (idempotente: apaga o snapshot de hoje e reinsere)
        cur.execute("delete from instagram_profile_daily_metrics "
                    "where tenant_id=%s and profile_handle=%s and metric_date=current_date", (tid, handle))
        cur.execute(
            "insert into instagram_profile_daily_metrics "
            "(tenant_id, metric_date, profile_handle, followers_count, following_count, posts_count, source, raw_payload) "
            "values (%s, current_date, %s, %s, %s, %s, %s, %s::jsonb)",
            (tid, handle, followers, following, posts_count, SOURCE, json.dumps(prof)))

        # PUBLICAÇÕES (idempotente por dia)
        cur.execute("delete from instagram_publication_daily_metrics "
                    "where tenant_id=%s and profile_handle=%s and metric_date=current_date", (tid, handle))
        n = 0
        for nd in nodes:
            code = nd.get("code") or nd.get("shortcode")
            if not code:
                continue
            ext = str(nd.get("pk") or nd.get("id") or code)
            url = f"https://www.instagram.com/p/{code}/"
            ts = nd.get("taken_at") or nd.get("taken_at_timestamp")
            cur.execute(
                "insert into instagram_publication_daily_metrics "
                "(tenant_id, metric_date, profile_handle, publication_external_id, publication_url, "
                " published_at, likes, comments, views, format, caption_excerpt, source, raw_payload) "
                "values (%s, current_date, %s, %s, %s, to_timestamp(%s), %s, %s, %s, %s, %s, %s, %s::jsonb)",
                (tid, handle, ext, url, ts, nd.get("like_count"), nd.get("comment_count"),
                 nd.get("view_count") or nd.get("play_count"), _fmt(nd), _caption(nd), SOURCE,
                 json.dumps(_slim(nd))))
            n += 1

    print(f"OK ingest @{HANDLE}: followers={followers} posts_count={posts_count} publicacoes_gravadas={n}")


if __name__ == "__main__":
    main()
