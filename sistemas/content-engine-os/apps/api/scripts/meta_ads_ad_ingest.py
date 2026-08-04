"""meta_ads_ad_ingest.py — Performance do Meta Ads NO NÍVEL DO ANÚNCIO (criativo a criativo).

Irmão do meta_ads_ingest.py (campanha): mesmo token/conta, level=ad, e grava idempotente
por (dia × anúncio) em meta_ads_ad_insights_daily. Também sincroniza os metadados de cada
criativo (título, corpo, thumbnail, formato) em meta_ads_creatives — é o que permite o
"detalhe do detalhe": analisar cada criativo e casar com os leads CTWA do WhatsApp
(externalAdReply.sourceId/título).

Rodar no host:  docker exec --env-file /root/.openclaw/secure/meta_insights.env \
                  content-engine-api python scripts/meta_ads_ad_ingest.py
Config por env: META_IG_TOKEN (obrigatório), META_AD_ACCOUNT, IG_TENANT_SLUG,
                META_ADS_AD_DAYS (default 14; use 30 no backfill).
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
AD_ACCOUNT = os.environ.get("META_AD_ACCOUNT", "act_1451185309998325")
TENANT_SLUG = os.environ.get("IG_TENANT_SLUG", "demo")
DAYS = int(os.environ.get("META_ADS_AD_DAYS", "14"))
GRAPH = "https://graph.facebook.com/v23.0"
SOURCE = "meta_graph:ads_ad:v23.0"
BRT = dt.timezone(dt.timedelta(hours=-3))

FIELDS = ("ad_id,ad_name,adset_id,adset_name,campaign_id,campaign_name,"
          "spend,impressions,reach,clicks,ctr,cpc,cpm,frequency,"
          "actions,video_thruplay_watched_actions,video_play_actions")

DDL_INSIGHTS = """
create table if not exists meta_ads_ad_insights_daily (
  id bigserial primary key,
  tenant_id uuid not null,
  metric_date date not null,
  ad_account_id text not null,
  campaign_id text not null,
  campaign_name text,
  adset_id text,
  adset_name text,
  ad_id text not null,
  ad_name text,
  spend numeric(12,2),
  impressions bigint,
  reach bigint,
  clicks bigint,
  link_clicks bigint,
  messaging_starts bigint,
  leads bigint,
  video_plays bigint,
  video_thruplays bigint,
  ctr numeric(8,4),
  cpc numeric(10,4),
  cpm numeric(10,4),
  frequency numeric(8,4),
  actions jsonb not null default '[]'::jsonb,
  source text not null,
  collected_at timestamptz not null default now(),
  unique (tenant_id, ad_account_id, metric_date, ad_id)
);
"""

DDL_CREATIVES = """
create table if not exists meta_ads_creatives (
  ad_id text primary key,
  tenant_id uuid not null,
  ad_account_id text not null,
  campaign_id text,
  adset_id text,
  ad_name text,
  status text,
  creative_id text,
  title text,
  body text,
  thumbnail_url text,
  object_type text,
  instagram_permalink text,
  updated_at timestamptz not null default now()
);
"""

ACT_MSG = ("onsite_conversion.messaging_conversation_started_7d",)
ACT_LEAD_GROUPED = ("onsite_conversion.lead_grouped", "leadgen_grouped")
ACT_LINK = ("link_click",)


def _action(actions: list[dict], names: tuple[str, ...]) -> int:
    total = 0
    for a in actions or []:
        if a.get("action_type") in names:
            try:
                total += int(float(a.get("value") or 0))
            except (TypeError, ValueError):
                pass
    return total


def _leads(actions: list[dict]) -> int:
    for a in actions or []:
        if a.get("action_type") == "lead":
            try:
                return int(float(a.get("value") or 0))
            except (TypeError, ValueError):
                return 0
    return _action(actions, ACT_LEAD_GROUPED)


def _video_total(items: list[dict] | None) -> int:
    total = 0
    for a in items or []:
        try:
            total += int(float(a.get("value") or 0))
        except (TypeError, ValueError):
            pass
    return total


def _paged(cli: httpx.Client, url: str, params: dict) -> list[dict]:
    rows, first, pages = [], True, 0
    while url:
        pages += 1
        if pages > 80:
            raise RuntimeError("paginação passou de 80 páginas — abortando")
        r = cli.get(url, params=params if first else None, timeout=60)
        r.raise_for_status()
        payload = r.json()
        rows.extend(payload.get("data", []))
        url, first = (payload.get("paging") or {}).get("next"), False
    return rows


def fetch_ad_insights(cli: httpx.Client) -> list[dict]:
    until = dt.datetime.now(BRT).date() - dt.timedelta(days=1)
    since = until - dt.timedelta(days=DAYS - 1)
    return _paged(cli, f"{GRAPH}/{AD_ACCOUNT}/insights", {
        "level": "ad",
        "fields": FIELDS,
        "time_increment": 1,
        "time_range": json.dumps({"since": since.isoformat(), "until": until.isoformat()}),
        "limit": 500,
        "access_token": TOKEN,
    })


def fetch_creatives(cli: httpx.Client) -> list[dict]:
    """Metadados dos anúncios da conta (inclui pausados — histórico de leads CTWA precisa)."""
    return _paged(cli, f"{GRAPH}/{AD_ACCOUNT}/ads", {
        "fields": ("id,name,status,campaign_id,adset_id,"
                   "creative{id,title,body,thumbnail_url,object_type,instagram_permalink_url}"),
        "thumbnail_width": 512,   # sem isso a Meta devolve 64x64 — pequeno demais p/ card visual
        "thumbnail_height": 512,
        "limit": 200,
        "access_token": TOKEN,
    })


def main() -> None:
    if not TOKEN:
        raise SystemExit("META_IG_TOKEN ausente (rode com --env-file /root/.openclaw/secure/meta_insights.env)")

    with httpx.Client() as cli:
        insights = fetch_ad_insights(cli)
        ads_meta = fetch_creatives(cli)

    n_ins = n_cre = 0
    with get_conn() as conn:
        with conn.transaction(), conn.cursor() as cur:
            cur.execute(DDL_INSIGHTS)
            cur.execute(DDL_CREATIVES)
            cur.execute("select id from tenants where slug=%s", (TENANT_SLUG,))
            row = cur.fetchone()
            if not row:
                raise SystemExit(f"tenant '{TENANT_SLUG}' não encontrado")
            tid = row["id"]

            for r in insights:
                actions = r.get("actions") or []
                cur.execute(
                    """
                    insert into meta_ads_ad_insights_daily
                      (tenant_id, metric_date, ad_account_id, campaign_id, campaign_name,
                       adset_id, adset_name, ad_id, ad_name,
                       spend, impressions, reach, clicks, link_clicks, messaging_starts, leads,
                       video_plays, video_thruplays, ctr, cpc, cpm, frequency, actions, source)
                    values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s)
                    on conflict (tenant_id, ad_account_id, metric_date, ad_id) do update set
                      campaign_id = excluded.campaign_id, campaign_name = excluded.campaign_name,
                      adset_id = excluded.adset_id, adset_name = excluded.adset_name,
                      ad_name = excluded.ad_name, spend = excluded.spend,
                      impressions = excluded.impressions, reach = excluded.reach,
                      clicks = excluded.clicks, link_clicks = excluded.link_clicks,
                      messaging_starts = excluded.messaging_starts, leads = excluded.leads,
                      video_plays = excluded.video_plays, video_thruplays = excluded.video_thruplays,
                      ctr = excluded.ctr, cpc = excluded.cpc, cpm = excluded.cpm,
                      frequency = excluded.frequency, actions = excluded.actions,
                      collected_at = now()
                    """,
                    (tid, r.get("date_start"), AD_ACCOUNT, r.get("campaign_id"),
                     r.get("campaign_name"), r.get("adset_id"), r.get("adset_name"),
                     r.get("ad_id"), r.get("ad_name"),
                     r.get("spend"), r.get("impressions"), r.get("reach"), r.get("clicks"),
                     _action(actions, ACT_LINK), _action(actions, ACT_MSG), _leads(actions),
                     _video_total(r.get("video_play_actions")),
                     _video_total(r.get("video_thruplay_watched_actions")),
                     r.get("ctr"), r.get("cpc"), r.get("cpm"), r.get("frequency"),
                     json.dumps(actions), SOURCE))
                n_ins += 1

            for a in ads_meta:
                cre = a.get("creative") or {}
                cur.execute(
                    """
                    insert into meta_ads_creatives
                      (ad_id, tenant_id, ad_account_id, campaign_id, adset_id, ad_name, status,
                       creative_id, title, body, thumbnail_url, object_type, instagram_permalink)
                    values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    on conflict (ad_id) do update set
                      campaign_id = excluded.campaign_id, adset_id = excluded.adset_id,
                      ad_name = excluded.ad_name, status = excluded.status,
                      creative_id = excluded.creative_id, title = excluded.title,
                      body = excluded.body, thumbnail_url = excluded.thumbnail_url,
                      object_type = excluded.object_type,
                      instagram_permalink = excluded.instagram_permalink,
                      updated_at = now()
                    """,
                    (a.get("id"), tid, AD_ACCOUNT, a.get("campaign_id"), a.get("adset_id"),
                     a.get("name"), a.get("status"), cre.get("id"), cre.get("title"),
                     cre.get("body"), cre.get("thumbnail_url"), cre.get("object_type"),
                     cre.get("instagram_permalink_url")))
                n_cre += 1

    print(f"OK ad-level {AD_ACCOUNT}: linhas_dia_anuncio={n_ins} criativos={n_cre} janela={DAYS}d")


if __name__ == "__main__":
    main()
