"""meta_insights_ingest.py — Métricas privadas do Instagram (Meta Insights) no Content Engine OS.

Usa a Graph API oficial (token de usuário do sistema, nunca expira) e grava, idempotente por dia:
  - meta_profile_insights_daily   → reach, views, visitas ao perfil, contas engajadas, cliques
  - meta_audience_demographics    → seguidores por cidade / faixa etária / gênero (snapshot)
  - meta_online_followers         → seguidores online por hora do dia (quando a Meta disponibiliza)
  - meta_media_insights_daily     → por publicação: reach, saved, shares, views, retenção de reels
  - meta_story_insights           → por story no ar: views, replies, navegação (efêmero — coleta diária)

Complementa o instagram_ingest.py (RapidAPI, dados públicos). O que o scraper não vê, entra aqui.

O rótulo de dia (metric_date=D) segue o bucket diário da própria Meta — o mesmo número que o
painel do Instagram mostra para o dia D (ver _bucket_window). O dia D é reprocessado nas
coletas de D+1 e D+2 porque a Meta corrige/consolida os agregados com atraso.
Cada seção roda na própria transação: uma falha (HTTP ou SQL) não descarta as demais.

Rodar no host:  docker exec --env-file /root/.openclaw/secure/meta_insights.env \
                  content-engine-api python scripts/meta_insights_ingest.py
Config por env: META_IG_TOKEN (obrigatório), META_IG_USER_ID (default conta da Dra),
                IG_TENANT_SLUG (default demo), META_MEDIA_LIMIT (default 30).
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys

import httpx

sys.path.insert(0, "/app")
from app.db import get_conn  # noqa: E402

TOKEN = os.environ.get("META_IG_TOKEN", "")
IG_ID = os.environ.get("META_IG_USER_ID", "17841400449703531")
TENANT_SLUG = os.environ.get("IG_TENANT_SLUG", "demo")
MEDIA_LIMIT = int(os.environ.get("META_MEDIA_LIMIT", "30"))
GRAPH = "https://graph.facebook.com/v23.0"
SOURCE = "meta_graph:v23.0"
BRT = dt.timezone(dt.timedelta(hours=-3))  # Brasil sem horário de verão desde 2019

# Métricas de perfil agregadas por dia (metric_type=total_value)
PROFILE_TOTAL_METRICS = [
    "views", "profile_views", "accounts_engaged", "total_interactions",
    "likes", "comments", "shares", "saves", "replies", "website_clicks",
]
# Métricas por publicação (lifetime). Reels têm extras de retenção.
MEDIA_METRICS_BASE = ["reach", "views", "saved", "shares", "likes", "comments", "total_interactions"]
MEDIA_METRICS_REELS = MEDIA_METRICS_BASE + ["ig_reels_avg_watch_time", "ig_reels_video_view_total_time"]
STORY_METRICS = ["views", "reach", "replies", "shares", "total_interactions", "profile_visits", "navigation"]

DDL = """
create table if not exists meta_profile_insights_daily (
  id bigserial primary key,
  tenant_id uuid not null,
  metric_date date not null,
  ig_user_id text not null,
  metrics jsonb not null default '{}'::jsonb,
  source text not null,
  collected_at timestamptz not null default now(),
  unique (tenant_id, ig_user_id, metric_date)
);
create table if not exists meta_audience_demographics (
  id bigserial primary key,
  tenant_id uuid not null,
  snapshot_date date not null,
  ig_user_id text not null,
  dimension text not null,
  dimension_value text not null,
  followers integer not null,
  source text not null,
  unique (tenant_id, ig_user_id, snapshot_date, dimension, dimension_value)
);
create table if not exists meta_online_followers (
  id bigserial primary key,
  tenant_id uuid not null,
  metric_date date not null,
  ig_user_id text not null,
  hour_of_day smallint not null,
  followers_online integer not null,
  source text not null,
  unique (tenant_id, ig_user_id, metric_date, hour_of_day)
);
create table if not exists meta_media_insights_daily (
  id bigserial primary key,
  tenant_id uuid not null,
  snapshot_date date not null,
  ig_user_id text not null,
  media_id text not null,
  permalink text,
  media_product_type text,
  media_type text,
  published_at timestamptz,
  caption_excerpt text,
  like_count integer,
  comments_count integer,
  metrics jsonb not null default '{}'::jsonb,
  source text not null,
  unique (tenant_id, ig_user_id, snapshot_date, media_id)
);
create table if not exists meta_story_insights (
  id bigserial primary key,
  tenant_id uuid not null,
  story_id text not null,
  published_at timestamptz,
  caption_excerpt text,
  metrics jsonb not null default '{}'::jsonb,
  last_seen_date date not null,
  source text not null,
  unique (tenant_id, story_id)
);
"""


def _is_auth_error(exc: httpx.HTTPStatusError) -> bool:
    """Token inválido/escopo revogado não pode virar 'métrica indisponível' silenciosa."""
    if exc.response.status_code in (401, 403):
        return True
    try:
        err = exc.response.json().get("error", {})
    except Exception:
        return False
    code = err.get("code")
    return code in (190, 102, 10) or 200 <= (code or 0) <= 299


def _get(cli: httpx.Client, path: str, **params) -> dict:
    params["access_token"] = TOKEN
    r = cli.get(f"{GRAPH}/{path}", params=params, timeout=40)
    r.raise_for_status()
    return r.json()


def _get_paged(cli: httpx.Client, path: str, max_items: int, **params) -> list[dict]:
    """Segue paging.next até max_items (a Meta pagina em ~25 por padrão)."""
    params["limit"] = min(max_items, 100)
    out: list[dict] = []
    payload = _get(cli, path, **params)
    while True:
        out.extend(payload.get("data", []))
        nxt = (payload.get("paging") or {}).get("next")
        if not nxt or len(out) >= max_items:
            return out[:max_items]
        r = cli.get(nxt, timeout=40)
        r.raise_for_status()
        payload = r.json()


def _parse_totals(payload: dict) -> dict[str, object]:
    out: dict[str, object] = {}
    for item in payload.get("data", []):
        name = item.get("name")
        if "total_value" in item:
            tv = item["total_value"]
            out[name] = tv.get("breakdowns", tv.get("value"))
        elif item.get("values"):
            out[name] = item["values"][-1].get("value")
    return out


def _insights(cli: httpx.Client, obj_id: str, metrics: list[str], **params) -> dict[str, object]:
    """Busca insights em lote; se a Meta rejeitar o conjunto, cai para métrica a métrica.

    Métricas indisponíveis para o objeto são omitidas; erro de autenticação/permissão sobe.
    """
    try:
        return _parse_totals(_get(cli, f"{obj_id}/insights", metric=",".join(metrics), **params))
    except httpx.HTTPStatusError as exc:
        if _is_auth_error(exc):
            raise
        out: dict[str, object] = {}
        for m in metrics:
            try:
                out.update(_parse_totals(_get(cli, f"{obj_id}/insights", metric=m, **params)))
            except httpx.HTTPStatusError as exc2:
                if _is_auth_error(exc2):
                    raise
                continue
        return out


def _bucket_window(day: dt.date) -> tuple[int, int]:
    """Janela que captura exatamente o bucket diário da Meta para o dia D.

    A Meta agrega os insights de conta em buckets fixos de dia no fuso Pacific (igual ao app
    do Instagram), e uma consulta com since/until retorna os buckets cujo FIM cai dentro da
    janela. O bucket do dia D termina em (D+1) às 07:00Z (PDT) ou 08:00Z (PST); a janela
    [(D+1) 00:00Z, (D+1) 12:00Z] contém exatamente esse fim nos dois casos.
    """
    nxt = dt.datetime.combine(day + dt.timedelta(days=1), dt.time.min, tzinfo=dt.timezone.utc)
    return int(nxt.timestamp()), int(nxt.timestamp()) + 12 * 3600


def _brt_day_window(day: dt.date) -> tuple[int, int]:
    """Janela de dia BRT completa [D 00:00, D+1 00:00). A métrica follows_and_unfollows,
    diferente das total_value de tráfego, só retorna 'results' com a janela de 24h da conta."""
    start = dt.datetime.combine(day, dt.time.min, tzinfo=BRT)
    return int(start.timestamp()), int((start + dt.timedelta(days=1)).timestamp())


def _today_brt() -> dt.date:
    return dt.datetime.now(BRT).date()


def ingest_profile(cli: httpx.Client, cur, tid) -> int:
    """Grava ontem e anteontem (buckets fechados; reprocessa p/ capturar correções da Meta).

    O rótulo metric_date=D corresponde ao mesmo dia que o painel do Instagram mostra para D.
    """
    days = [_today_brt() - dt.timedelta(days=2), _today_brt() - dt.timedelta(days=1)]
    n = 0
    for day in days:
        since, until = _bucket_window(day)
        metrics = _insights(cli, IG_ID, PROFILE_TOTAL_METRICS,
                            metric_type="total_value", period="day", since=since, until=until)
        reach = _insights(cli, IG_ID, ["reach"], period="day", since=since, until=until)
        metrics.update(reach)
        # saldo líquido oficial de seguidores no dia (contas que passaram a seguir menos as que
        # deixaram de seguir/saíram); breakdown FOLLOWER isola quem já é do público de perfis
        fu_since, fu_until = _brt_day_window(day)
        fu = _insights(cli, IG_ID, ["follows_and_unfollows"], metric_type="total_value",
                       breakdown="follow_type", period="day", since=fu_since, until=fu_until)
        net = fu.get("follows_and_unfollows")
        if isinstance(net, list):
            for bd in net:
                for res in bd.get("results", []):
                    if (res.get("dimension_values") or [""])[0] == "FOLLOWER":
                        metrics["net_follower_change"] = res.get("value")
        if not metrics:
            continue
        cur.execute(
            "insert into meta_profile_insights_daily (tenant_id, metric_date, ig_user_id, metrics, source) "
            "values (%s, %s, %s, %s::jsonb, %s) "
            "on conflict (tenant_id, ig_user_id, metric_date) do update "
            "set metrics = excluded.metrics, collected_at = now()",
            (tid, day, IG_ID, json.dumps(metrics), SOURCE))
        n += 1
    return n


def ingest_demographics(cli: httpx.Client, cur, tid) -> int:
    # Busca tudo antes de tocar no banco: se a API falhar no meio, o snapshot antigo sobrevive.
    rows: list[tuple[str, str, int]] = []
    for dim in ("city", "age", "gender"):
        data = _insights(cli, IG_ID, ["follower_demographics"],
                         period="lifetime", metric_type="total_value", breakdown=dim)
        breakdowns = data.get("follower_demographics") or []
        if not isinstance(breakdowns, list):
            continue
        for bd in breakdowns:
            for res in bd.get("results", []):
                vals = res.get("dimension_values") or ["?"]
                rows.append((dim, vals[0][:120], int(res.get("value") or 0)))
    if not rows:
        return 0
    cur.execute("delete from meta_audience_demographics "
                "where tenant_id=%s and ig_user_id=%s and snapshot_date=current_date", (tid, IG_ID))
    for dim, value, followers in rows:
        cur.execute(
            "insert into meta_audience_demographics "
            "(tenant_id, snapshot_date, ig_user_id, dimension, dimension_value, followers, source) "
            "values (%s, current_date, %s, %s, %s, %s, %s) on conflict do nothing",
            (tid, IG_ID, dim, value, followers, SOURCE))
    return len(rows)


def ingest_online_followers(cli: httpx.Client, cur, tid) -> int:
    payload = _get(cli, f"{IG_ID}/insights", metric="online_followers", period="lifetime")
    n = 0
    for item in payload.get("data", []):
        for v in item.get("values", []):
            end = (v.get("end_time") or "")[:10]
            hours = v.get("value") or {}
            if not end or not isinstance(hours, dict):
                continue
            for hour, count in hours.items():
                cur.execute(
                    "insert into meta_online_followers "
                    "(tenant_id, metric_date, ig_user_id, hour_of_day, followers_online, source) "
                    "values (%s, %s, %s, %s, %s, %s) "
                    "on conflict (tenant_id, ig_user_id, metric_date, hour_of_day) do update "
                    "set followers_online = excluded.followers_online",
                    (tid, end, IG_ID, int(hour), int(count or 0), SOURCE))
                n += 1
    return n


def ingest_media(cli: httpx.Client, cur, tid) -> int:
    fields = "id,media_type,media_product_type,timestamp,permalink,caption,like_count,comments_count"
    medias = _get_paged(cli, f"{IG_ID}/media", MEDIA_LIMIT, fields=fields)
    # Coleta os insights de todas antes do delete: snapshot antigo só sai quando o novo está pronto.
    enriched: list[tuple[dict, dict]] = []
    for m in medias:
        is_reel = (m.get("media_product_type") or "").upper() == "REELS"
        metrics = _insights(cli, m["id"], MEDIA_METRICS_REELS if is_reel else MEDIA_METRICS_BASE)
        enriched.append((m, metrics))
    cur.execute("delete from meta_media_insights_daily "
                "where tenant_id=%s and ig_user_id=%s and snapshot_date=current_date", (tid, IG_ID))
    n = 0
    for m, metrics in enriched:
        cur.execute(
            "insert into meta_media_insights_daily "
            "(tenant_id, snapshot_date, ig_user_id, media_id, permalink, media_product_type, media_type, "
            " published_at, caption_excerpt, like_count, comments_count, metrics, source) "
            "values (%s, current_date, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s) "
            "on conflict (tenant_id, ig_user_id, snapshot_date, media_id) do update "
            "set metrics = excluded.metrics, like_count = excluded.like_count, "
            "    comments_count = excluded.comments_count",
            (tid, IG_ID, m["id"], m.get("permalink"), m.get("media_product_type"), m.get("media_type"),
             m.get("timestamp"), (m.get("caption") or "")[:280],
             m.get("like_count"), m.get("comments_count"), json.dumps(metrics), SOURCE))
        n += 1
    return n


def ingest_stories(cli: httpx.Client, cur, tid) -> int:
    stories = _get_paged(cli, f"{IG_ID}/stories", 100, fields="id,timestamp,caption")
    n = 0
    for s in stories:
        metrics = _insights(cli, s["id"], STORY_METRICS)
        # métricas vazias (ex.: janela de permissão) não sobrescrevem coleta anterior boa
        cur.execute(
            "insert into meta_story_insights "
            "(tenant_id, story_id, published_at, caption_excerpt, metrics, last_seen_date, source) "
            "values (%s, %s, %s, %s, %s::jsonb, current_date, %s) "
            "on conflict (tenant_id, story_id) do update set "
            "  metrics = case when excluded.metrics = '{}'::jsonb "
            "            then meta_story_insights.metrics else excluded.metrics end, "
            "  last_seen_date = excluded.last_seen_date",
            (tid, s["id"], s.get("timestamp"), (s.get("caption") or "")[:280],
             json.dumps(metrics), SOURCE))
        n += 1
    return n


def main() -> None:
    if not TOKEN:
        raise SystemExit("META_IG_TOKEN ausente (rode com --env-file /root/.openclaw/secure/meta_insights.env)")

    results: dict[str, object] = {}
    with get_conn() as conn:
        with conn.transaction(), conn.cursor() as cur:
            cur.execute(DDL)
            cur.execute("select id from tenants where slug=%s", (TENANT_SLUG,))
            row = cur.fetchone()
            if not row:
                raise SystemExit(f"tenant '{TENANT_SLUG}' não encontrado")
            tid = row["id"]

        with httpx.Client() as cli:
            for name, fn in (("perfil", ingest_profile), ("demografia", ingest_demographics),
                             ("online", ingest_online_followers), ("midia", ingest_media),
                             ("stories", ingest_stories)):
                # transação por seção: falha (HTTP ou SQL) reverte só a própria seção
                try:
                    with conn.transaction(), conn.cursor() as cur:
                        results[name] = fn(cli, cur, tid)
                except Exception as exc:
                    results[name] = f"ERRO: {exc}"

    print(f"OK meta-insights @{IG_ID}: " + " ".join(f"{k}={v}" for k, v in results.items()))
    if any(str(v).startswith("ERRO") for v in results.values()):
        sys.exit(1)


if __name__ == "__main__":
    main()
