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
import urllib.parse

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


def request_text(path: str) -> str:
    with urllib.request.urlopen(f"{BASE}{path}", timeout=20) as resp:
        return resp.read().decode("utf-8", errors="replace")


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def request_redirect_location(path: str) -> str:
    opener = urllib.request.build_opener(NoRedirect)
    try:
        opener.open(f"{BASE}{path}", timeout=20)
    except urllib.error.HTTPError as exc:
        if exc.code in {301, 302, 303, 307, 308}:
            return exc.headers.get("Location", "")
        raise
    raise RuntimeError("tracking endpoint não redirecionou")


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
                    "stories": [
                        {"n": 1, "funcao": "Hook", "texto": "Smoke test sem publicação.", "visual": "card IVS", "sticker": "enquete", "dm": "quero entender", "risco": "baixo"},
                        {"n": 2, "funcao": "CTA", "texto": "Me manda quero entender para testar o fluxo.", "visual": "texto", "sticker": "DM", "dm": "quero entender", "risco": "baixo"},
                    ],
                }
            },
        },
    )
    seq_id = created["id"]
    items = request("GET", f"/stories/sequences/{seq_id}/items?tenant_slug=demo")
    if len(items.get("items", [])) < 2:
        raise RuntimeError("story_items não foram persistidos")

    handoff = request("GET", f"/stories/sequences/{seq_id}/handoff?tenant_slug=demo")
    if "utm_campaign" not in handoff.get("utm", {}):
        raise RuntimeError("handoff sem utm_campaign")
    if "SPIN" not in handoff.get("clara_script", ""):
        raise RuntimeError("handoff sem orientação SPIN")
    if not handoff.get("tracking_url"):
        raise RuntimeError("handoff sem tracking_url")

    export_txt = request_text(f"/stories/sequences/{seq_id}/export?tenant_slug=demo&format=telegram")
    if "### Handoff Clara" not in export_txt or "Smoke IVS" not in export_txt:
        raise RuntimeError("export Telegram incompleto")
    export_html = request_text(f"/stories/sequences/{seq_id}/export?tenant_slug=demo&format=html")
    if "<table" not in export_html or "Script Clara" not in export_html:
        raise RuntimeError("export HTML incompleto")

    location = request_redirect_location(f"/stories/track/{seq_id}?tenant_slug=demo")
    if "api.whatsapp.com" not in location:
        raise RuntimeError("tracking não redirecionou para WhatsApp")
    clicks = request("GET", f"/stories/sequences/{seq_id}/clicks?tenant_slug=demo")
    if clicks.get("summary", {}).get("total_clicks", 0) < 1:
        raise RuntimeError("clique não foi registrado")

    request(
        "POST",
        "/stories/block-metrics",
        {
            "tenant_slug": "demo",
            "sequence_id": seq_id,
            "block_name": "hook_cta",
            "story_start": 1,
            "story_end": 2,
            "views_start": 100,
            "views_end": 71,
            "notes": "Smoke sintético: retenção por bloco.",
        },
    )
    request(
        "POST",
        "/stories/conversions",
        {
            "tenant_slug": "demo",
            "sequence_id": seq_id,
            "origin_tag": handoff["origin_tag"],
            "conversion_type": "appointment",
            "source": "smoke",
            "notes": "Smoke sintético sem PII.",
        },
    )
    analytics = request("GET", f"/stories/sequences/{seq_id}/analytics?tenant_slug=demo")
    if analytics.get("conversions", {}).get("appointments", 0) < 1:
        raise RuntimeError("analytics não computou agendamento")
    contract = request("GET", f"/stories/origin-tags/{urllib.parse.quote(handoff['origin_tag'], safe='')}/clara-contract?tenant_slug=demo")
    if "clara_instruction" not in contract or "SPIN" not in contract["clara_instruction"]:
        raise RuntimeError("contrato Clara incompleto")
    weekly = request_text("/stories/weekly-report?tenant_slug=demo&limit=5")
    if "Relatório semanal" not in weekly or "Agendamentos" not in weekly:
        raise RuntimeError("relatório semanal incompleto")

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

    print(json.dumps({"ok": True, "sequence_id": seq_id, "story_items": len(items["items"]), "tracking_clicks": clicks["summary"]["total_clicks"], "appointments": analytics["conversions"]["appointments"], "handoff_tag": handoff["origin_tag"], "themes": len(themes["items"]), "products": len(products["items"])}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
