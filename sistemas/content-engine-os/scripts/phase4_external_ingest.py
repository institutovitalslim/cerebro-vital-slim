#!/usr/bin/env python3
"""Fase 4 Content Engine OS — ingestão externa governada.

Padrão seguro:
- read-only sobre conteúdo público já obtido/permitido;
- não publica, não envia DM, não escreve em Z-API;
- envia itens ao endpoint interno /api/external-learning/ingest;
- modo --sample é idempotente para smoke/cron inicial.

Para RapidAPI real, configure um coletor que produza JSON no formato:
{
  "items": [{"source_profile":"@perfil", "external_id":"...", "url":"...", "format":"reels", "caption":"...", "metrics": {...}}]
}
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_BASE = os.environ.get("CONTENT_ENGINE_BASE", "http://127.0.0.1:8010")


def post_json(url: str, payload: dict[str, Any], *, session_cookie: str) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "User-Agent": "IVS-Phase4-Ingest/1.0",
            "Cookie": session_cookie,
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        body = resp.read().decode("utf-8", errors="replace")
        return json.loads(body)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default=DEFAULT_BASE)
    parser.add_argument("--tenant", default="demo")
    parser.add_argument("--json-file", help="Arquivo JSON com items externos já coletados via fonte governada")
    parser.add_argument("--provider", default="manual_governed_json")
    parser.add_argument(
        "--source-kind",
        choices=["candidate", "thematic_search"],
        default="candidate",
    )
    parser.add_argument("--collector-run-id")
    parser.add_argument(
        "--session-cookie-file",
        default=os.environ.get("CONTENT_ENGINE_SESSION_COOKIE_FILE"),
        help="Arquivo local contendo cos_session=<token>; não passe o token na linha de comando",
    )
    args = parser.parse_args()

    if not args.json_file:
        print("ERRO: use --json-file; amostras sintéticas não entram no radar operacional", file=sys.stderr)
        return 2

    if not args.session_cookie_file:
        print("ERRO: use --session-cookie-file para autenticar a ingestão interna", file=sys.stderr)
        return 2
    cookie_path = Path(args.session_cookie_file)
    session_cookie = cookie_path.read_text(encoding="utf-8").strip()
    if not session_cookie.startswith("cos_session="):
        print("ERRO: arquivo de sessão inválido", file=sys.stderr)
        return 2

    path = Path(args.json_file)
    data = json.loads(path.read_text())
    items = data.get("items") if isinstance(data, dict) else data
    if not isinstance(items, list) or not items:
        print("ERRO: JSON sem lista items", file=sys.stderr)
        return 2

    collector_run_id = args.collector_run_id or f"manual:{datetime.now(timezone.utc).isoformat()}"
    out = post_json(
        f"{args.base}/external-learning/ingest",
        {
            "tenant_slug": args.tenant,
            "collector_run_id": collector_run_id,
            "source_kind": args.source_kind,
            "provider": args.provider,
            "items": items,
        },
        session_cookie=session_cookie,
    )
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
