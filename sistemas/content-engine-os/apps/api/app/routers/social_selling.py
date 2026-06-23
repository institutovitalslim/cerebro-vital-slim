from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.db import get_conn

router = APIRouter(prefix="/social-selling", tags=["social-selling"])


def _tenant_id(conn, tenant_slug: str) -> str:
    with conn.cursor() as cur:
        cur.execute("select id from tenants where slug = %s", (tenant_slug,))
        row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=f"tenant '{tenant_slug}' not found")
    return row["id"]


class InteractorStatusUpdate(BaseModel):
    status: str = Field(pattern="^(candidate|reviewed|approved_for_manual_outreach|discarded|converted)$")


@router.get("/overview")
def social_selling_overview(tenant_slug: str = "demo") -> dict:
    """Cockpit Social Selling.

    Governança: leitura e qualificação. Não envia DM, não publica, não agenda e
    não escreve em WhatsApp/Z-API. A abordagem é manual e aprovada por humano.
    """
    with get_conn() as conn:
        tenant_id = _tenant_id(conn, tenant_slug)
        with conn.cursor() as cur:
            cur.execute(
                """
                select profile_handle, metric_date, followers_count, following_count, posts_count,
                       reach, impressions, profile_views, website_clicks, whatsapp_clicks, source, created_at
                from instagram_profile_daily_metrics
                where tenant_id=%s
                order by metric_date desc, created_at desc
                limit 1
                """,
                (tenant_id,),
            )
            latest_profile = cur.fetchone()

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
                  coalesce(avg(engagement_rate),0)::numeric(8,4) as avg_engagement_rate,
                  count(*)::int as publications_tracked
                from instagram_publication_daily_metrics
                where tenant_id=%s and metric_date >= current_date - interval '30 days'
                """,
                (tenant_id,),
            )
            aggregate = cur.fetchone()

            cur.execute(
                """
                select status, count(*)::int as total
                from social_selling_interactors
                where tenant_id=%s
                group by status
                order by total desc
                """,
                (tenant_id,),
            )
            by_status = cur.fetchall()

            cur.execute(
                """
                select consciousness_stage, count(*)::int as total, coalesce(avg(fit_score),0)::numeric(8,2) as avg_fit_score
                from social_selling_interactors
                where tenant_id=%s
                group by consciousness_stage
                order by total desc
                """,
                (tenant_id,),
            )
            by_stage = cur.fetchall()

            cur.execute(
                """
                select id::text, public_handle, public_name, interaction_type, interaction_count,
                       publication_url, last_interaction_at, consciousness_stage, fit_score, status,
                       suggested_opening, guardrails
                from social_selling_interactors
                where tenant_id=%s
                order by fit_score desc, updated_at desc
                limit 50
                """,
                (tenant_id,),
            )
            candidates = cur.fetchall()

            cur.execute(
                """
                select publication_external_id, publication_url, format, caption_excerpt, published_at,
                       views, reach, likes, comments, saves, shares, follows, whatsapp_clicks, engagement_rate
                from instagram_publication_daily_metrics
                where tenant_id=%s
                order by coalesce(engagement_rate,0) desc, metric_date desc
                limit 10
                """,
                (tenant_id,),
            )
            top_publications = cur.fetchall()

    return {
        "profile": latest_profile or {
            "profile_handle": "@dradaniely.freitas",
            "metric_date": None,
            "followers_count": 0,
            "following_count": 0,
            "posts_count": 0,
            "reach": 0,
            "impressions": 0,
            "profile_views": 0,
            "website_clicks": 0,
            "whatsapp_clicks": 0,
            "source": "rapidapi_pending",
        },
        "aggregate_30d": aggregate,
        "by_status": by_status,
        "by_stage": by_stage,
        "candidates": candidates,
        "top_publications": top_publications,
        "governance": {
            "mode": "read_only_and_manual_outreach",
            "blocked": ["auto_dm", "bulk_message", "diagnosis", "promise_result", "price_without_context"],
            "allowed": ["prioritize_candidates", "draft_manual_opening", "classify_awareness", "export_internal_review"],
            "approval_required_for": ["sending_any_message", "bulk_actions", "zapi_write", "external_publication"],
        },
        "playbook": [
            "Priorizar quem comentou, salvou, compartilhou ou clicou no perfil/WhatsApp.",
            "Classificar consciência: frio → dor → solução → quase pronto.",
            "Criar abertura manual contextual, sem parecer automação e sem promessa.",
            "Conduzir por educação e pergunta SPIN curta antes de qualquer convite.",
        ],
    }


@router.post("/interactors/{interactor_id}/status")
def update_interactor_status(interactor_id: str, payload: InteractorStatusUpdate) -> dict:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                update social_selling_interactors
                set status=%s, updated_at=now()
                where id=%s
                returning id::text, public_handle, status
                """,
                (payload.status, interactor_id),
            )
            row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="interactor not found")
    return row
