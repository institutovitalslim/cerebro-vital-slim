#!/usr/bin/env python3
"""Content Engine OS — geração diária governada de criativos IVS.

Objetivo operacional: produzir 30–50 criativos/dia em matriz de hipóteses
(ângulo × hook × objeção × visual × CTA), sem depender da UI e com relatório
JSON auditável.

Segurança:
- padrão é DRY-RUN; só grava no banco quando usar --execute;
- não publica nada em rede social;
- não expõe PII;
- limita execução a 50 peças por rodada.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_BASE_URL = "https://conteudo.institutovitalslim.com.br/api"
MAX_COUNT = 50

THEMES = [
    "fadiga persistente e peso travado na mulher 40+",
    "tireoide lenta, queda de cabelo e dificuldade de emagrecer",
    "resistência à insulina e gordura abdominal depois dos 40",
    "menopausa, sono ruim e compulsão por doce à noite",
    "efeito sanfona e medo de começar só mais uma dieta",
    "cansaço mental, cortisol e barriga inchada",
    "bioimpedância mostrando perda de músculo apesar da dieta",
    "mulher que já tentou de tudo e precisa investigar a causa",
]
ANGULOS = ["culpa", "so_dieta", "metodo", "baseline", "preco"]
HOOKS = ["identificacao", "mecanismo", "contraste", "mito", "pergunta_direta"]
OBJECOES = ["ja_tentei_de_tudo", "so_mais_uma_dieta", "preco_valor", "sem_tempo", "hormonios_metabolismo"]
VISUAIS = ["dra_camera", "broll_rotina", "prova_metodo", "texto_premium"]
CTAS_FEED = ["salvar_compartilhar", "pre_avaliacao"]
CTAS_ADS = ["pre_avaliacao", "whatsapp_qualificado", "agendamento"]


@dataclass
class PlannedCreative:
    variant_index: int
    formato: str
    objetivo: str
    destino: str
    tema: str
    angulo: str | None
    hook_tipo: str
    objecao_alvo: str
    visual_tipo: str
    cta_tipo: str
    persona: str
    quality_metric: str
    expected_intent_signal: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gera lote diário de criativos IVS")
    parser.add_argument("--count", type=int, default=30, help="Quantidade de criativos (1–50)")
    parser.add_argument("--execute", action="store_true", help="Grava de verdade chamando /generation/orchestrate")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--tenant-slug", default="demo")
    parser.add_argument("--theme", action="append", dest="themes", help="Tema adicional/obrigatório; pode repetir")
    parser.add_argument("--format-mix", default="carrossel:0.55,reels:0.30,stories:0.10,estatico:0.05")
    parser.add_argument("--sleep", type=float, default=1.0, help="Pausa entre chamadas live")
    parser.add_argument("--out", default="/root/deliverables/content-engine-daily-batch-latest.json")
    parser.add_argument("--seed", type=int, default=None)
    return parser.parse_args()


def weighted_formats(spec: str) -> list[str]:
    pool: list[str] = []
    for part in spec.split(","):
        if not part.strip():
            continue
        name, weight_s = part.split(":", 1)
        weight = max(0.0, float(weight_s))
        pool.extend([name.strip()] * max(1, int(round(weight * 100))))
    return pool or ["carrossel"]


def build_plan(count: int, extra_themes: list[str] | None, format_mix: str, seed: int | None) -> list[PlannedCreative]:
    if count < 1 or count > MAX_COUNT:
        raise SystemExit(f"count precisa estar entre 1 e {MAX_COUNT}")
    rng = random.Random(seed)
    themes = (extra_themes or []) + THEMES
    formats = weighted_formats(format_mix)
    combos: list[tuple[str, str, str, str, str]] = []
    for angulo in ANGULOS:
        for hook in HOOKS:
            for obj in OBJECOES:
                for visual in VISUAIS:
                    # CTA varia por destino/formato na montagem final
                    combos.append((angulo, hook, obj, visual, rng.choice(CTAS_ADS)))
    rng.shuffle(combos)

    plan: list[PlannedCreative] = []
    for idx in range(1, count + 1):
        formato = rng.choice(formats)
        destino = "meta_ads" if formato == "carrossel" and idx % 3 == 0 else "feed"
        angulo, hook, obj, visual, _ = combos[(idx - 1) % len(combos)]
        cta_pool = CTAS_ADS if destino == "meta_ads" else CTAS_FEED
        cta = rng.choice(cta_pool)
        objetivo = "conversão" if destino == "meta_ads" else rng.choice(["identificação", "educação", "desejo", "atração"])
        quality_metric = "lead_util" if destino == "meta_ads" else rng.choice(["envio", "salvamento", "retencao", "dm_util"])
        expected = "WhatsApp qualificado/agendamento" if destino == "meta_ads" else "salvamento/envio/direct qualificado"
        plan.append(PlannedCreative(
            variant_index=idx,
            formato=formato,
            objetivo=objetivo,
            destino=destino,
            tema=themes[(idx - 1) % len(themes)],
            angulo=angulo if destino == "meta_ads" else None,
            hook_tipo=hook,
            objecao_alvo=obj,
            visual_tipo=visual,
            cta_tipo=cta,
            persona="mulher 38-55, rotina intensa, já tentou dietas e quer entender a causa do corpo travado",
            quality_metric=quality_metric,
            expected_intent_signal=expected,
        ))
    return plan


def post_json(url: str, payload: dict[str, Any], timeout: int = 180) -> tuple[int, dict[str, Any] | str]:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "IVS-Content-Daily-Batch/1.0"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            try:
                return resp.status, json.loads(body)
            except Exception:
                return resp.status, body[:1000]
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")[:1000]
    except Exception as exc:
        return 0, f"{type(exc).__name__}: {exc}"


def payload_for(item: PlannedCreative, tenant_slug: str) -> dict[str, Any]:
    payload = asdict(item)
    payload.pop("variant_index", None)
    payload["tenant_slug"] = tenant_slug
    payload["rede"] = "instagram"
    payload["funil"] = "relacionamento_conversao"
    payload["trial_reel"] = item.formato == "reels"
    payload["seo_social_intent"] = item.tema
    payload["send_save_reason"] = "explica um mecanismo que a paciente quer lembrar ou enviar para uma amiga"
    if item.formato != "carrossel":
        payload.pop("angulo", None)
        payload["destino"] = "feed"
    return payload


def main() -> int:
    args = parse_args()
    plan = build_plan(args.count, args.themes, args.format_mix, args.seed)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    report: dict[str, Any] = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "mode": "execute" if args.execute else "dry_run",
        "base_url": args.base_url,
        "tenant_slug": args.tenant_slug,
        "requested": args.count,
        "plan": [asdict(p) for p in plan],
        "results": [],
        "summary": {"created": 0, "failed": 0},
    }

    if not args.execute:
        out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"ok": True, "mode": "dry_run", "planned": len(plan), "out": str(out_path)}, ensure_ascii=False))
        return 0

    endpoint = args.base_url.rstrip("/") + "/generation/orchestrate"
    for item in plan:
        payload = payload_for(item, args.tenant_slug)
        status, data = post_json(endpoint, payload)
        ok = status == 200 and isinstance(data, dict) and bool(data.get("id"))
        row = {
            "variant_index": item.variant_index,
            "ok": ok,
            "http_status": status,
            "creative_id": data.get("id") if isinstance(data, dict) else None,
            "quality_score": data.get("quality_score") if isinstance(data, dict) else None,
            "format": item.formato,
            "tema": item.tema,
            "error": None if ok else data,
        }
        report["results"].append(row)
        report["summary"]["created" if ok else "failed"] += 1
        out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(row, ensure_ascii=False), flush=True)
        if args.sleep:
            time.sleep(args.sleep)

    ok_all = report["summary"]["failed"] == 0
    print(json.dumps({"ok": ok_all, "summary": report["summary"], "out": str(out_path)}, ensure_ascii=False))
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
