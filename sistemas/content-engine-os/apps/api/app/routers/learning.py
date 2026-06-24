from __future__ import annotations

from collections import defaultdict
import json
from math import log1p
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.db import get_conn
from app.routers.calendar import ensure_phase1_schema

router = APIRouter(prefix="/learning", tags=["learning"])


class MetricsImportItem(BaseModel):
    calendar_entry_id: str | None = None
    creative_id: str | None = None
    platform_post_id: str | None = None
    published_url: str | None = None
    metrics: dict[str, Any] = Field(default_factory=dict)


class MetricsImportRequest(BaseModel):
    tenant_slug: str = Field(default="demo")
    source: str = Field(default="manual_import")
    items: list[MetricsImportItem]


def _tenant_id(conn, tenant_slug: str) -> str:
    with conn.cursor() as cur:
        cur.execute("select id from tenants where slug = %s", (tenant_slug,))
        row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=f"tenant '{tenant_slug}' not found")
    return row["id"]


def _num(metrics: dict[str, Any], key: str) -> float:
    aliases = {
        "comments": ["comments", "comentarios"],
        "shares": ["shares", "envios", "compartilhamentos"],
        "leads": ["leads", "whatsapp_leads"],
        "whatsapp_leads": ["whatsapp_leads", "leads"],
        "whatsapp_clicks": ["whatsapp_clicks", "profile_clicks"],
        "views": ["views", "visualizacoes", "plays"],
        "retention_rate": ["retention_rate", "retencao_3s_pct", "conclusao_pct"],
    }
    keys = aliases.get(key, [key])
    for k in keys:
        value = metrics.get(k)
        try:
            if value is not None and value != "":
                return float(value or 0)
        except (TypeError, ValueError):
            continue
    return 0.0


def _content_score(metrics: dict[str, Any]) -> float:
    """Score interno: prioriza sinais de intenção e retenção, sem prometer resultado externo."""
    reach = max(_num(metrics, "reach"), 1.0)
    views = _num(metrics, "views")
    retention = _num(metrics, "retention_rate")
    engagement = (
        _num(metrics, "likes")
        + 2 * _num(metrics, "comments")
        + 3 * _num(metrics, "shares")
        + 4 * _num(metrics, "saves")
        + 1.5 * _num(metrics, "replies")
        + 2 * _num(metrics, "profile_clicks")
        + 3 * _num(metrics, "whatsapp_clicks")
    )
    intent = 12 * _num(metrics, "whatsapp_leads") + 25 * _num(metrics, "appointments")
    retention_bonus = min(retention, 100.0) * 0.8 + log1p(max(views, 0.0))
    return round(((engagement + intent + retention_bonus) / (reach / 1000.0)) + log1p(reach), 2)


def _aggregate(rows: list[dict[str, Any]], key: str, label: str) -> list[dict[str, Any]]:
    buckets: dict[str, dict[str, Any]] = defaultdict(lambda: {"dimension": label, "value": "sem_dado", "count": 0, "score_sum": 0.0, "reach": 0, "views": 0, "saves": 0, "shares": 0, "leads": 0, "appointments": 0, "examples": []})
    for row in rows:
        value = row.get(key) or "sem_dado"
        bucket = buckets[str(value)]
        bucket["value"] = str(value)
        metrics = row.get("metrics") or {}
        score = float(row.get("learning_score") or 0)
        bucket["count"] += 1
        bucket["score_sum"] += score
        bucket["reach"] += int(_num(metrics, "reach"))
        bucket["views"] += int(_num(metrics, "views"))
        bucket["saves"] += int(_num(metrics, "saves"))
        bucket["shares"] += int(_num(metrics, "shares"))
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
        return "Há publicações aguardando métricas. Feche a medição antes de declarar vencedores."
    if not rows:
        return "Ainda não há peças medidas. Publique e registre métricas para alimentar recomendações reais."
    if len(rows) < 3:
        return "Aprendizado inicial: já existe sinal, mas a amostra ainda é pequena. Use como hipótese, não regra canônica."
    return "Aprendizado operacional ativo: usar vencedores por formato, hook, objeção, visual e CTA para orientar o próximo sprint."


def _winner_value(bucket: list[dict[str, Any]]) -> str | None:
    if not bucket:
        return None
    value = bucket[0].get("value")
    return None if not value or value == "sem_dado" else str(value)


