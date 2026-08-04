"""metrics_autolink.py — fecha o ciclo publicar → medir sem digitação manual.

O que faz, em ordem (tudo idempotente, re-rodável todo dia):
  1. AUTO-VÍNCULO: entrada de calendário publicada pelo 1-clique (publishing.py) ganha o
     shortcode do post real via cadeia creative_id → meta_ig_publications.permalink.
  2. BACKFILL (--backfill): post real dos últimos 90 dias que não tem entrada no calendário
     vira entrada 'published' (título = legenda truncada) — o aprendizado nasce alimentado.
  3. MEDIÇÃO: toda entrada com ig_shortcode recebe a última snapshot de métricas —
     meta_media_insights_daily (Graph API, preferida) com fallback em
     instagram_publication_daily_metrics (scraper) — e vira status 'medido'.
     O merge (jsonb ||) preserva campos digitados à mão (leads, agendamentos, notes).

Shortcode é a chave canônica: o MESMO post é /p/X no scraper e /reel/X na Graph API.

Rodar no host:  docker exec content-engine-api python scripts/metrics_autolink.py --tenant demo --backfill
Cron diário 07:30 (sem --backfill não cria entradas novas, só vincula e mede).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import time

sys.path.insert(0, "/app")
from app.db import get_conn  # noqa: E402

os.environ.setdefault("TZ", "America/Sao_Paulo")
if hasattr(time, "tzset"):
    time.tzset()

BRT = dt.timezone(dt.timedelta(hours=-3))  # Brasil sem horário de verão desde 2019
SHORTCODE_RE = re.compile(r"/(?:p|reel|tv)/([A-Za-z0-9_-]+)")
# regex equivalente dentro do Postgres (substring com grupo de captura)
SQL_SHORTCODE = r"substring(%s from '/(?:p|reel|tv)/([A-Za-z0-9_-]+)')"


def _shortcode(url: str | None) -> str | None:
    if not url:
        return None
    m = SHORTCODE_RE.search(url)
    return m.group(1) if m else None


def _tenant_id(conn, slug: str) -> str:
    with conn.cursor() as cur:
        cur.execute("select id from tenants where slug=%s", (slug,))
        row = cur.fetchone()
    if not row:
        raise SystemExit(f"tenant '{slug}' não encontrado")
    return row["id"]


def ensure_schema(conn) -> None:
    with conn.cursor() as cur:
        cur.execute("alter table calendar_entries add column if not exists ig_shortcode text")
        cur.execute("alter table calendar_entries add column if not exists published_url text")
        cur.execute("create index if not exists idx_calendar_entries_shortcode on "
                    "calendar_entries(tenant_id, ig_shortcode) where ig_shortcode is not null")


def autolink(conn, tid: str) -> int:
    """Entrada published sem shortcode + criativo publicado pelo 1-clique → shortcode do permalink."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select e.id, p.permalink
            from calendar_entries e
            join meta_ig_publications p
              on p.tenant_id = e.tenant_id and p.creative_id = e.creative_id
            where e.tenant_id = %s
              and e.ig_shortcode is null
              and e.creative_id is not null
              and p.permalink is not null
            """,
            (tid,),
        )
        rows = cur.fetchall()
        n = 0
        for r in rows:
            sc = _shortcode(r["permalink"])
            if not sc:
                continue
            cur.execute(
                """
                update calendar_entries
                set ig_shortcode=%s,
                    published_url=%s,
                    status=case when status='medido' then status else 'published' end,
                    published_at=coalesce(published_at, now())
                where id=%s
                """,
                (sc, r["permalink"], r["id"]),
            )
            n += 1
    return n


def _format_for(media_product_type: str | None, media_type: str | None) -> str:
    if (media_product_type or "").upper() == "REELS":
        return "reel"
    mt = (media_type or "").upper()
    if mt == "CAROUSEL_ALBUM":
        return "carrossel"
    if mt == "IMAGE":
        return "post_estatico"
    if mt == "VIDEO":
        return "reel"
    return "feed_post"


def backfill(conn, tid: str, days: int = 90) -> int:
    """Post real sem entrada de calendário vira entrada 'published' já vinculada."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select distinct on (m.media_id)
                   m.media_id, m.permalink, m.caption_excerpt, m.media_type,
                   m.media_product_type, m.published_at
            from meta_media_insights_daily m
            where m.tenant_id = %s
              and m.permalink is not null
              and m.published_at >= now() - make_interval(days => %s)
            order by m.media_id, m.snapshot_date desc
            """,
            (tid, days),
        )
        posts = cur.fetchall()
        cur.execute(
            "select ig_shortcode from calendar_entries where tenant_id=%s and ig_shortcode is not null",
            (tid,),
        )
        existentes = {r["ig_shortcode"] for r in cur.fetchall()}
        n = 0
        for p in posts:
            sc = _shortcode(p["permalink"])
            if not sc or sc in existentes:
                continue
            caption = " ".join((p.get("caption_excerpt") or "").split()).strip()
            title = caption[:80] + ("…" if len(caption) > 80 else "") if caption else f"Post do Instagram ({sc})"
            cur.execute(
                """
                insert into calendar_entries
                    (tenant_id, title, format, channel, status, published_at,
                     ig_shortcode, published_url, origin_tag, notes)
                values (%s, %s, %s, 'instagram', 'published', %s, %s, %s,
                        'backfill_instagram', 'Criada automaticamente a partir do post real no Instagram.')
                """,
                (tid, title, _format_for(p.get("media_product_type"), p.get("media_type")),
                 p.get("published_at"), sc, p["permalink"]),
            )
            existentes.add(sc)
            n += 1
    return n


def _metrics_from_meta(row: dict) -> dict:
    """meta_media_insights_daily → campos que o calendar.py já usa no registro manual."""
    m = row.get("metrics") or {}
    if isinstance(m, str):
        m = json.loads(m)
    out = {
        "reach": m.get("reach"),
        "views": m.get("views"),
        "likes": m.get("likes", row.get("like_count")),
        "comments": m.get("comments", row.get("comments_count")),
        "shares": m.get("shares"),
        "saves": m.get("saved"),
    }
    return {k: v for k, v in out.items() if v is not None}


def _metrics_from_scraper(row: dict) -> dict:
    """instagram_publication_daily_metrics → mesmos campos do registro manual."""
    out = {
        "reach": row.get("reach"),
        "views": row.get("views"),
        "likes": row.get("likes"),
        "comments": row.get("comments"),
        "shares": row.get("shares"),
        "saves": row.get("saves"),
        "profile_clicks": row.get("profile_visits"),
        "whatsapp_clicks": row.get("whatsapp_clicks"),
    }
    return {k: v for k, v in out.items() if v is not None}


def measure(conn, tid: str) -> dict:
    """Última snapshot por shortcode (Graph preferida, scraper fallback) → upsert na entrada."""
    with conn.cursor() as cur:
        cur.execute(
            "select id, creative_id, ig_shortcode from calendar_entries "
            "where tenant_id=%s and ig_shortcode is not null",
            (tid,),
        )
        entries = cur.fetchall()
        if not entries:
            return {"medidas": 0, "fonte_meta": 0, "fonte_scraper": 0, "sem_metricas": 0}
        shortcodes = sorted({e["ig_shortcode"] for e in entries})

        # última snapshot da Graph API por shortcode
        cur.execute(
            f"""
            select distinct on (sc) * from (
                select {SQL_SHORTCODE % 'permalink'} as sc, m.*
                from meta_media_insights_daily m
                where m.tenant_id = %s and m.permalink is not null
            ) t
            where sc = any(%s)
            order by sc, snapshot_date desc
            """,
            (tid, shortcodes),
        )
        meta_by_sc = {r["sc"]: r for r in cur.fetchall()}

        # última snapshot do scraper por shortcode (fallback)
        cur.execute(
            f"""
            select distinct on (sc) * from (
                select {SQL_SHORTCODE % 'publication_url'} as sc, i.*
                from instagram_publication_daily_metrics i
                where i.tenant_id = %s and i.publication_url is not null
            ) t
            where sc = any(%s)
            order by sc, metric_date desc
            """,
            (tid, shortcodes),
        )
        scraper_by_sc = {r["sc"]: r for r in cur.fetchall()}

        counts = {"medidas": 0, "fonte_meta": 0, "fonte_scraper": 0, "sem_metricas": 0}
        for e in entries:
            sc = e["ig_shortcode"]
            if sc in meta_by_sc:
                metrics = _metrics_from_meta(meta_by_sc[sc])
                metrics["fonte"] = "meta_graph"
                metrics["snapshot"] = str(meta_by_sc[sc]["snapshot_date"])
                counts["fonte_meta"] += 1
            elif sc in scraper_by_sc:
                metrics = _metrics_from_scraper(scraper_by_sc[sc])
                metrics["fonte"] = "instagram_scraper"
                metrics["snapshot"] = str(scraper_by_sc[sc]["metric_date"])
                counts["fonte_scraper"] += 1
            else:
                counts["sem_metricas"] += 1
                continue
            # merge jsonb: métricas automáticas atualizam, campos manuais (leads,
            # agendamentos, notes) que não vêm da API são preservados
            cur.execute(
                """
                update calendar_entries
                set metrics = coalesce(metrics, '{}'::jsonb) || %s::jsonb,
                    metrics_recorded_at = now(),
                    status = 'medido'
                where id = %s
                returning creative_id, metrics
                """,
                (json.dumps(metrics, ensure_ascii=False), e["id"]),
            )
            row = cur.fetchone()
            counts["medidas"] += 1
            # espelha em publications quando há criativo (mesmo comportamento do registro manual)
            if row and row.get("creative_id"):
                cur.execute(
                    """
                    insert into publications (tenant_id, creative_id, format, published_at, metrics, platform)
                    select tenant_id, creative_id, format, coalesce(published_at, now()), %s::jsonb, channel
                    from calendar_entries where id=%s
                    on conflict (creative_id) where creative_id is not null do update set
                        metrics = excluded.metrics,
                        published_at = coalesce(publications.published_at, excluded.published_at),
                        platform = coalesce(publications.platform, excluded.platform)
                    """,
                    (json.dumps(row["metrics"], ensure_ascii=False)
                     if not isinstance(row["metrics"], str) else row["metrics"], e["id"]),
                )
    return counts


def main() -> None:
    ap = argparse.ArgumentParser(description="Auto-vínculo e medição de posts do Instagram no calendário")
    ap.add_argument("--tenant", default="demo", help="slug do tenant (default: demo)")
    ap.add_argument("--backfill", action="store_true",
                    help="cria entradas published para posts reais dos últimos 90d sem entrada")
    ap.add_argument("--backfill-days", type=int, default=90)
    args = ap.parse_args()

    with get_conn() as conn:
        with conn.transaction():
            ensure_schema(conn)
        tid = _tenant_id(conn, args.tenant)

        results: dict[str, object] = {}
        with conn.transaction():
            results["vinculadas_1clique"] = autolink(conn, tid)
        if args.backfill:
            with conn.transaction():
                results["criadas_backfill"] = backfill(conn, tid, args.backfill_days)
        with conn.transaction():
            results.update(measure(conn, tid))

    hoje = dt.datetime.now(BRT).strftime("%Y-%m-%d %H:%M")
    print(f"OK metrics-autolink [{hoje} BRT] tenant={args.tenant}: "
          + " ".join(f"{k}={v}" for k, v in results.items()))


if __name__ == "__main__":
    main()
