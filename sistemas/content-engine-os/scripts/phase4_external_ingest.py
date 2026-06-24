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
from pathlib import Path
from typing import Any

DEFAULT_BASE = os.environ.get("CONTENT_ENGINE_BASE", "http://127.0.0.1:8010")


def post_json(url: str, payload: dict[str, Any]) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "IVS-Phase4-Ingest/1.0"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        body = resp.read().decode("utf-8", errors="replace")
        return json.loads(body)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default=DEFAULT_BASE)
    parser.add_argument("--tenant", default="demo")
    parser.add_argument("--sample", action="store_true", help="Roda ingestão idempotente de amostra interna governada")
    parser.add_argument("--json-file", help="Arquivo JSON com items externos já coletados via fonte governada")
    parser.add_argument("--source", default="phase4_script")
    args = parser.parse_args()

    if args.sample:
        out = post_json(f"{args.base}/external-learning/ingest-sample?tenant_slug={args.tenant}", {})
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0

    if not args.json_file:
        print("ERRO: use --sample ou --json-file", file=sys.stderr)
        return 2

    path = Path(args.json_file)
    data = json.loads(path.read_text())
    items = data.get("items") if isinstance(data, dict) else data
    if not isinstance(items, list) or not items:
        print("ERRO: JSON sem lista items", file=sys.stderr)
        return 2

    out = post_json(f"{args.base}/external-learning/ingest", {"tenant_slug": args.tenant, "source": args.source, "items": items})
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
