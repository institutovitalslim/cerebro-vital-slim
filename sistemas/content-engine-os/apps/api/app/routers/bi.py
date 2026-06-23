from fastapi import APIRouter, HTTPException

from app.db import get_conn
from app.routers.calendar import ensure_phase1_schema

router = APIRouter(prefix="/bi", tags=["business-intelligence"])


def _tenant_id(conn, tenant_slug: str) -> str:
    with conn.cursor() as cur:
        cur.execute("select id from tenants where slug = %s", (tenant_slug,))
        row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=f"tenant '{tenant_slug}' not found")
    return row["id"]


@router.get("/overview")
def bi_overview(tenant_slug: str = "demo") -> dict:
    """BI agregado do Content Engine OS.

    Read-only, sem PII. A rota prepara a seção de Business Intelligence para
    receber ingestão diária via RapidAPI do perfil @dradaniely.freitas.
    """
    with get_conn() as conn:
        ensure_phase1_schema(conn)
        tenant_id = _tenant_id(conn, tenant_slug)
        with conn.cursor() as cur:
            cur.execute(
                """
                select
                  count(*)::int as total_creatives,
                  coalesce(sum(case when status='aprovado' then 1 else 0 end),0)::int as approved,
                  coalesce(sum(case when status='renderizado' then 1 else 0 end),0)::int as ready_review,
                  coalesce(sum(case when status='ajustes_solicitados' then 1 else 0 end),0)::int as changes_requested,
                  coalesce(avg(quality_score),0)::numeric(8,2) as avg_quality_score
                from creatives
                where tenant_id = %s
                """,
                (tenant_id,),
            )
            creatives = cur.fetchone()

            cur.execute(
                """
                select format, count(*)::int as total,
                       coalesce(sum(case when status='aprovado' then 1 else 0 end),0)::int as approved
                from creatives
                where tenant_id = %s
                group by format
                order by total desc
                """,
                (tenant_id,),
            )
            by_format = cur.fetchall()

            cur.execute(
                """
                select
                  count(*)::int as stories_sequences,
                  coalesce(sum(case when status='approved' then 1 else 0 end),0)::int as stories_approved,
                  coalesce(sum(case when status='changes_requested' then 1 else 0 end),0)::int as stories_changes_requested
                from story_sequences
                where tenant_id = %s
                """,
                (tenant_id,),
            )
            stories = cur.fetchone()

            cur.execute(
                """
                select
                  coalesce(count(distinct c.id),0)::int as story_clicks,
                  coalesce(sum(case when v.conversion_type='qualified_dm' then 1 else 0 end),0)::int as qualified_dms,
                  coalesce(sum(case when v.conversion_type='lead' then 1 else 0 end),0)::int as leads,
                  coalesce(sum(case when v.conversion_type='appointment' then 1 else 0 end),0)::int as appointments
                from story_sequences s
                left join story_click_events c on c.sequence_id=s.id
                left join story_conversions v on v.sequence_id=s.id
                where s.tenant_id=%s
                """,
                (tenant_id,),
            )
            funnel = cur.fetchone()

            cur.execute(
                """
                select title, sequence_type, objective, status, created_at
                from story_sequences
                where tenant_id = %s
                order by created_at desc
                limit 5
                """,
                (tenant_id,),
            )
            recent_stories = cur.fetchall()

            cur.execute(
                """
                select id::text as id, title, format, channel, objective, status, scheduled_for, created_at,
                       creative_id::text as creative_id, origin_tag, sprint_thesis, sprint_hook,
                       metrics_recorded_at,
                       case when metrics_recorded_at is null and status in ('published','publicado','metrics_pending') then true else false end as metrics_pending
                from calendar_entries
                where tenant_id = %s
                order by coalesce(scheduled_for, created_at) asc
                limit 8
                """,
                (tenant_id,),
            )
            calendar = cur.fetchall()

            cur.execute(
                """
                select
                  coalesce(sum(case when status in ('approved','aprovado_para_publicar') then 1 else 0 end),0)::int as approved_to_publish,
                  coalesce(sum(case when status in ('published','publicado','metrics_pending') and metrics_recorded_at is null then 1 else 0 end),0)::int as metrics_pending,
                  coalesce(sum(case when status='medido' or metrics_recorded_at is not null then 1 else 0 end),0)::int as measured
                from calendar_entries
                where tenant_id = %s
                """,
                (tenant_id,),
            )
            editorial_flow = cur.fetchone()

            cur.execute(
                """
                select network, count(*)::int as total
                from sources
                where tenant_id = %s and active=true
                group by network
                order by total desc
                """,
                (tenant_id,),
            )
            sources = cur.fetchall()

            cur.execute(
                """
                select profile_handle, metric_date, followers_count, following_count, posts_count,
                       reach, impressions, profile_views, website_clicks, whatsapp_clicks
                from instagram_profile_daily_metrics
                where tenant_id=%s
                order by metric_date desc, created_at desc
                limit 1
                """,
                (tenant_id,),
            )
            social_profile = cur.fetchone()

            cur.execute(
                """
                select
                  coalesce(sum(likes),0)::int as likes,
                  coalesce(sum(comments),0)::int as comments,
                  coalesce(sum(saves),0)::int as saves,
                  coalesce(sum(shares),0)::int as shares,
                  coalesce(sum(profile_visits),0)::int as profile_visits,
                  coalesce(sum(follows),0)::int as follows,
                  coalesce(sum(whatsapp_clicks),0)::int as whatsapp_clicks,
                  count(*)::int as publications_tracked
                from instagram_publication_daily_metrics
                where tenant_id=%s and metric_date >= current_date - interval '30 days'
                """,
                (tenant_id,),
            )
            social_aggregate = cur.fetchone()

            cur.execute(
                """
                select
                  count(*)::int as total_interactors,
                  coalesce(sum(case when status='candidate' then 1 else 0 end),0)::int as candidates,
                  coalesce(sum(case when status='approved_for_manual_outreach' then 1 else 0 end),0)::int as approved_for_manual_outreach,
                  coalesce(avg(fit_score),0)::numeric(8,2) as avg_fit_score
                from social_selling_interactors
                where tenant_id=%s
                """,
                (tenant_id,),
            )
            social_selling = cur.fetchone()

    readiness = {
        "profile": "@dradaniely.freitas",
        "collector": "João",
        "source": "RapidAPI",
        "mode": "read_only_planned",
        "status": "spec_ready_pending_ingestion",
        "pii_policy": "métricas agregadas; sem coletar seguidores, nomes, telefone ou comentários identificáveis",
        "next_step": "criar ingestão diária idempotente RapidAPI → instagram_post_metrics",
    }
    content_score = round(
        (creatives["approved"] * 4)
        + (creatives["ready_review"] * 2)
        + (stories["stories_approved"] * 5)
        + (funnel["appointments"] * 20)
        + (funnel["leads"] * 8)
        + (funnel["qualified_dms"] * 3),
        2,
    )
    return {
        "workspace": {"tenant_slug": tenant_slug},
        "creatives": creatives,
        "by_format": by_format,
        "stories": stories,
        "funnel": funnel,
        "recent_stories": recent_stories,
        "calendar": calendar,
        "editorial_flow": editorial_flow,
        "sources": sources,
        "rapidapi_instagram": readiness,
        "social_profile": social_profile or {"profile_handle": "@dradaniely.freitas", "followers_count": 0, "profile_views": 0, "whatsapp_clicks": 0},
        "social_aggregate_30d": social_aggregate,
        "social_selling": social_selling,
        "content_score": content_score,
        "diagnosis": _diagnosis(creatives, stories, funnel),
    }


def _diagnosis(creatives: dict, stories: dict, funnel: dict) -> dict:
    if creatives["total_creatives"] == 0:
        priority = "Gerar a primeira família de criativos a partir de uma tese central."
    elif creatives["ready_review"] > creatives["approved"]:
        priority = "Revisar e aprovar a fila pronta antes de gerar mais volume."
    elif stories["stories_sequences"] == 0:
        priority = "Criar sequências de stories conectadas a WhatsApp/Clara."
    elif funnel["appointments"] == 0 and funnel["leads"] == 0:
        priority = "Medir cliques/DMs/leads e ajustar CTAs para conversa qualificada."
    else:
        priority = "Escalar as teses vencedoras em matriz de formatos e calendário."
    return {
        "status_label": "Cockpit operacional ativo",
        "priority": priority,
        "next_actions": [
            "Escolher uma tese central da semana e gerar família: reel, carrossel, stories e anúncio.",
            "Aprovar ou solicitar alterações em tudo que está pronto antes de publicar.",
            "Registrar performance e realimentar o BI para decidir a próxima rodada.",
        ],
    }
