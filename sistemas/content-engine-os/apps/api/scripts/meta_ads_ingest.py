"""meta_ads_ingest.py — Performance do Meta Ads (campanhas) no Content Engine OS.

Usa a Graph API oficial (mesmo token do meta_insights_ingest, escopo ads_read) e grava,
idempotente por (dia × campanha), os últimos N dias em meta_ads_insights_daily — que o
endpoint /ads/overview e a tela Ads & canais pagos leem. Reprocessa a janela inteira a cada
corrida porque a Meta consolida gasto/atribuição com atraso de até 72h.

Rodar no host:  docker exec --env-file /root/.openclaw/secure/meta_insights.env \
                  content-engine-api python scripts/meta_ads_ingest.py
Config por env: META_IG_TOKEN (obrigatório), META_AD_ACCOUNT (default conta da clínica),
                IG_TENANT_SLUG (default demo), META_ADS_DAYS (default 14).
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
DAYS = int(os.environ.get("META_ADS_DAYS", "14"))
GRAPH = "https://graph.facebook.com/v23.0"
SOURCE = "meta_graph:ads:v23.0"
BRT = dt.timezone(dt.timedelta(hours=-3))

FIELDS = ("campaign_id,campaign_name,spend,impressions,reach,clicks,ctr,cpc,cpm,frequency,"
          "actions,cost_per_action_type")

DDL = """
create table if not exists meta_ads_insights_daily (
  id bigserial primary key,
  tenant_id uuid not null,
  metric_date date not null,
  ad_account_id text not null,
  campaign_id text not null,
  campaign_name text,
  spend numeric(12,2),
  impressions bigint,
  reach bigint,
  clicks bigint,
  link_clicks bigint,
  messaging_starts bigint,
  leads bigint,
  ctr numeric(8,4),
  cpc numeric(10,4),
  cpm numeric(10,4),
  frequency numeric(8,4),
  actions jsonb not null default '[]'::jsonb,
  source text not null,
  collected_at timestamptz not null default now(),
  unique (tenant_id, ad_account_id, metric_date, campaign_id)
);
"""

# action_types da Meta que interessam ao funil da clínica
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
    """'lead' é o agregado oficial e JÁ CONTÉM os grupos — somar tudo inflaria 2-3x.
    Usa 'lead' quando presente; só cai para os agrupados na ausência dele."""
    for a in actions or []:
        if a.get("action_type") == "lead":
            try:
                return int(float(a.get("value") or 0))
            except (TypeError, ValueError):
                return 0
    return _action(actions, ACT_LEAD_GROUPED)


def fetch_insights(cli: httpx.Client) -> list[dict]:
    until = dt.datetime.now(BRT).date() - dt.timedelta(days=1)
    since = until - dt.timedelta(days=DAYS - 1)
    params = {
        "level": "campaign",
        "fields": FIELDS,
        "time_increment": 1,
        "time_range": json.dumps({"since": since.isoformat(), "until": until.isoformat()}),
        "limit": 500,
        "access_token": TOKEN,
    }
    rows: list[dict] = []
    url, first, pages = f"{GRAPH}/{AD_ACCOUNT}/insights", True, 0
    while url:
        pages += 1
        if pages > 50:  # glitches de paginação da Meta não podem pendurar o cron
            raise RuntimeError("paginação do insights passou de 50 páginas — abortando")
        r = cli.get(url, params=params if first else None, timeout=60)
        r.raise_for_status()
        payload = r.json()
        data = payload.get("data", [])
        if not data:
            break
        rows.extend(data)
        url, first = (payload.get("paging") or {}).get("next"), False
    return rows


def main() -> None:
    if not TOKEN:
        raise SystemExit("META_IG_TOKEN ausente (rode com --env-file /root/.openclaw/secure/meta_insights.env)")

    with httpx.Client() as cli:
        rows = fetch_insights(cli)

    n = 0
    with get_conn() as conn:
        with conn.transaction(), conn.cursor() as cur:
            cur.execute(DDL)
            cur.execute("select id from tenants where slug=%s", (TENANT_SLUG,))
            row = cur.fetchone()
            if not row:
                raise SystemExit(f"tenant '{TENANT_SLUG}' não encontrado")
            tid = row["id"]

            for r in rows:
                actions = r.get("actions") or []
                cur.execute(
                    """
                    insert into meta_ads_insights_daily
                      (tenant_id, metric_date, ad_account_id, campaign_id, campaign_name,
                       spend, impressions, reach, clicks, link_clicks, messaging_starts, leads,
                       ctr, cpc, cpm, frequency, actions, source)
                    values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s)
                    on conflict (tenant_id, ad_account_id, metric_date, campaign_id) do update set
                      campaign_name = excluded.campaign_name,
                      spend = excluded.spend, impressions = excluded.impressions,
                      reach = excluded.reach, clicks = excluded.clicks,
                      link_clicks = excluded.link_clicks,
                      messaging_starts = excluded.messaging_starts, leads = excluded.leads,
                      ctr = excluded.ctr, cpc = excluded.cpc, cpm = excluded.cpm,
                      frequency = excluded.frequency, actions = excluded.actions,
                      collected_at = now()
                    """,
                    (tid, r.get("date_start"), AD_ACCOUNT, r.get("campaign_id"),
                     r.get("campaign_name"), r.get("spend"), r.get("impressions"),
                     r.get("reach"), r.get("clicks"),
                     _action(actions, ACT_LINK), _action(actions, ACT_MSG), _leads(actions),
                     r.get("ctr"), r.get("cpc"), r.get("cpm"), r.get("frequency"),
                     json.dumps(actions), SOURCE))
                n += 1

    print(f"OK ads-ingest {AD_ACCOUNT}: linhas_dia_campanha={n} janela={DAYS}d")


if __name__ == "__main__":
    main()
