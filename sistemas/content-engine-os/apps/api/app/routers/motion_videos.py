from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.db import get_conn
from app.services.motion_video_planner import (
    CONTENT_FORMATS,
    build_content_format_examples,
    build_motion_video_plan,
    example_winners_for_format,
    motion_video_matrix_8x8,
    motion_video_options,
    normalize_real_content_format_example,
)

router = APIRouter(prefix="/motion-videos", tags=["motion-videos"])


class RealExampleIngestRequest(BaseModel):
    tenant_slug: str = Field(default="demo")
    content_format: str
    source_type: str = Field(default="manual_url")
    source_handle_or_url: str | None = None
    external_id: str | None = None
    content_url: str | None = None
    thumbnail_url: str | None = None
    transcript_summary: str | None = None
    hook_summary: str | None = None
    why_this_example_works: str | None = None
    retention_mechanism: str | None = None
    compliance_risk: str | None = None
    ivs_applicability_score: int = Field(default=70, ge=0, le=100)
    winner_candidate_type: str | None = None
    metrics: dict[str, Any] = Field(default_factory=dict)
    raw_payload_summary: str | None = None
    caption_summary: str | None = None


class MotionVideoPlanRequest(BaseModel):
    tenant_slug: str = Field(default="demo")
    source_type: str = Field(default="manual")
    source_id: str | None = None
    topic: str
    thesis: str | None = None
    objective: str = Field(default="educacao_autoridade")
    audience: str | None = None
    objection: str = Field(default="ja_tentei_de_tudo")
    content_format: str = Field(default="mini_aula_visual")
    source_example_ids: list[str] = Field(default_factory=list)
    source_examples_summary: str | None = None
    content_strategy: str = Field(default="loop_previsao")
    screen_format: str = Field(default="reels")
    duration_seconds: int = Field(default=60, ge=10, le=180)
    visual_preset: str = Field(default="ivs_mixed_media_medico_premium")
    narrative_pattern: str | None = None
    voiceover: str = Field(default="documental_feminina_pt_br")
    cta: str | None = None


def _tenant_id(conn, tenant_slug: str) -> str:
    with conn.cursor() as cur:
        cur.execute("select id from tenants where slug = %s", (tenant_slug,))
        row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=f"tenant '{tenant_slug}' not found")
    return row["id"]


def _format_ids(conn, tenant_id: str) -> dict[str, str]:
    with conn.cursor() as cur:
        cur.execute("select key, id from content_formats where tenant_id=%s", (tenant_id,))
        return {row["key"]: row["id"] for row in cur.fetchall()}


def _upsert_format_example(cur, tenant_id: str, format_id: str | None, item: dict[str, Any]) -> None:
    cur.execute(
        """
        insert into content_format_examples (
          tenant_id, content_format_id, content_format_key, source_type,
          source_handle_or_url, external_id, content_url, thumbnail_url,
          transcript_summary, hook_summary, retention_mechanism, why_this_example_works,
          compliance_risk, ivs_applicability_score, metadata
        ) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
        on conflict (tenant_id, external_id) do update set
          content_format_id = excluded.content_format_id,
          content_format_key = excluded.content_format_key,
          source_type = excluded.source_type,
          source_handle_or_url = excluded.source_handle_or_url,
          content_url = excluded.content_url,
          thumbnail_url = excluded.thumbnail_url,
          transcript_summary = excluded.transcript_summary,
          hook_summary = excluded.hook_summary,
          retention_mechanism = excluded.retention_mechanism,
          why_this_example_works = excluded.why_this_example_works,
          compliance_risk = excluded.compliance_risk,
          ivs_applicability_score = excluded.ivs_applicability_score,
          metadata = excluded.metadata
        """,
        (
            tenant_id,
            format_id,
            item["content_format"],
            item["source_type"],
            item["source_handle_or_url"],
            item["external_id"],
            item["content_url"],
            item["thumbnail_url"],
            item["transcript_summary"],
            item["hook_summary"],
            item.get("retention_mechanism"),
            item["why_this_example_works"],
            item["compliance_risk"],
            item["ivs_applicability_score"],
            json.dumps({
                "winner_candidate_type": item.get("winner_candidate_type"),
                "copy_guardrail": item.get("copy_guardrail"),
                "selected_for_generation": item.get("selected_for_generation", False),
                "raw_metrics": item.get("raw_metrics") or {},
                "raw_payload_summary": item.get("raw_payload_summary"),
            }, ensure_ascii=False),
        ),
    )