def _build_payload(rows: list[dict[str, Any]], pending: int, publication_count: int) -> dict:
    rows = sorted(rows, key=lambda x: x["learning_score"], reverse=True)
    top = rows[:8]
    by_format = _aggregate(rows, "format", "format")
    by_hook = _aggregate(rows, "sprint_hook", "hook")
    by_origin = _aggregate(rows, "origin_tag", "origin_tag")
    by_cta = _aggregate(rows, "cta_tipo", "cta")
    by_objection = _aggregate(rows, "objecao_alvo", "objection")
    by_visual = _aggregate(rows, "visual_tipo", "visual")
    by_pillar = _aggregate(rows, "pillar", "pillar")
    winner = top[0] if top else None
    next_thesis = (
        winner.get("sprint_thesis")
        if winner
        else "O corpo travado não é falta de força de vontade; é sinal de mecanismo metabólico não investigado."
    )
    next_hook = (winner.get("sprint_hook") or winner.get("hook_tipo") or "Por que fazer tudo certo pode não destravar seu corpo") if winner else "Por que fazer tudo certo pode não destravar seu corpo"
    champion_variables = {
        "format": _winner_value(by_format),
        "hook": _winner_value(by_hook),
        "objection": _winner_value(by_objection),
        "cta": _winner_value(by_cta),
        "visual": _winner_value(by_visual),
        "pillar": _winner_value(by_pillar),
        "origin_tag": _winner_value(by_origin),
    }
    recommendations = []
    if pending:
        recommendations.append(f"Registrar métricas de {pending} publicação(ões) antes de declarar vencedor final.")
    if publication_count and pending:
        recommendations.append("Separar publicação registrada de publicação medida: o sistema já rastreia o gargalo entre postar e aprender.")
    if by_format:
        recommendations.append(f"Priorizar formato {by_format[0]['value']} no próximo sprint; melhor média interna: {by_format[0]['avg_score']}.")
    if champion_variables["hook"]:
        recommendations.append(f"Reaproveitar/variar o hook vencedor: {champion_variables['hook']}.")
    if champion_variables["objection"]:
        recommendations.append(f"Atacar novamente a objeção vencedora: {champion_variables['objection']}.")
    if champion_variables["visual"]:
        recommendations.append(f"Manter o padrão visual vencedor como hipótese de escala: {champion_variables['visual']}.")
    if champion_variables["cta"]:
        recommendations.append(f"Manter CTA {champion_variables['cta']} como hipótese principal de teste.")
    if not recommendations:
        recommendations.append("Publicar pelo menos 3 peças e registrar métricas para habilitar recomendação robusta.")

    return {
        "phase": "fase_3_performance_learning",
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
            "registered_publications": publication_count,
            "metrics_pending": pending,
            "champions_ready": len([r for r in rows if r.get("learning_score", 0) >= 70]),
            "diagnosis": _diagnosis(rows, pending),
        },
        "winners": {
            "top_items": top,
            "by_format": by_format[:6],
            "by_hook": by_hook[:6],
            "by_origin": by_origin[:6],
            "by_cta": by_cta[:6],
            "by_objection": by_objection[:6],
            "by_visual": by_visual[:6],
            "by_pillar": by_pillar[:6],
        },
        "next_sprint_seed": {
            "thesis": next_thesis,
            "hook": next_hook,
            "objective": "autoridade_e_conversa",
            "audience_stage": "consciente_da_dor",
            "champion_variables": champion_variables,
            "reason": "Baseado nas peças medidas no Calendário Editorial e nas variáveis vencedoras.",
        },
        "recommendations": recommendations,
    }


