#!/usr/bin/env python3
"""Smoke read-only e focado do Content Radar v1 no runtime oficial.

Não ingere, não altera fonte e não persiste dados. O cookie efêmero é mantido
somente em memória e nunca é impresso.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class Check:
    name: str
    ok: bool
    detail: str


def owner_cookie() -> str | None:
    code = r'''
from app.db import get_conn
from app.auth_core import make_token
with get_conn() as conn, conn.cursor() as cur:
    cur.execute("""
        select u.id::text as id, u.tenant_id::text as tenant_id, u.email
        from users u join tenants t on t.id=u.tenant_id
        where t.slug=%s and u.role='owner'
        order by u.created_at asc
        limit 1
    """, ("demo",))
    user = cur.fetchone()
if user:
    print("cos_session=" + make_token(user["id"], user["tenant_id"], user["email"], ttl=600))
'''
    proc = subprocess.run(
        ["docker", "exec", "content-engine-api", "python", "-c", code],
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )
    value = (proc.stdout or "").strip()
    return value if proc.returncode == 0 and value.startswith("cos_session=") else None


def other_tenant_slug() -> str | None:
    code = r'''from app.db import get_conn
with get_conn() as conn, conn.cursor() as cur:
    cur.execute("select slug from tenants where slug<>%s order by created_at asc limit 1", ("demo",))
    row = cur.fetchone()
if row:
    print(row["slug"])
'''
    proc = subprocess.run(
        ["docker", "exec", "content-engine-api", "python", "-c", code],
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )
    value = (proc.stdout or "").strip()
    return value if proc.returncode == 0 and value else None


def request(base: str, path: str, *, cookie: str | None = None, method: str = "GET") -> tuple[int, bytes, str]:
    headers = {"User-Agent": "IVS-Content-Radar-Smoke/1.0"}
    if cookie:
        headers["Cookie"] = cookie
    req = urllib.request.Request(f"{base.rstrip('/')}{path}", headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=25) as response:
            return response.status, response.read(), response.headers.get("content-type", "")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read(), exc.headers.get("content-type", "")
    except Exception as exc:
        return 0, str(exc).encode(), ""


def decode_json(body: bytes) -> Any:
    try:
        return json.loads(body.decode("utf-8", errors="replace"))
    except Exception:
        return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="https://conteudo.institutovitalslim.com.br")
    parser.add_argument("--expect", choices=("legacy", "off", "on"), required=True)
    args = parser.parse_args()

    checks: list[Check] = []
    cookie = owner_cookie()
    checks.append(Check("owner_cookie", bool(cookie), "cookie efêmero de owner carregado" if cookie else "owner ausente"))
    if not cookie:
        print(json.dumps({"ok": False, "checks": [asdict(item) for item in checks]}, ensure_ascii=False, indent=2))
        return 1

    status, body, _ = request(args.base, "/api/external-learning/overview?tenant_slug=demo")
    checks.append(Check("unauthenticated_overview", status == 401, f"http={status}"))

    status, body, content_type = request(
        args.base,
        "/api/external-learning/overview?tenant_slug=demo",
        cookie=cookie,
    )
    payload = decode_json(body)
    checks.append(Check("authenticated_overview", status == 200 and isinstance(payload, dict), f"http={status} type={content_type}"))

    if isinstance(payload, dict):
        if args.expect == "legacy":
            contract_ok = payload.get("phase") == "fase_4_external_reverse_engineering" and "patterns" in payload
        else:
            expected_flag = args.expect == "on"
            summary = payload.get("summary") or {}
            contract_ok = (
                payload.get("feature_enabled") is expected_flag
                and payload.get("mode") == "observed_metrics_only"
                and bool(payload.get("version"))
                and all(key in summary for key in ("total_items", "candidate_items", "governed_items", "eligible_items", "last_ingest_at"))
                and isinstance(payload.get("top_items"), list)
                and isinstance(payload.get("sources"), list)
            )
        checks.append(Check("overview_contract", contract_ok, f"expect={args.expect}"))

    foreign_slug = other_tenant_slug()
    if foreign_slug:
        status, _, _ = request(
            args.base,
            f"/api/external-learning/overview?tenant_slug={foreign_slug}",
            cookie=cookie,
        )
        checks.append(Check("cross_tenant_hidden", status == 404, f"http={status}; foreign tenant exists"))
    else:
        checks.append(Check("cross_tenant_hidden", True, "não há segundo tenant para exercitar o isolamento"))

    status, html, content_type = request(args.base, "/radar-externo", cookie=cookie)
    checks.append(Check("radar_page", status == 200 and "text/html" in content_type, f"http={status} type={content_type}"))

    css_paths = sorted(set(re.findall(rb'href=["\']([^"\']+\.css[^"\']*)["\']', html)))
    css_text = b""
    for raw_path in css_paths:
        css_path = raw_path.decode("utf-8", errors="ignore")
        if css_path.startswith("http"):
            continue
        css_status, css_body, _ = request(args.base, css_path, cookie=cookie)
        if css_status == 200:
            css_text += css_body
    css_ok = args.expect == "legacy" or b".radarToolbar" in css_text
    checks.append(Check("radar_css", css_ok, f"assets={len(css_paths)} selector_present={b'.radarToolbar' in css_text}"))

    ok = all(item.ok for item in checks)
    print(json.dumps({"ok": ok, "expect": args.expect, "checks": [asdict(item) for item in checks]}, ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