def _safe_fetch_sources(conn, tenant_id: str) -> dict[str, list[dict[str, Any]]]:
    data: dict[str, list[dict[str, Any]]] = {"themes": [], "viral_scripts": []}
    with conn.cursor() as cur:
        try:
            cur.execute(
                """
                select id, theme as title, objective, notes, created_at
                from manual_themes
                where tenant_id = %s
                order by created_at desc
                limit 80
                """,
                (tenant_id,),
            )
            data["themes"] = cur.fetchall()
        except Exception:
            conn.rollback()
        try:
            cur.execute(
                """
                select id, coalesce(hook_base, codigo, tese_central, objetivo) as title,
                       objetivo, classe_ivs, mecanismo, hook_base, tese_central, objecao_principal, adaptacao_ivs, created_at
                from viral_scripts
                where tenant_id = %s or tenant_id is null
                order by created_at desc
                limit 80
                """,
                (tenant_id,),
            )
            data["viral_scripts"] = cur.fetchall()
        except Exception:
            conn.rollback()
    return data


@router.get("/options")
def options() -> dict[str, Any]:
    payload = motion_video_options()
    payload["field_names"] = {
        "official_format_field": "content_format",
        "examples_entity": "content_format_examples",
        "do_not_use": ["format_brick", "lego_bricks"],
    }
    payload["workflow"] = [
        "Objetivo",
        "Objeção",
        "Formato de conteúdo",
        "Vídeos de exemplo",
        "Estratégia Narrativa",
        "Roteiro/Copy",
        "Motion Brief",
        "Prompts Higgsfield",
        "Gate compliance",
        "Aprovação de gasto",
    ]
    return payload


@router.get("/examples")
def examples(content_format: str | None = None, tenant_slug: str = "demo", include_archetypes: bool = True) -> dict[str, Any]:
    try:
        items = build_content_format_examples(content_format) if include_archetypes else []
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    with get_conn() as conn:
        tenant_id = _tenant_id(conn, tenant_slug)
        with conn.cursor() as cur:
            if content_format:
                cur.execute(
                    """
                    select id::text, content_format_key as content_format, source_type, source_handle_or_url,
                           external_id, content_url, thumbnail_url, transcript_summary, hook_summary,
                           retention_mechanism, why_this_example_works, compliance_risk,
                           ivs_applicability_score, metadata, created_at
                    from content_format_examples
                    where tenant_id=%s and content_format_key=%s
                    order by created_at desc
                    limit 120
                    """,
                    (tenant_id, content_format),
                )
            else:
                cur.execute(
                    """
                    select id::text, content_format_key as content_format, source_type, source_handle_or_url,
                           external_id, content_url, thumbnail_url, transcript_summary, hook_summary,
                           retention_mechanism, why_this_example_works, compliance_risk,
                           ivs_applicability_score, metadata, created_at
                    from content_format_examples
                    where tenant_id=%s
                    order by created_at desc
                    limit 240
                    """,
                    (tenant_id,),
                )
            db_items = cur.fetchall()
    for item in db_items:
        item["copy_guardrail"] = (item.get("metadata") or {}).get("copy_guardrail", "Referência governada: não copiar.")
        item["winner_candidate_type"] = (item.get("metadata") or {}).get("winner_candidate_type", "pending")
        item["origin"] = "db"
    for item in items:
        item["origin"] = "archetype"
    merged = db_items + items
    return {"items": merged, "count": len(merged), "content_format": content_format, "db_count": len(db_items), "archetype_count": len(items)}


@router.get("/matrix-8x8")
def matrix_8x8() -> dict[str, Any]:
    return motion_video_matrix_8x8()


@router.get("/winners")
def winners(content_format: str = "mito_que_prende") -> dict[str, Any]:
    try:
        items = example_winners_for_format(content_format)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return {"content_format": content_format, "items": items}


@router.post("/ingest-example")
def ingest_real_example(payload: RealExampleIngestRequest) -> dict[str, Any]:
    raw = payload.model_dump() if hasattr(payload, "model_dump") else payload.dict()
    try:
        item = normalize_real_content_format_example(raw)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    with get_conn() as conn:
        tenant_id = _tenant_id(conn, payload.tenant_slug)
        formats = _format_ids(conn, tenant_id)
        format_id = formats.get(item["content_format"])
        if not format_id:
            raise HTTPException(status_code=422, detail="rode /motion-videos/seed-formats antes de ingerir exemplos reais")
        with conn.cursor() as cur:
            _upsert_format_example(cur, tenant_id, format_id, item)
    return {"status": "ingested", "tenant_slug": payload.tenant_slug, "item": item}


