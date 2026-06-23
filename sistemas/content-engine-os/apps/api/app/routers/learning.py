from __future__ import annotations

from collections import defaultdict
from math import log1p
from typing import Any

from fastapi import APIRouter, HTTPException

from app.db import get_conn
from app.routers.calendar import ensure_phase1_schema

router = APIRouter(prefix="/learning", tags=["learning"])


def _tenant_id(conn, tenant_slug: str) -> str:
    with conn.cursor() as cur:
        cur.execute("select id from tenants where slug = %s", (tenant_slug,))
        row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=f"tenant '{tenant_slug}' not found")
    return row["id"]


def _num(metrics: dict[str, Any], key: str) -> float:
    value = metrics.get(key)
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _content_score(metrics: dict[str, Any]) -> float:
    """Score interno: prioriza sinais de intenção, sem prometer resultado externo."""
    reach = max(_num(metrics, "reach"), 1.0)
    engagement = (
        _num(metrics, "likes")
        + 2 * _num(metrics, "comments")
        + 3 * _num(metrics, "shares")
        + 4 * _num(metrics, "saves")
        + 2 * _num(metrics, "profile_clicks")
    )
    intent = 12 * _num(metrics, "whatsapp_leads") + 25 * _num(metrics, "appointments")
    return round(((engagement + intent) / (reach / 1000.0)) + log1p(reach), 2)


def _aggregate(rows: list[dict[str, Any]], key: str, label: str) -> list[dict[str, Any]]:
    buckets: dict[str, dict[str, Any]] = defaultdict(lambda: {"dimension": label, "value": "sem_dado", "count": 0, "score_sum": 0.0, "reach": 0, "leads": 0, "appointments": 0, "examples": []})
    for row in rows:
        value = row.get(key) or "sem_dado"
        bucket = buckets[str(value)]
        bucket["value"] = str(value)
        metrics = row.get("metrics") or {}
        score = float(row.get("learning_score") or 0)
        bucket["count"] += 1
        bucket["score_sum"] += score
        bucket["reach"] += int(_num(metrics, "reach"))
        bucket["leads"] += int(_num(metrics, "whatsapp_leads"))
        bucket["appointments"] += int(_num(metrics, "appointments"))
        if len(bucket["examples"]) < 3:
            bucket["examples"].append({"title": row.get("title"), "score": score, "status": row.get("status")})
    out = []
    for bucket in buckets.values():
        count = max(bucket["count"], 1)
        bucket["avg_score"] = round(bucket.pop("score_sum") / count, 2)
        out.append(bucket)
    return sorted(out, key=lambda x: (x["avg_score"], x["count"]), reverse=True)


def _diagnosis(rows: list[dict[str, Any]], pending: int) -> str:
    if not rows and pending:
        return "Há publicações aguardando métricas. Fase 2 deve primeiro fechar medição antes de decidir vencedores."
    if not rows:
        return "Ainda não há peças medidas. Publique e registre métricas para alimentar recomendações reais."
    if len(rows) < 3:
        return "Aprendizado inicial: já existe sinal, mas a amostra ainda é pequena. Use como hipótese, não regra canônica."
    return "Aprendizado operacional ativo: usar vencedores por formato, hook e CTA para orientar o próximo sprint."


