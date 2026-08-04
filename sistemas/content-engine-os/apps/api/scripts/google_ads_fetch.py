#!/usr/bin/env python3
"""google_ads_fetch.py — Busca performance do Google Ads (4 níveis) e emite JSON no stdout.

v2 (detalhe do detalhe): além de campanha, coleta os 3 níveis operacionais que alimentam
o dashboard de decisão — TERMOS DE PESQUISA reais (base da negativação), KEYWORDS
(custo/conversão/QS p/ incluir-pausar) e ANÚNCIOS RSA (headlines/descriptions).

Roda no HOST (lib google-ads + OAuth read-only em /root/.config/ivs-marketing/).
Par: google_ads_load.py (container) — aceita o formato v2 {campaigns, search_terms,
keywords, ads} e também o array puro v1.

  python3 google_ads_fetch.py [--days 14] | docker exec -i content-engine-api \
      python scripts/google_ads_load.py
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path

CONFIG = Path("/root/.config/ivs-marketing/google-ads.yaml")
CUSTOMER_ID = "1070207880"


def _range(days: int) -> tuple[str, str]:
    end = date.today() - timedelta(days=1)
    start = end - timedelta(days=days - 1)
    return start.isoformat(), end.isoformat()


def _money(micros) -> float:
    return round(int(micros or 0) / 1_000_000, 2)


def fetch_all(days: int) -> dict:
    from google.ads.googleads.client import GoogleAdsClient

    client = GoogleAdsClient.load_from_storage(str(CONFIG))
    ga = client.get_service("GoogleAdsService")
    start, end = _range(days)

    def run(query: str):
        for batch in ga.search_stream(customer_id=CUSTOMER_ID, query=query):
            yield from batch.results

    campaigns: list[dict] = []
    for r in run(f"""
        SELECT segments.date, campaign.id, campaign.name, campaign.status,
               campaign.advertising_channel_type, metrics.impressions, metrics.clicks,
               metrics.cost_micros, metrics.conversions, metrics.ctr, metrics.average_cpc
        FROM campaign
        WHERE segments.date BETWEEN '{start}' AND '{end}'
    """):
        campaigns.append({
            "metric_date": r.segments.date, "customer_id": CUSTOMER_ID,
            "campaign_id": str(r.campaign.id), "campaign_name": r.campaign.name,
            "status": r.campaign.status.name, "channel_type": r.campaign.advertising_channel_type.name,
            "impressions": int(r.metrics.impressions), "clicks": int(r.metrics.clicks),
            "spend": _money(r.metrics.cost_micros), "conversions": float(r.metrics.conversions),
            "ctr": float(r.metrics.ctr),
            "cpc": round(int(r.metrics.average_cpc) / 1_000_000, 4) if r.metrics.average_cpc else None,
        })

    search_terms: list[dict] = []
    for r in run(f"""
        SELECT segments.date, campaign.id, campaign.name, ad_group.id, ad_group.name,
               search_term_view.search_term, search_term_view.status,
               metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions
        FROM search_term_view
        WHERE segments.date BETWEEN '{start}' AND '{end}'
    """):
        search_terms.append({
            "metric_date": r.segments.date, "customer_id": CUSTOMER_ID,
            "campaign_id": str(r.campaign.id), "campaign_name": r.campaign.name,
            "ad_group_id": str(r.ad_group.id), "ad_group_name": r.ad_group.name,
            "term": r.search_term_view.search_term, "term_status": r.search_term_view.status.name,
            "impressions": int(r.metrics.impressions), "clicks": int(r.metrics.clicks),
            "spend": _money(r.metrics.cost_micros), "conversions": float(r.metrics.conversions),
        })

    keywords: list[dict] = []
    for r in run(f"""
        SELECT segments.date, campaign.id, campaign.name, ad_group.id, ad_group.name,
               ad_group_criterion.criterion_id, ad_group_criterion.keyword.text,
               ad_group_criterion.keyword.match_type, ad_group_criterion.status,
               metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions
        FROM keyword_view
        WHERE segments.date BETWEEN '{start}' AND '{end}'
    """):
        keywords.append({
            "metric_date": r.segments.date, "customer_id": CUSTOMER_ID,
            "campaign_id": str(r.campaign.id), "campaign_name": r.campaign.name,
            "ad_group_id": str(r.ad_group.id), "ad_group_name": r.ad_group.name,
            "criterion_id": str(r.ad_group_criterion.criterion_id),
            "keyword": r.ad_group_criterion.keyword.text,
            "match_type": r.ad_group_criterion.keyword.match_type.name,
            "kw_status": r.ad_group_criterion.status.name,
            "impressions": int(r.metrics.impressions), "clicks": int(r.metrics.clicks),
            "spend": _money(r.metrics.cost_micros), "conversions": float(r.metrics.conversions),
        })

    ads: list[dict] = []
    for r in run(f"""
        SELECT segments.date, campaign.id, campaign.name, ad_group.id, ad_group.name,
               ad_group_ad.ad.id, ad_group_ad.ad.type, ad_group_ad.status,
               ad_group_ad.ad.responsive_search_ad.headlines,
               ad_group_ad.ad.responsive_search_ad.descriptions,
               ad_group_ad.ad.final_urls,
               metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions
        FROM ad_group_ad
        WHERE segments.date BETWEEN '{start}' AND '{end}'
    """):
        rsa = r.ad_group_ad.ad.responsive_search_ad
        ads.append({
            "metric_date": r.segments.date, "customer_id": CUSTOMER_ID,
            "campaign_id": str(r.campaign.id), "campaign_name": r.campaign.name,
            "ad_group_id": str(r.ad_group.id), "ad_group_name": r.ad_group.name,
            "ad_id": str(r.ad_group_ad.ad.id), "ad_type": r.ad_group_ad.ad.type_.name,
            "ad_status": r.ad_group_ad.status.name,
            "headlines": [h.text for h in rsa.headlines][:15],
            "descriptions": [d.text for d in rsa.descriptions][:6],
            "final_url": (list(r.ad_group_ad.ad.final_urls) or [None])[0],
            "impressions": int(r.metrics.impressions), "clicks": int(r.metrics.clicks),
            "spend": _money(r.metrics.cost_micros), "conversions": float(r.metrics.conversions),
        })

    # snapshot do ESTADO ATUAL (sem janela de datas): o que existe AGORA na conta.
    # É o que permite ao painel saber que uma ação já foi executada — keyword
    # recém-criada ainda sem tráfego e negativas não aparecem nos relatórios diários.
    negativos: list[dict] = []
    for r in run("""
        SELECT campaign.id, campaign.name, campaign_criterion.keyword.text,
               campaign_criterion.keyword.match_type
        FROM campaign_criterion
        WHERE campaign_criterion.type = KEYWORD AND campaign_criterion.negative = TRUE
          AND campaign_criterion.status != REMOVED
    """):
        negativos.append({
            "customer_id": CUSTOMER_ID, "nivel": "campanha",
            "campaign_id": str(r.campaign.id), "campaign_name": r.campaign.name,
            "ad_group_id": None, "ad_group_name": None,
            "keyword": r.campaign_criterion.keyword.text,
            "match_type": r.campaign_criterion.keyword.match_type.name,
        })
    for r in run("""
        SELECT campaign.id, campaign.name, ad_group.id, ad_group.name,
               ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type
        FROM ad_group_criterion
        WHERE ad_group_criterion.type = KEYWORD AND ad_group_criterion.negative = TRUE
          AND ad_group_criterion.status != REMOVED
    """):
        negativos.append({
            "customer_id": CUSTOMER_ID, "nivel": "grupo",
            "campaign_id": str(r.campaign.id), "campaign_name": r.campaign.name,
            "ad_group_id": str(r.ad_group.id), "ad_group_name": r.ad_group.name,
            "keyword": r.ad_group_criterion.keyword.text,
            "match_type": r.ad_group_criterion.keyword.match_type.name,
        })

    # listas COMPARTILHADAS de negativas (Ferramentas → Listas): sem coletar
    # isso, frase negativada em lista nunca sairia da fila do painel
    for r in run("""
        SELECT shared_set.id, shared_set.name,
               shared_criterion.keyword.text, shared_criterion.keyword.match_type
        FROM shared_criterion
        WHERE shared_criterion.type = KEYWORD AND shared_set.status != REMOVED
    """):
        negativos.append({
            "customer_id": CUSTOMER_ID, "nivel": "lista",
            "campaign_id": None, "campaign_name": r.shared_set.name,
            "ad_group_id": None, "ad_group_name": None,
            "keyword": r.shared_criterion.keyword.text,
            "match_type": r.shared_criterion.keyword.match_type.name,
        })

    keywords_atuais: list[dict] = []
    for r in run("""
        SELECT campaign.id, campaign.name, ad_group.id, ad_group.name,
               ad_group_criterion.criterion_id, ad_group_criterion.keyword.text,
               ad_group_criterion.keyword.match_type, ad_group_criterion.status
        FROM ad_group_criterion
        WHERE ad_group_criterion.type = KEYWORD AND ad_group_criterion.negative = FALSE
          AND ad_group_criterion.status != REMOVED
    """):
        keywords_atuais.append({
            "customer_id": CUSTOMER_ID,
            "campaign_id": str(r.campaign.id), "campaign_name": r.campaign.name,
            "ad_group_id": str(r.ad_group.id), "ad_group_name": r.ad_group.name,
            "criterion_id": str(r.ad_group_criterion.criterion_id),
            "keyword": r.ad_group_criterion.keyword.text,
            "match_type": r.ad_group_criterion.keyword.match_type.name,
            "kw_status": r.ad_group_criterion.status.name,
        })

    return {"campaigns": campaigns, "search_terms": search_terms,
            "keywords": keywords, "ads": ads,
            "negativos": negativos, "keywords_atuais": keywords_atuais}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=14)
    args = ap.parse_args()
    if not CONFIG.exists():
        print(json.dumps({"error": f"config ausente: {CONFIG}"}), file=sys.stderr)
        sys.exit(2)
    data = fetch_all(args.days)
    json.dump(data, sys.stdout, ensure_ascii=False)
    print("\nfetch ok: " + ", ".join(f"{k}={len(v)}" for k, v in data.items()), file=sys.stderr)


if __name__ == "__main__":
    main()
