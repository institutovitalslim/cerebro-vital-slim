#!/usr/bin/env python3
"""Coleta perfil público Instagram -> external_content_items do Content OS.

Uso governado:
- read-only via wrapper `ivs-social-reach` / RapidAPI segura;
- não publica, não comenta, não envia DM e não baixa mídia;
- ingere no endpoint interno autenticado com cookie efêmero do tenant demo;
- idempotente por (tenant_id, source_network, external_id).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

OUT_DIR = Path("/root/.openclaw/reports/social-learning")
OUT_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_BASE = "http://127.0.0.1:8010"


def run_json(cmd: list[str], timeout: int = 180) -> dict[str, Any]:
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout or "comando falhou")[:1200])
    return json.loads(proc.stdout)


def demo_cookie(tenant_slug: str = "demo") -> str:
    code = f'''
from app.db import get_conn
from app.auth_core import make_token
with get_conn() as conn, conn.cursor() as cur:
    cur.execute("""
        select u.id::text as id, u.tenant_id::text as tenant_id, u.email
        from users u join tenants t on t.id=u.tenant_id
        where t.slug=%s and u.role='owner'
        order by u.created_at asc
        limit 1
    """, ({tenant_slug!r},))
    u=cur.fetchone()
if not u:
    raise SystemExit("tenant/user not found")
print("cos_session=" + make_token(u["id"], u["tenant_id"], u["email"], ttl=900))
'''
    proc = subprocess.run(
        ["docker", "exec", "content-engine-api", "python", "-c", code],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    cookie = (proc.stdout or "").strip()
    if proc.returncode != 0 or not cookie.startswith("cos_session="):
        raise RuntimeError((proc.stderr or proc.stdout or "falha ao gerar cookie efêmero")[:1200])
    return cookie


def format_of(item: dict[str, Any]) -> str:
    product = item.get("product_type")
    media_type = item.get("media_type")
    if product == "clips" or media_type == 2 or item.get("video_url_available"):
        return "reels"
    if product == "carousel_container" or media_type == 8:
        return "carrossel"
    return "post"


def url_for(shortcode: str, fmt: str) -> str:
    if fmt == "reels":
        return f"https://www.instagram.com/reel/{shortcode}/"
    return f"https://www.instagram.com/p/{shortcode}/"


def iso_ts(raw: Any) -> str | None:
    try:
        ts = int(raw)
        if ts > 0:
            return datetime.fromtimestamp(ts, timezone.utc).isoformat()
    except Exception:
        pass
    return None


def to_external_item(username: str, item: dict[str, Any]) -> dict[str, Any] | None:
    shortcode = item.get("shortcode") or item.get("code")
    if not shortcode:
        return None
    fmt = format_of(item)
    raw_payload = {k: v for k, v in item.items() if k not in {"video_url"}}
    metrics: dict[str, int | float] = {}
    for key in ("likes", "comments", "views", "plays", "reach", "shares", "saves"):
        value = item.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
            continue
        metrics[key] = value
    return {
        "source_network": "instagram",
        "source_profile": "@" + username.lstrip("@"),
        "external_id": shortcode,
        "url": url_for(shortcode, fmt),
        "format": fmt,
        "caption": (item.get("caption") or "")[:2500],
        "published_at": iso_ts(item.get("taken_at")),
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "metrics": metrics,
        "raw_payload": raw_payload,
    }


def post_ingest(
    base: str,
    tenant: str,
    source_kind: str,
    collector_run_id: str,
    items: list[dict[str, Any]],
) -> dict[str, Any]:
    payload = {
        "tenant_slug": tenant,
        "collector_run_id": collector_run_id,
        "source_kind": source_kind,
        "provider": "rapidapi_instagram_scraper_stable",
        "items": items,
    }
    req = urllib.request.Request(
        f"{base.rstrip('/')}/external-learning/ingest",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Cookie": demo_cookie(tenant),
            "User-Agent": "IVS-profile-external-collect/1.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=90) as resp:
        return json.loads(resp.read().decode("utf-8", "replace"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", default="analyzeandoptimize")
    parser.add_argument("--limit", type=int, default=30)
    parser.add_argument("--tenant", default="demo")
    parser.add_argument("--base", default=DEFAULT_BASE)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--source-kind",
        choices=["candidate"],
        default=None,
    )
    args = parser.parse_args()

    username = args.username.lstrip("@")
    collected = run_json(["ivs-social-reach", "instagram-profile", "--username", username, "--limit", str(args.limit)])
    items = [x for x in (to_external_item(username, row) for row in collected.get("items", [])) if x]
    selected = items[: args.limit]
    source_kind = args.source_kind or "candidate"
    collector_run_id = f"rapidapi-profile:{username}:{datetime.now(timezone.utc).isoformat()}"

    ingest = {"status": "dry_run", "items": len(selected), "rows": []}
    if not args.dry_run and selected:
        ingest = post_ingest(args.base, args.tenant, source_kind, collector_run_id, selected)

    report = {
        "ok": True,
        "username": username,
        "source_kind": source_kind,
        "collector_run_id": collector_run_id,
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "source_report": collected.get("saved"),
        "collected_count": len(collected.get("items", [])),
        "selected_count": len(selected),
        "ingested_count": ingest.get("items", 0),
        "dry_run": args.dry_run,
        "top": [
            {
                "external_id": item["external_id"],
                "url": item["url"],
                "format": item["format"],
                "likes": item["metrics"].get("likes"),
                "comments": item["metrics"].get("comments"),
            }
            for item in selected[:10]
        ],
        "ingest_status": ingest.get("status"),
    }
    out = OUT_DIR / f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-content-os-profile-{username}.json"
    out.write_text(json.dumps({**report, "ingest": ingest}, ensure_ascii=False, indent=2))
    print(json.dumps({**report, "saved": str(out)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
