"""ctwa_load.py — grava os leads CTWA (WhatsApp por anúncio) no Postgres do Content OS.

Lê do stdin o JSON do ctwa_fetch.py (host) e faz upsert idempotente por
(tenant, phone, source_id). Tabela é a ponte lead↔criativo do dashboard de decisão:
custo por lead QUALIFICADO por anúncio = spend do ad (meta_ads_ad_insights_daily)
÷ leads com engajamento (msgs_7d) desta tabela.

Uso: python3 ctwa_fetch.py | docker exec -i content-engine-api python scripts/ctwa_load.py
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, "/app")
from app.db import get_conn  # noqa: E402

TENANT_SLUG = os.environ.get("IG_TENANT_SLUG", "demo")

DDL = """
create table if not exists whatsapp_ctwa_leads (
  id bigserial primary key,
  tenant_id uuid not null,
  phone text not null,
  sender_name text,
  first_ts timestamptz not null,
  source_id text not null,
  ad_title text,
  ad_body text,
  media_type text,
  source_app text,
  source_url text,
  ctwa_clid text,
  first_text text,
  msgs_7d int not null default 0,
  msgs_total int not null default 0,
  last_inbound_ts timestamptz,
  source text not null default 'zapi_spool:ctwa',
  collected_at timestamptz not null default now(),
  unique (tenant_id, phone, source_id)
);
alter table whatsapp_ctwa_leads add column if not exists conversa_amostra text;
"""

DDL_FLUXO = """
create table if not exists whatsapp_fluxo_diario (
  id bigserial primary key,
  tenant_id uuid not null,
  dia date not null,
  contatos_novos int not null default 0,
  msgs_inbound int not null default 0,
  ctwa_leads int not null default 0,
  collected_at timestamptz not null default now(),
  unique (tenant_id, dia)
);
alter table whatsapp_fluxo_diario add column if not exists fonte_anuncio_ig int not null default 0;
alter table whatsapp_fluxo_diario add column if not exists fonte_anuncio_fb int not null default 0;
alter table whatsapp_fluxo_diario add column if not exists fonte_site_google int not null default 0;
alter table whatsapp_fluxo_diario add column if not exists fonte_indicacao int not null default 0;
alter table whatsapp_fluxo_diario add column if not exists fonte_outros int not null default 0;
alter table whatsapp_fluxo_diario add column if not exists contatos_ativos int not null default 0;
"""


def main() -> None:
    data = json.load(sys.stdin)
    leads = data.get("leads") or []
    fluxo = data.get("fluxo_diario") or []
    n = 0
    with get_conn() as conn:
        with conn.transaction(), conn.cursor() as cur:
            cur.execute(DDL)
            cur.execute(DDL_FLUXO)
            cur.execute("select id from tenants where slug=%s", (TENANT_SLUG,))
            row = cur.fetchone()
            if not row:
                raise SystemExit(f"tenant '{TENANT_SLUG}' não encontrado")
            tid = row["id"]
            for L in leads:
                cur.execute(
                    """
                    insert into whatsapp_ctwa_leads
                      (tenant_id, phone, sender_name, first_ts, source_id, ad_title, ad_body,
                       media_type, source_app, source_url, ctwa_clid, first_text,
                       msgs_7d, msgs_total, last_inbound_ts, conversa_amostra)
                    values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    on conflict (tenant_id, phone, source_id) do update set
                      sender_name = excluded.sender_name,
                      msgs_7d = greatest(whatsapp_ctwa_leads.msgs_7d, excluded.msgs_7d),
                      msgs_total = greatest(whatsapp_ctwa_leads.msgs_total, excluded.msgs_total),
                      last_inbound_ts = greatest(whatsapp_ctwa_leads.last_inbound_ts, excluded.last_inbound_ts),
                      conversa_amostra = coalesce(excluded.conversa_amostra, whatsapp_ctwa_leads.conversa_amostra),
                      collected_at = now()
                    """,
                    (tid, L["phone"], L.get("sender_name"), L["ts"], L["source_id"],
                     L.get("ad_title"), L.get("ad_body"), L.get("media_type"),
                     L.get("source_app"), L.get("source_url"), L.get("ctwa_clid"),
                     L.get("first_text"), L.get("msgs_7d", 0), L.get("msgs_total", 0),
                     L.get("last_inbound_ts"), L.get("conversa_amostra")))
                n += 1
            for f in fluxo:
                cur.execute(
                    """
                    insert into whatsapp_fluxo_diario
                      (tenant_id, dia, contatos_novos, msgs_inbound, ctwa_leads,
                       fonte_anuncio_ig, fonte_anuncio_fb, fonte_site_google,
                       fonte_indicacao, fonte_outros, contatos_ativos)
                    values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    on conflict (tenant_id, dia) do update set
                      contatos_ativos = greatest(whatsapp_fluxo_diario.contatos_ativos, excluded.contatos_ativos),
                      contatos_novos = excluded.contatos_novos,
                      msgs_inbound = excluded.msgs_inbound,
                      ctwa_leads = excluded.ctwa_leads,
                      fonte_anuncio_ig = excluded.fonte_anuncio_ig,
                      fonte_anuncio_fb = excluded.fonte_anuncio_fb,
                      fonte_site_google = excluded.fonte_site_google,
                      fonte_indicacao = excluded.fonte_indicacao,
                      fonte_outros = excluded.fonte_outros,
                      collected_at = now()
                    """,
                    (tid, f["dia"], f.get("contatos_novos", 0), f.get("msgs_inbound", 0),
                     f.get("ctwa_leads", 0), f.get("fonte_anuncio_ig", 0),
                     f.get("fonte_anuncio_fb", 0), f.get("fonte_site_google", 0),
                     f.get("fonte_indicacao", 0), f.get("fonte_outros", 0),
                     f.get("contatos_ativos", 0)))
    print(f"OK ctwa-load: leads_upsert={n} fluxo_dias={len(fluxo)} (arquivos_spool={data.get('arquivos')})")


if __name__ == "__main__":
    main()
