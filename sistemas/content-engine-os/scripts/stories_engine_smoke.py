#!/usr/bin/env python3
"""Smoke test do Stories Engine 10x IVS.

Valida ciclo mínimo sem publicar nada:
1. temas/produtos seed disponíveis;
2. cria sequência sintética;
3. gera handoff Clara/WhatsApp;
4. registra performance;
5. consulta ranking.
"""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:8010"


def request(method: str, path: str, payload: dict | None = None) -> dict:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=data,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {path} -> {exc.code}: {body}") from exc


def main() -> int:
    themes = request("GET", "/stories/themes?tenant_slug=demo&limit=5")
    products = request("GET", "/stories/products?tenant_slug=demo&limit=5")
    if not themes.get("items"):
        raise RuntimeError("sem themes seed")
    if not products.get("items"):
        raise RuntimeError("sem products seed")

    created = request(
        "POST",
        "/stories/sequences",
        {
            "tenant_slug": "demo",
            "title": "Smoke IVS - Resistência à insulina",
            "sequence_type": "divulgacao_conteudo",
            "objective": "dm",
            "main_objection": "já tentei de tudo",
            "patient_moment": "frustracao",
            "support_asset": "texto",
            "story_count": 8,
            "payload": {
                "sequence": {
                    "palavraChave": "quero entender",
                    "ctaPrincipal": "Me manda 'quero entender' se essa parte fez sentido.",
                    "stories": [{"n": 1, "texto": "Smoke test sem publicação."}],
                }
            },
        },
    )
    seq_id = created["id"]
    handoff = request("GET", f"/stories/sequences/{seq_id}/handoff?tenant_slug=demo")
    if "utm_campaign" not in handoff.get("utm", {}):
        raise RuntimeError("handoff sem utm_campaign")
    if "SPIN" not in handoff.get("clara_script", ""):
        raise RuntimeError("handoff sem orientação SPIN")

    request(
        "POST",
        "/stories/performance",
        {
            "tenant_slug": "demo",
            "sequence_id": seq_id,
            "views": 100,
            "replies": 8,
            "useful_dms": 3,
            "leads": 1,
            "prints": 2,
            "sticker_taps": 11,
            "shares": 4,
            "saves": 5,
            "retention_initial_pct": 72,
            "intent_signal": "quero entender",
            "quality_metric": "dm_util",
            "dominant_objection": "já tentei de tudo",
            "decision": "adaptar",
            "notes": "Smoke test sintético, sem publicação real.",
        },
    )
    winners = request("GET", "/stories/winners?tenant_slug=demo&limit=3")
    if not winners.get("items"):
        raise RuntimeError("ranking vazio após performance")

    print(json.dumps({"ok": True, "sequence_id": seq_id, "handoff_tag": handoff["origin_tag"], "themes": len(themes["items"]), "products": len(products["items"])}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
