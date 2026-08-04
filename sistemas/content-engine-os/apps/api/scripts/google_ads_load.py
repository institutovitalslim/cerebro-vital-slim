"""google_ads_load.py — Carrega no Content OS o JSON do google_ads_fetch.py (host).

v2: aceita o formato novo {campaigns, search_terms, keywords, ads} e mantém compat com o
array puro v1 (só campanhas). Upserts idempotentes:
  google_ads_insights_daily        (dia × campanha)   — como sempre
  google_ads_search_terms_daily    (dia × campanha × grupo × termo)  ← base da NEGATIVAÇÃO
  google_ads_keywords_daily        (dia × grupo × criterion)          ← incluir/pausar kw
  google_ads_ads_daily             (dia × anúncio RSA)                ← análise de anúncio
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, "/app")
from app.db import get_conn  # noqa: E402

TENANT_SLUG = os.environ.get("IG_TENANT_SLUG", "demo")
SOURCE = "google_ads_api"

DDL_CAMPAIGNS = """
create table if not exists google_ads_insights_daily (
  id bigserial primary key,
  tenant_id uuid not null,
  metric_date date not null,
  customer_id text not null,
  campaign_id text not null,
  campaign_name text,
  campaign_status text,
  channel_type text,
  spend numeric(12,2),
  impressions bigint,
  clicks bigint,
  conversions numeric(10,2),
  ctr numeric(8,4),
  cpc numeric(10,4),
  source text not null,
  collected_at timestamptz not null default now(),
  unique (tenant_id, customer_id, metric_date, campaign_id)
);
"""

DDL_TERMS = """
create table if not exists google_ads_search_terms_daily (
  id bigserial primary key,
  tenant_id uuid not null,
  metric_date date not null,
  customer_id text not null,
  campaign_id text not null,
  campaign_name text,
  ad_group_id text not null,
  ad_group_name text,
  term text not null,
  term_status text,
  impressions bigint,
  clicks bigint,
  spend numeric(12,2),
  conversions numeric(10,2),
  source text not null,
  collected_at timestamptz not null default now(),
  unique (tenant_id, customer_id, metric_date, campaign_id, ad_group_id, term)
);
"""

DDL_KEYWORDS = """
create table if not exists google_ads_keywords_daily (
  id bigserial primary key,
  tenant_id uuid not null,
  metric_date date not null,
  customer_id text not null,
  campaign_id text not null,
  campaign_name text,
  ad_group_id text not null,
  ad_group_name text,
  criterion_id text not null,
  keyword text,
  match_type text,
  kw_status text,
  impressions bigint,
  clicks bigint,
  spend numeric(12,2),
  conversions numeric(10,2),
  source text not null,
  collected_at timestamptz not null default now(),
  unique (tenant_id, customer_id, metric_date, ad_group_id, criterion_id)
);
"""

DDL_NEGATIVOS = """
create table if not exists google_ads_negativos (
  id bigserial primary key,
  tenant_id uuid not null,
  customer_id text not null,
  nivel text not null,
  campaign_id text,
  campaign_name text,
  ad_group_id text,
  ad_group_name text,
  keyword text not null,
  match_type text,
  collected_at timestamptz not null default now()
);
"""

DDL_KW_ATUAIS = """
create table if not exists google_ads_keywords_atuais (
  id bigserial primary key,
  tenant_id uuid not null,
  customer_id text not null,
  campaign_id text,
  campaign_name text,
  ad_group_id text,
  ad_group_name text,
  criterion_id text,
  keyword text not null,
  match_type text,
  kw_status text,
  collected_at timestamptz not null default now()
);
"""

DDL_ADS = """
create table if not exists google_ads_ads_daily (
  id bigserial primary key,
  tenant_id uuid not null,
  metric_date date not null,
  customer_id text not null,
  campaign_id text not null,
  campaign_name text,
  ad_group_id text not null,
  ad_group_name text,
  ad_id text not null,
  ad_type text,
  ad_status text,
  headlines jsonb not null default '[]'::jsonb,
  descriptions jsonb not null default '[]'::jsonb,
  final_url text,
  impressions bigint,
  clicks bigint,
  spend numeric(12,2),
  conversions numeric(10,2),
  source text not null,
  collected_at timestamptz not null default now(),
  unique (tenant_id, customer_id, metric_date, ad_id)
);
"""


def main() -> None:
    raw = sys.stdin.read().strip()
    if not raw:
        raise SystemExit("stdin vazio — rode via google_ads_fetch.py | docker exec -i ...")
    data = json.loads(raw)
    if isinstance(data, dict) and data.get("error"):
        raise SystemExit(f"fetch reportou erro: {data['error']}")
    if isinstance(data, list):  # compat v1
        data = {"campaigns": data, "search_terms": [], "keywords": [], "ads": []}

    counts = {}
    with get_conn() as conn:
        with conn.transaction(), conn.cursor() as cur:
            for ddl in (DDL_CAMPAIGNS, DDL_TERMS, DDL_KEYWORDS, DDL_ADS,
                        DDL_NEGATIVOS, DDL_KW_ATUAIS):
                cur.execute(ddl)
            cur.execute("select id from tenants where slug=%s", (TENANT_SLUG,))
            row = cur.fetchone()
            if not row:
                raise SystemExit(f"tenant '{TENANT_SLUG}' não encontrado")
            tid = row["id"]

            for r in data.get("campaigns") or []:
                cur.execute(
                    """
                    insert into google_ads_insights_daily
                      (tenant_id, metric_date, customer_id, campaign_id, campaign_name,
                       campaign_status, channel_type, spend, impressions, clicks,
                       conversions, ctr, cpc, source)
                    values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    on conflict (tenant_id, customer_id, metric_date, campaign_id) do update set
                      campaign_name = excluded.campaign_name,
                      campaign_status = excluded.campaign_status,
                      channel_type = excluded.channel_type,
                      spend = excluded.spend, impressions = excluded.impressions,
                      clicks = excluded.clicks, conversions = excluded.conversions,
                      ctr = excluded.ctr, cpc = excluded.cpc, collected_at = now()
                    """,
                    (tid, r.get("metric_date"), r.get("customer_id"), r.get("campaign_id"),
                     r.get("campaign_name"), r.get("status"), r.get("channel_type"),
                     r.get("spend"), r.get("impressions"), r.get("clicks"),
                     r.get("conversions"), r.get("ctr"), r.get("cpc"), SOURCE))
            counts["campaigns"] = len(data.get("campaigns") or [])

            for r in data.get("search_terms") or []:
                cur.execute(
                    """
                    insert into google_ads_search_terms_daily
                      (tenant_id, metric_date, customer_id, campaign_id, campaign_name,
                       ad_group_id, ad_group_name, term, term_status,
                       impressions, clicks, spend, conversions, source)
                    values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    on conflict (tenant_id, customer_id, metric_date, campaign_id, ad_group_id, term)
                    do update set
                      campaign_name = excluded.campaign_name,
                      ad_group_name = excluded.ad_group_name,
                      term_status = excluded.term_status,
                      impressions = excluded.impressions, clicks = excluded.clicks,
                      spend = excluded.spend, conversions = excluded.conversions,
                      collected_at = now()
                    """,
                    (tid, r.get("metric_date"), r.get("customer_id"), r.get("campaign_id"),
                     r.get("campaign_name"), r.get("ad_group_id"), r.get("ad_group_name"),
                     r.get("term"), r.get("term_status"), r.get("impressions"),
                     r.get("clicks"), r.get("spend"), r.get("conversions"), SOURCE))
            counts["search_terms"] = len(data.get("search_terms") or [])

            for r in data.get("keywords") or []:
                cur.execute(
                    """
                    insert into google_ads_keywords_daily
                      (tenant_id, metric_date, customer_id, campaign_id, campaign_name,
                       ad_group_id, ad_group_name, criterion_id, keyword, match_type, kw_status,
                       impressions, clicks, spend, conversions, source)
                    values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    on conflict (tenant_id, customer_id, metric_date, ad_group_id, criterion_id)
                    do update set
                      campaign_name = excluded.campaign_name,
                      ad_group_name = excluded.ad_group_name,
                      keyword = excluded.keyword, match_type = excluded.match_type,
                      kw_status = excluded.kw_status,
                      impressions = excluded.impressions, clicks = excluded.clicks,
                      spend = excluded.spend, conversions = excluded.conversions,
                      collected_at = now()
                    """,
                    (tid, r.get("metric_date"), r.get("customer_id"), r.get("campaign_id"),
                     r.get("campaign_name"), r.get("ad_group_id"), r.get("ad_group_name"),
                     r.get("criterion_id"), r.get("keyword"), r.get("match_type"),
                     r.get("kw_status"), r.get("impressions"), r.get("clicks"),
                     r.get("spend"), r.get("conversions"), SOURCE))
            counts["keywords"] = len(data.get("keywords") or [])

            for r in data.get("ads") or []:
                cur.execute(
                    """
                    insert into google_ads_ads_daily
                      (tenant_id, metric_date, customer_id, campaign_id, campaign_name,
                       ad_group_id, ad_group_name, ad_id, ad_type, ad_status,
                       headlines, descriptions, final_url,
                       impressions, clicks, spend, conversions, source)
                    values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s::jsonb,%s,%s,%s,%s,%s,%s)
                    on conflict (tenant_id, customer_id, metric_date, ad_id) do update set
                      campaign_name = excluded.campaign_name,
                      ad_group_name = excluded.ad_group_name,
                      ad_type = excluded.ad_type, ad_status = excluded.ad_status,
                      headlines = excluded.headlines, descriptions = excluded.descriptions,
                      final_url = excluded.final_url,
                      impressions = excluded.impressions, clicks = excluded.clicks,
                      spend = excluded.spend, conversions = excluded.conversions,
                      collected_at = now()
                    """,
                    (tid, r.get("metric_date"), r.get("customer_id"), r.get("campaign_id"),
                     r.get("campaign_name"), r.get("ad_group_id"), r.get("ad_group_name"),
                     r.get("ad_id"), r.get("ad_type"), r.get("ad_status"),
                     json.dumps(r.get("headlines") or []), json.dumps(r.get("descriptions") or []),
                     r.get("final_url"), r.get("impressions"), r.get("clicks"),
                     r.get("spend"), r.get("conversions"), SOURCE))
            counts["ads"] = len(data.get("ads") or [])

            # snapshots do estado atual: substitui tudo a cada corrida (retrato AGORA)
            if "negativos" in data:
                cur.execute("delete from google_ads_negativos where tenant_id=%s", (tid,))
                for r in data.get("negativos") or []:
                    cur.execute(
                        """
                        insert into google_ads_negativos
                          (tenant_id, customer_id, nivel, campaign_id, campaign_name,
                           ad_group_id, ad_group_name, keyword, match_type)
                        values (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        """,
                        (tid, r.get("customer_id"), r.get("nivel"), r.get("campaign_id"),
                         r.get("campaign_name"), r.get("ad_group_id"), r.get("ad_group_name"),
                         r.get("keyword"), r.get("match_type")))
                counts["negativos"] = len(data.get("negativos") or [])
            if "keywords_atuais" in data:
                cur.execute("delete from google_ads_keywords_atuais where tenant_id=%s", (tid,))
                for r in data.get("keywords_atuais") or []:
                    cur.execute(
                        """
                        insert into google_ads_keywords_atuais
                          (tenant_id, customer_id, campaign_id, campaign_name, ad_group_id,
                           ad_group_name, criterion_id, keyword, match_type, kw_status)
                        values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        """,
                        (tid, r.get("customer_id"), r.get("campaign_id"), r.get("campaign_name"),
                         r.get("ad_group_id"), r.get("ad_group_name"), r.get("criterion_id"),
                         r.get("keyword"), r.get("match_type"), r.get("kw_status")))
                counts["keywords_atuais"] = len(data.get("keywords_atuais") or [])

    print("OK google-ads-load v2: " + " ".join(f"{k}={v}" for k, v in counts.items()))


if __name__ == "__main__":
    main()