def _load_rows(tenant_slug: str) -> tuple[list[dict[str, Any]], int, int]:
    with get_conn() as conn:
        ensure_phase1_schema(conn)
        tenant_id = _tenant_id(conn, tenant_slug)
        with conn.cursor() as cur:
            cur.execute(
                """
                select e.id::text as calendar_entry_id, e.title, e.format, e.channel, e.objective,
                       e.status, e.origin_tag, e.sprint_thesis, e.sprint_hook,
                       split_part(coalesce(e.origin_tag,''), ':', 2) as pillar,
                       coalesce(nullif(e.metrics, '{}'::jsonb), nullif(p.metrics, '{}'::jsonb), '{}'::jsonb) as metrics,
                       coalesce(e.metrics_recorded_at, p.created_at) as metrics_recorded_at,
                       coalesce(e.published_at, p.published_at) as published_at,
                       p.id::text as publication_id, p.platform, p.platform_post_id, p.published_url, p.campaign_name,
                       c.id::text as creative_id, c.quality_score, c.angulo_ivs, c.hook_tipo,
                       c.objecao_alvo, c.visual_tipo, c.cta_tipo, c.destino_criativo,
                       c.hypothesis
                from calendar_entries e
                left join creatives c on c.id = e.creative_id
                left join publications p on p.creative_id = e.creative_id
                where e.tenant_id = %s and (e.metrics_recorded_at is not null or (p.metrics is not null and p.metrics <> '{}'::jsonb))
                order by coalesce(e.metrics_recorded_at, p.created_at) desc
                limit 300
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
            cur.execute("select count(*)::int as total from publications where tenant_id=%s", (tenant_id,))
            publication_count = cur.fetchone()["total"]

    rows: list[dict[str, Any]] = []
    for row in measured:
        item = dict(row)
        metrics = item.get("metrics") or {}
        item["metrics"] = metrics
        item["learning_score"] = _content_score(metrics)
        item["conversion_hint"] = {
            "views": int(_num(metrics, "views")),
            "reach": int(_num(metrics, "reach")),
            "whatsapp_clicks": int(_num(metrics, "whatsapp_clicks")),
            "whatsapp_leads": int(_num(metrics, "whatsapp_leads")),
            "appointments": int(_num(metrics, "appointments")),
            "saves": int(_num(metrics, "saves")),
            "shares": int(_num(metrics, "shares")),
        }
        rows.append(item)
    return rows, pending, publication_count


@router.get("/insights")
def learning_insights(tenant_slug: str = "demo") -> dict:
    """Fase 3: transforma publicações e métricas em variáveis vencedoras para o próximo sprint."""
    rows, pending, publication_count = _load_rows(tenant_slug)
    return _build_payload(rows, pending, publication_count)


@router.get("/performance-dashboard")
def performance_dashboard(tenant_slug: str = "demo") -> dict:
    """Dashboard por variável: hook, objeção, CTA, visual, pilar e formato."""
    rows, pending, publication_count = _load_rows(tenant_slug)
    payload = _build_payload(rows, pending, publication_count)
    return {
        "phase": payload["phase"],
        "summary": payload["summary"],
        "variable_dashboard": payload["winners"],
        "next_sprint_seed": payload["next_sprint_seed"],
        "governance": payload["governance"],
    }


@router.post("/metrics-import")
def import_metrics(payload: MetricsImportRequest) -> dict:
    """Importação governada/manual de métricas já obtidas fora do sistema. Não acessa Meta/Instagram."""
    if not payload.items:
        raise HTTPException(400, "lista de métricas vazia")
    updated: list[dict[str, Any]] = []
    with get_conn() as conn:
        ensure_phase1_schema(conn)
        tenant_id = _tenant_id(conn, payload.tenant_slug)
        with conn.cursor() as cur:
            for item in payload.items:
                metrics = dict(item.metrics or {})
                metrics["source"] = payload.source
                if item.calendar_entry_id:
                    cur.execute(
                        """
                        update calendar_entries
                        set metrics=%s::jsonb, metrics_recorded_at=now(), status='medido'
                        where id=%s and tenant_id=%s
                        returning id::text as calendar_entry_id, creative_id::text as creative_id, format
                        """,
                        (json.dumps(metrics, ensure_ascii=False), item.calendar_entry_id, tenant_id),
                    )
                elif item.creative_id:
                    cur.execute(
                        """
                        update calendar_entries
                        set metrics=%s::jsonb, metrics_recorded_at=now(), status='medido'
                        where creative_id=%s and tenant_id=%s
                        returning id::text as calendar_entry_id, creative_id::text as creative_id, format
                        """,
                        (json.dumps(metrics, ensure_ascii=False), item.creative_id, tenant_id),
                    )
                else:
                    raise HTTPException(400, "cada item precisa de calendar_entry_id ou creative_id")
                row = cur.fetchone()
                if not row:
                    raise HTTPException(404, "entrada para importar métricas não encontrada")
                cur.execute(
                    """
                    insert into publications (tenant_id, creative_id, format, published_at, metrics, platform, platform_post_id, published_url)
                    values (%s,%s,%s,now(),%s::jsonb,'instagram',%s,%s)
                    on conflict (creative_id) where creative_id is not null do update set
                        metrics=excluded.metrics,
                        platform_post_id=coalesce(excluded.platform_post_id, publications.platform_post_id),
                        published_url=coalesce(excluded.published_url, publications.published_url)
                    returning id::text as publication_id
                    """,
                    (tenant_id, row.get("creative_id"), row.get("format"), json.dumps(metrics, ensure_ascii=False), item.platform_post_id, item.published_url),
                )
                pub = cur.fetchone()
                updated.append({**dict(row), "publication_id": pub.get("publication_id") if pub else None})
    return {"status": "imported", "source": payload.source, "updated": updated, "governance": {"external_fetch": False, "manual_metrics_only": True}}