@router.post("/seed-examples")
def seed_examples(tenant_slug: str = "demo") -> dict[str, Any]:
    examples = build_content_format_examples()
    with get_conn() as conn:
        tenant_id = _tenant_id(conn, tenant_slug)
        upserted = 0
        with conn.cursor() as cur:
            cur.execute("select key, id from content_formats where tenant_id=%s", (tenant_id,))
            format_ids = {row["key"]: row["id"] for row in cur.fetchall()}
            for item in examples:
                format_id = format_ids.get(item["content_format"])
                if not format_id:
                    continue
                cur.execute(
                    """
                    insert into content_format_examples (
                      tenant_id, content_format_id, content_format_key, source_type,
                      source_handle_or_url, external_id, content_url, thumbnail_url,
                      transcript_summary, hook_summary, why_this_example_works,
                      compliance_risk, ivs_applicability_score, metadata
                    ) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
                    on conflict (tenant_id, external_id) do update set
                      transcript_summary = excluded.transcript_summary,
                      hook_summary = excluded.hook_summary,
                      why_this_example_works = excluded.why_this_example_works,
                      compliance_risk = excluded.compliance_risk,
                      ivs_applicability_score = excluded.ivs_applicability_score,
                      metadata = excluded.metadata
                    """,
                    (
                        tenant_id,
                        format_id,
                        item["content_format"],
                        item["source_type"],
                        item["source_handle_or_url"],
                        item["external_id"],
                        item["content_url"],
                        item["thumbnail_url"],
                        item["transcript_summary"],
                        item["hook_summary"],
                        item["why_this_example_works"],
                        item["compliance_risk"],
                        item["ivs_applicability_score"],
                        json.dumps({
                            "retention_mechanism": item["retention_mechanism"],
                            "winner_candidate_type": item["winner_candidate_type"],
                            "copy_guardrail": item["copy_guardrail"],
                        }, ensure_ascii=False),
                    ),
                )
                upserted += 1
    return {"status": "seeded", "tenant_slug": tenant_slug, "content_format_examples": upserted}


@router.get("/sources")
def sources(tenant_slug: str = "demo") -> dict[str, Any]:
    with get_conn() as conn:
        tenant_id = _tenant_id(conn, tenant_slug)
        data = _safe_fetch_sources(conn, tenant_id)
    return {"tenant_slug": tenant_slug, **data}


@router.get("")
def list_projects(tenant_slug: str = "demo", limit: int = 30) -> dict[str, Any]:
    with get_conn() as conn:
        tenant_id = _tenant_id(conn, tenant_slug)
        with conn.cursor() as cur:
            try:
                cur.execute(
                    """
                    select id, title, topic, objective, objection, content_format, content_strategy,
                           screen_format, aspect_ratio, duration_seconds, blocks_count,
                           visual_preset, status, approval_status, created_at
                    from motion_video_projects
                    where tenant_id = %s
                    order by created_at desc
                    limit %s
                    """,
                    (tenant_id, min(max(limit, 1), 100)),
                )
                items = cur.fetchall()
            except Exception as exc:
                conn.rollback()
                raise HTTPException(status_code=503, detail=f"motion video tables not ready: {exc}")
    return {"items": items}


@router.get("/{project_id}")
def get_project(project_id: str, tenant_slug: str = "demo") -> dict[str, Any]:
    with get_conn() as conn:
        tenant_id = _tenant_id(conn, tenant_slug)
        with conn.cursor() as cur:
            cur.execute(
                """
                select * from motion_video_projects
                where id = %s and tenant_id = %s
                """,
                (project_id, tenant_id),
            )
            project = cur.fetchone()
            if not project:
                raise HTTPException(status_code=404, detail="motion video project not found")
            cur.execute(
                """
                select * from motion_video_blocks
                where project_id = %s
                order by block_index asc
                """,
                (project_id,),
            )
            blocks = cur.fetchall()
    return {"project": project, "blocks": blocks}