@router.get("/insights")
def learning_insights(tenant_slug: str = "demo") -> dict:
    """Fase 2: transforma publicações medidas em recomendação prática para o próximo sprint."""
    with get_conn() as conn:
        ensure_phase1_schema(conn)
        tenant_id = _tenant_id(conn, tenant_slug)
        with conn.cursor() as cur:
            cur.execute(
                """
                select e.id::text as calendar_entry_id, e.title, e.format, e.channel, e.objective,
                       e.status, e.origin_tag, e.sprint_thesis, e.sprint_hook,
                       e.metrics, e.metrics_recorded_at, e.published_at,
                       c.id::text as creative_id, c.quality_score, c.angulo_ivs, c.hook_tipo,
                       c.objecao_alvo, c.visual_tipo, c.cta_tipo, c.destino_criativo,
                       c.hypothesis
                from calendar_entries e
                left join creatives c on c.id = e.creative_id
                where e.tenant_id = %s and e.metrics_recorded_at is not null
                order by e.metrics_recorded_at desc
                limit 200
                """,
                (tenant_id,),
            )
            measured = cur.fetchall()
            cur.execute(
                """
                select count(*)::int as total
                from calendar_entries
                where tenant_id = %s
                  and metrics_recorded_at is null
                  and status in ('published','publicado','metrics_pending')
                """,
                (tenant_id,),
            )
            pending = cur.fetchone()["total"]

    rows: list[dict[str, Any]] = []
    for row in measured:
        item = dict(row)
        metrics = item.get("metrics") or {}
        item["metrics"] = metrics
        item["learning_score"] = _content_score(metrics)
        item["conversion_hint"] = {
            "whatsapp_leads": int(_num(metrics, "whatsapp_leads")),
            "appointments": int(_num(metrics, "appointments")),
            "saves": int(_num(metrics, "saves")),
            "shares": int(_num(metrics, "shares")),
        }
        rows.append(item)

    rows = sorted(rows, key=lambda x: x["learning_score"], reverse=True)
    top = rows[:8]
    by_format = _aggregate(rows, "format", "format")
    by_hook = _aggregate(rows, "sprint_hook", "hook")
    by_origin = _aggregate(rows, "origin_tag", "origin_tag")
    by_cta = _aggregate(rows, "cta_tipo", "cta")
    winner = top[0] if top else None
    next_thesis = (
        winner.get("sprint_thesis")
        if winner
        else "O corpo travado não é falta de força de vontade; é sinal de mecanismo metabólico não investigado."
    )
    next_hook = (winner.get("sprint_hook") or winner.get("hook_tipo") or "Por que fazer tudo certo pode não destravar seu corpo") if winner else "Por que fazer tudo certo pode não destravar seu corpo"
    recommendations = []
    if pending:
        recommendations.append(f"Registrar métricas de {pending} publicação(ões) antes de declarar vencedor final.")
    if by_format:
        recommendations.append(f"Priorizar formato {by_format[0]['value']} no próximo sprint; melhor média interna: {by_format[0]['avg_score']}.")
    if by_hook and by_hook[0]["value"] != "sem_dado":
        recommendations.append(f"Reaproveitar/variar o hook vencedor: {by_hook[0]['value']}.")
    if by_cta and by_cta[0]["value"] != "sem_dado":
        recommendations.append(f"Manter CTA {by_cta[0]['value']} como hipótese principal de teste.")
    if not recommendations:
        recommendations.append("Publicar pelo menos 3 peças e registrar métricas para habilitar recomendação robusta.")

    return {
        "phase": "fase_2_learning_loop",
        "mode": "read_only_recommendation",
        "governance": {
            "auto_publish": False,
            "auto_dm": False,
            "zapi_write": False,
            "external_actions": "blocked_by_default",
            "note": "Aprendizado vira hipótese operacional; publicação e envio continuam humanos.",
        },
        "summary": {
            "measured_items": len(rows),
            "metrics_pending": pending,
            "diagnosis": _diagnosis(rows, pending),
        },
        "winners": {
            "top_items": top,
            "by_format": by_format[:6],
            "by_hook": by_hook[:6],
            "by_origin": by_origin[:6],
            "by_cta": by_cta[:6],
        },
        "next_sprint_seed": {
            "thesis": next_thesis,
            "hook": next_hook,
            "objective": "autoridade_e_conversa",
            "audience_stage": "consciente_da_dor",
            "reason": "Baseado nas peças medidas no Calendário Editorial.",
        },
        "recommendations": recommendations,
    }
