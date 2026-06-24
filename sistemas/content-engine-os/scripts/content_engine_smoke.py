#!/usr/bin/env python3
"""Smoke test read-only do Content Engine OS.

Valida o que costuma quebrar a operação:
- API pública via /api
- web pública
- endpoints centrais do Motor A
- render público de um criativo renderizado
- worker de render ativo no systemd

Não cria conteúdo, não publica e não toca em dados sensíveis.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.request
from dataclasses import dataclass, asdict
from typing import Any

BASE = "https://conteudo.institutovitalslim.com.br"


@dataclass
class Check:
    name: str
    ok: bool
    detail: str


def http_json(path: str, timeout: int = 20) -> tuple[int, Any, str]:
    url = f"{BASE}{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "IVS-Content-Smoke/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            try:
                data = json.loads(body)
            except Exception:
                data = body[:300]
            return resp.status, data, resp.headers.get("content-type", "")
    except Exception as exc:
        return 0, None, str(exc)


def http_head(path: str, timeout: int = 20) -> tuple[int, str, int]:
    url = f"{BASE}{path}"
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "IVS-Content-Smoke/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.headers.get("content-type", ""), int(resp.headers.get("content-length") or 0)
    except Exception as exc:
        return 0, str(exc), 0


def cmd(args: list[str]) -> tuple[int, str]:
    p = subprocess.run(args, capture_output=True, text=True, timeout=20)
    return p.returncode, (p.stdout + p.stderr).strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    checks: list[Check] = []

    status, data, ctype = http_json("/api/health")
    checks.append(Check("api_health", status == 200 and isinstance(data, dict) and data.get("status") == "ok", f"status={status} content_type={ctype}"))

    status, ctype, _ = http_head("/")
    checks.append(Check("web_cockpit", status == 200 and "text/html" in ctype, f"status={status} content_type={ctype}"))

    status, ctype, _ = http_head("/criar")
    checks.append(Check("web_criar", status == 200 and "text/html" in ctype, f"status={status} content_type={ctype}"))

    status, ctype, _ = http_head("/business-intelligence")
    checks.append(Check("web_business_intelligence", status == 200 and "text/html" in ctype, f"status={status} content_type={ctype}"))

    for page in ["/sprint-semanal", "/aprendizado", "/producao/carrosseis", "/producao/estaticos", "/producao/reels", "/social-selling"]:
        status, ctype, _ = http_head(page)
        checks.append(Check(f"web_{page.strip('/').replace('/', '_')}", status == 200 and "text/html" in ctype, f"status={status} content_type={ctype}"))

    for name, path in [
        ("dashboard_summary", "/api/dashboard/summary?tenant_slug=demo"),
        ("bi_overview", "/api/bi/overview?tenant_slug=demo"),
        ("social_selling_overview", "/api/social-selling/overview?tenant_slug=demo"),
        ("weekly_command_overview", "/api/weekly-command/overview?tenant_slug=demo"),
        ("learning_insights", "/api/learning/insights?tenant_slug=demo"),
        ("learning_performance_dashboard", "/api/learning/performance-dashboard?tenant_slug=demo"),
        ("creatives_list", "/api/generation/creatives?tenant_slug=demo&limit=2"),
        ("roteiros_library", "/api/generation/roteiros?tenant_slug=demo"),
        ("calendar_entries", "/api/calendar/entries?tenant_slug=demo"),
        ("stories_themes", "/api/stories/themes?tenant_slug=demo&limit=50"),
        ("stories_sequences", "/api/stories/sequences?tenant_slug=demo"),
    ]:
        status, data, ctype = http_json(path)
        checks.append(Check(name, status == 200 and isinstance(data, dict), f"status={status} content_type={ctype}"))
        if name == "calendar_entries" and status == 200 and isinstance(data, dict):
            sample = (data.get("items") or [{}])[0]
            checks.append(Check(
                "calendar_phase1_fields",
                all(k in sample for k in ("creative_id", "metrics_pending", "metrics_recorded_at")) or not data.get("items"),
                "creative_id/metrics_pending/metrics_recorded_at presentes ou calendário vazio",
            ))
        if name == "bi_overview" and status == 200 and isinstance(data, dict):
            flow = data.get("editorial_flow") or {}
            checks.append(Check(
                "bi_editorial_flow",
                all(k in flow for k in ("approved_to_publish", "metrics_pending", "measured")),
                f"editorial_flow={flow}",
            ))
        if name == "learning_insights" and status == 200 and isinstance(data, dict):
            summary = data.get("summary") or {}
            seed = data.get("next_sprint_seed") or {}
            winners = data.get("winners") or {}
            checks.append(Check(
                "learning_phase3_contract",
                data.get("phase") == "fase_3_performance_learning"
                and all(k in summary for k in ("measured_items", "metrics_pending", "registered_publications"))
                and bool(seed.get("thesis"))
                and all(k in winners for k in ("by_format", "by_hook", "by_objection", "by_visual", "by_pillar", "by_cta")),
                f"phase={data.get('phase')} summary={summary} next_thesis={seed.get('thesis')}",
            ))
        if name == "learning_performance_dashboard" and status == 200 and isinstance(data, dict):
            board = data.get("variable_dashboard") or {}
            checks.append(Check(
                "learning_variable_dashboard",
                all(k in board for k in ("by_format", "by_hook", "by_objection", "by_visual", "by_pillar", "by_cta")),
                f"dashboard_keys={sorted(board.keys())}",
            ))

    status, data, _ = http_json("/api/generation/creatives?tenant_slug=demo&limit=1")
    asset_url = None
    if status == 200 and isinstance(data, dict) and data.get("items"):
        asset_url = data["items"][0].get("asset_url") or (data["items"][0].get("assets") or [None])[0]
    if asset_url:
        r_status, r_ctype, r_size = http_head(asset_url)
        checks.append(Check("public_render", r_status == 200 and "image" in r_ctype and r_size > 1000, f"status={r_status} content_type={r_ctype} bytes={r_size} path={asset_url}"))
    else:
        checks.append(Check("public_render", False, "sem asset_url no último criativo"))

    rc, out = cmd(["systemctl", "is-active", "content-render.service"])
    checks.append(Check("render_worker_service", rc == 0 and out.strip() == "active", out[:200]))

    ok = all(c.ok for c in checks)
    payload = {"ok": ok, "checks": [asdict(c) for c in checks]}
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for c in checks:
            print(("OK" if c.ok else "FAIL"), c.name, c.detail)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