@router.post("/plan")
def create_plan(payload: MotionVideoPlanRequest) -> dict[str, Any]:
    raw = payload.model_dump() if hasattr(payload, "model_dump") else payload.dict()
    try:
        plan = build_motion_video_plan(raw)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    with get_conn() as conn:
        tenant_id = _tenant_id(conn, payload.tenant_slug)
        with conn.cursor() as cur:
            try:
                scores = plan["quality_scores_estimados"]
                cur.execute(
                    """
                    insert into motion_video_projects (
                      tenant_id, title, source_type, source_id, topic, thesis, objective, audience, objection,
                      content_format, content_strategy, source_example_ids, screen_format, aspect_ratio,
                      duration_seconds, blocks_count, visual_preset, narrative_pattern, voiceover,
                      status, approval_status, format_fit_score, example_abstraction_score,
                      objection_break_score, retention_score, compliance_score, ivs_avatar_score,
                      estimated_credits, plan_payload
                    ) values (
                      %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s,
                      %s, %s, %s, %s, %s, 'planned', 'plan_only', %s, %s, %s, %s, %s, %s,
                      %s::jsonb, %s::jsonb
                    ) returning id, created_at
                    """,
                    (
                        tenant_id,
                        plan["title"],
                        payload.source_type,
                        payload.source_id,
                        plan["topic"],
                        plan["thesis"],
                        plan["objective"],
                        payload.audience,
                        plan["objection"],
                        plan["content_format"],
                        plan["content_strategy"],
                        json.dumps(payload.source_example_ids),
                        plan["screen_format"],
                        plan["aspect_ratio"],
                        plan["duration_seconds"],
                        plan["blocks_count"],
                        plan["visual_preset"],
                        payload.narrative_pattern,
                        payload.voiceover,
                        scores["format_fit_score"],
                        scores["example_abstraction_score"],
                        scores["objection_break_score"],
                        scores["retention_score"],
                        scores["compliance_score"],
                        scores["ivs_avatar_score"],
                        json.dumps(plan["estimated_credits"]),
                        json.dumps(plan, ensure_ascii=False),
                    ),
                )
                row = cur.fetchone()
                project_id = row["id"]
                for block in plan["blocks"]:
                    cur.execute(
                        """
                        insert into motion_video_blocks (
                          project_id, block_index, narration_text, visual_prompt,
                          scene, motion, audio_prompt, negative_prompt, duration_sec, status
                        ) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'planned')
                        """,
                        (
                            project_id,
                            block["block_index"],
                            block["narration_text"],
                            block["visual_prompt"],
                            block["scene"],
                            block["motion"],
                            block["audio"],
                            block["negative_prompt"],
                            block["duration_sec"],
                        ),
                    )
            except Exception as exc:
                conn.rollback()
                raise HTTPException(status_code=503, detail=f"motion video tables not ready: {exc}")
    return {
        "status": "planned",
        "tenant_slug": payload.tenant_slug,
        "id": project_id,
        "created_at": row["created_at"],
        "approval_status": "plan_only",
        "payload": plan,
    }


@router.post("/{project_id}/approve-generation")
def approve_generation(project_id: str, tenant_slug: str = "demo") -> dict[str, Any]:
    with get_conn() as conn:
        tenant_id = _tenant_id(conn, tenant_slug)
        with conn.cursor() as cur:
            cur.execute(
                """
                update motion_video_projects
                set approval_status = 'approved_for_paid_generation', updated_at = now()
                where id = %s and tenant_id = %s
                returning id, approval_status
                """,
                (project_id, tenant_id),
            )
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="motion video project not found")
    return {"status": "approved", "project_id": row["id"], "approval_status": row["approval_status"]}


@router.post("/{project_id}/generate-clips")
def generate_clips_gate(project_id: str, tenant_slug: str = "demo") -> dict[str, Any]:
    with get_conn() as conn:
        tenant_id = _tenant_id(conn, tenant_slug)
        with conn.cursor() as cur:
            cur.execute(
                """
                select id, approval_status from motion_video_projects
                where id = %s and tenant_id = %s
                """,
                (project_id, tenant_id),
            )
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="motion video project not found")
            if row["approval_status"] != "approved_for_paid_generation":
                return {
                    "status": "needs_approval",
                    "message": "Geração Higgsfield exige aprovação antes do primeiro job pago.",
                    "approval_status": row["approval_status"],
                }
    return {
        "status": "queued_placeholder",
        "project_id": project_id,
        "message": "Worker Higgsfield pago ainda não habilitado nesta fase; plan-only está implementado.",
    }


@router.post("/seed-formats")
def seed_formats(tenant_slug: str = "demo") -> dict[str, Any]:
    with get_conn() as conn:
        tenant_id = _tenant_id(conn, tenant_slug)
        inserted = 0
        with conn.cursor() as cur:
            for item in CONTENT_FORMATS:
                cur.execute(
                    """
                    insert into content_formats (
                      tenant_id, key, name, description, best_for, objection_targets,
                      default_structure, motion_notes, prompt_bias, compliance_notes, enabled
                    ) values (%s, %s, %s, %s, %s::jsonb, %s::jsonb, %s::jsonb, %s, %s, %s, true)
                    on conflict (tenant_id, key) do update set
                      name = excluded.name,
                      description = excluded.description,
                      best_for = excluded.best_for,
                      objection_targets = excluded.objection_targets,
                      default_structure = excluded.default_structure,
                      motion_notes = excluded.motion_notes,
                      prompt_bias = excluded.prompt_bias,
                      compliance_notes = excluded.compliance_notes,
                      enabled = true
                    """,
                    (
                        tenant_id,
                        item["key"],
                        item["name"],
                        item["description"],
                        json.dumps(item["best_for"]),
                        json.dumps(item["objection_targets"]),
                        json.dumps(item["default_structure"]),
                        item["motion_notes"],
                        item["prompt_bias"],
                        item["compliance_notes"],
                    ),
                )
                inserted += 1
    return {"status": "seeded", "tenant_slug": tenant_slug, "content_formats": inserted}
