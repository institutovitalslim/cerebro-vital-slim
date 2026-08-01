#!/usr/bin/env python3
"""Smoke autenticado de copy/estado da UI do Content Radar.

Falha se códigos internos vazarem na interface ou se uma fonte excluída
for apresentada visualmente como ativa.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import urllib.request

BASE_URL = os.environ.get("CONTENT_RADAR_WEB_BASE", "http://127.0.0.1:3010")


def owner_cookie() -> str:
    code = '''from app.db import get_conn
from app.auth_core import make_token
with get_conn() as c, c.cursor() as x:
 x.execute("select u.id::text,u.tenant_id::text,u.email from users u join tenants t on t.id=u.tenant_id where t.slug='demo' and u.role='owner' order by u.created_at limit 1")
 u=x.fetchone()
print('cos_session='+make_token(u['id'],u['tenant_id'],u['email'],ttl=300))'''
    proc = subprocess.run(
        ["docker", "exec", "content-engine-api", "python", "-c", code],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    cookie = (proc.stdout or "").strip()
    if proc.returncode != 0 or not cookie.startswith("cos_session="):
        raise RuntimeError("não foi possível gerar cookie efêmero")
    return cookie


def main() -> int:
    request = urllib.request.Request(
        f"{BASE_URL}/radar-externo",
        headers={"Cookie": owner_cookie(), "User-Agent": "IVS-radar-copy-smoke/1.0"},
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        html = response.read().decode("utf-8", "replace")

    leaked_codes = sorted(
        token for token in ("insufficient_sample", "insufficient_metric", "missing_metric")
        if token in html
    )
    excluded_labels = re.findall(
        r'<article class="radarSourceCard source-excluded[^"]*">.*?'
        r'<span class="radarActivity[^"]*">([^<]+)</span>',
        html,
        flags=re.DOTALL,
    )
    invalid_excluded = [label for label in excluded_labels if label.strip() != "Excluída"]

    result = {
        "http_status": response.status,
        "leaked_codes": leaked_codes,
        "excluded_cards": len(excluded_labels),
        "invalid_excluded_labels": invalid_excluded,
        "ok": not leaked_codes and bool(excluded_labels) and not invalid_excluded,
    }
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
