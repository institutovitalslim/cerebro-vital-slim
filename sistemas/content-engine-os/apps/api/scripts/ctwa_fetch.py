#!/usr/bin/env python3
"""ctwa_fetch.py — extrai do spool Z-API os leads vindos de anúncio (CTWA) + engajamento.

Roda no HOST (o spool não é montado no container) e emite JSON no stdout para o
ctwa_load.py (container) gravar no Postgres — mesmo padrão do pipeline Google Ads.

Cada mensagem com payload.externalAdReply é um toque de anúncio: telefone, nome, quando,
e QUAL anúncio (sourceId, título, corpo, formato, app). O engajamento pós-clique (proxy de
qualificação) vem do próprio spool: nº de mensagens inbound do mesmo telefone nos 7 dias
seguintes ao primeiro toque, e a última atividade.

Uso: python3 ctwa_fetch.py [--days N]   (default: spool inteiro)
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import sys

SPOOL_GLOB = "/root/.openclaw/workspace/ops/zapi_bridge/audit/zapi_webhook_events_*.jsonl"


def _find_ad(obj):
    if isinstance(obj, dict):
        if "externalAdReply" in obj and isinstance(obj["externalAdReply"], dict):
            return obj["externalAdReply"]
        for v in obj.values():
            r = _find_ad(v)
            if r:
                return r
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=0, help="0 = spool inteiro")
    args = ap.parse_args()

    files = sorted(glob.glob(SPOOL_GLOB))
    if args.days:
        cutoff = (dt.date.today() - dt.timedelta(days=args.days)).isoformat()
        files = [f for f in files if f.split("_")[-1].replace(".jsonl", "") >= cutoff]

    inbound_por_fone: dict[str, list[str]] = {}          # phone -> [ts_utc...]
    textos_por_fone: dict[str, list[tuple]] = {}         # phone -> [(ts, texto)...]
    toques: list[dict] = []                              # eventos com anúncio

    def fone_valido(p: str) -> bool:
        """Só telefone BR real (55 + DDD + número). Exclui LIDs/broadcast/ids de sistema."""
        return p.isdigit() and p.startswith("55") and 12 <= len(p) <= 13

    for f in files:
        for line in open(f, encoding="utf-8", errors="ignore"):
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            if str(ev.get("from_me")) == "True" or str(ev.get("is_group")) == "True":
                continue
            phone, ts = ev.get("phone"), ev.get("received_at_utc")
            if not phone or not ts:
                continue
            inbound_por_fone.setdefault(phone, []).append(ts)
            txt = (ev.get("text") or "").strip()
            if txt:
                textos_por_fone.setdefault(phone, []).append((ts, txt[:280]))
            ad = _find_ad(ev.get("payload") or {})
            if ad and str(ad.get("sourceType", "ad")) == "ad":
                toques.append({
                    "phone": phone,
                    "sender_name": ev.get("sender_name"),
                    "ts": ts,
                    "source_id": str(ad.get("sourceId") or ""),
                    "ad_title": ad.get("title"),
                    "ad_body": (ad.get("body") or "")[:600],
                    "media_type": ad.get("mediaType"),
                    "source_app": ad.get("sourceApp"),
                    "source_url": ad.get("sourceUrl"),
                    "ctwa_clid": ad.get("ctwaClid"),
                    "first_text": (ev.get("text") or "")[:300],
                })

    # 1 lead = (phone, source_id) no primeiro toque; engajamento a partir do 1º toque
    leads: dict[tuple, dict] = {}
    for t in sorted(toques, key=lambda x: x["ts"]):
        key = (t["phone"], t["source_id"])
        if key not in leads:
            leads[key] = t
    out = []
    for (phone, _sid), lead in leads.items():
        ts0 = dt.datetime.fromisoformat(lead["ts"].replace("Z", "+00:00"))
        janela = ts0 + dt.timedelta(days=7)
        msgs = [m for m in inbound_por_fone.get(phone, [])]
        msgs_dt = []
        for m in msgs:
            try:
                msgs_dt.append(dt.datetime.fromisoformat(m.replace("Z", "+00:00")))
            except ValueError:
                pass
        # amostra da conversa: até 6 mensagens inbound a partir do toque do anúncio
        conversa = [txt for (t, txt) in sorted(textos_por_fone.get(phone, []))
                    if t >= lead["ts"]][:6]
        out.append({**lead,
                    "msgs_7d": sum(1 for m in msgs_dt if ts0 <= m <= janela),
                    "msgs_total": len(msgs_dt),
                    "conversa_amostra": " | ".join(conversa)[:900],
                    "last_inbound_ts": max(msgs_dt).isoformat() if msgs_dt else lead["ts"]})

    # fluxo diário de conversas: contatos ATIVOS no dia (métrica do relatório diário),
    # contatos NOVOS (1ª vez no histórico), mensagens, origem e anúncio
    primeiro_contato: dict[str, str] = {}
    msgs_por_dia: dict[str, int] = {}
    ativos_por_dia: dict[str, set] = {}
    for phone, tss in inbound_por_fone.items():
        valido = fone_valido(phone)
        for ts in tss:
            dia = ts[:10]
            msgs_por_dia[dia] = msgs_por_dia.get(dia, 0) + 1
            if valido:
                ativos_por_dia.setdefault(dia, set()).add(phone)
        if valido:
            primeiro_contato[phone] = min(tss)

    # classificação de fonte do novo contato:
    #   anúncio (CTWA, com app IG/FB) > site/Google (fala em site/página/google) >
    #   indicação (indicou/recomendou) > outros (orgânico/desconhecido)
    fone_ctwa_app: dict[str, str] = {}
    for lead in leads.values():
        app = (lead.get("source_app") or "").lower()
        fone_ctwa_app.setdefault(lead["phone"], "facebook" if "face" in app else "instagram")

    def classifica(phone: str) -> str:
        if phone in fone_ctwa_app:
            return f"anuncio_{'ig' if fone_ctwa_app[phone] == 'instagram' else 'fb'}"
        textos = sorted(textos_por_fone.get(phone, []))
        primeira = (textos[0][1] if textos else "").lower()
        if any(w in primeira for w in ("pelo site", "no site", "do site", "pela página",
                                       "pela pagina", "google", "pesquisei", "site de vocês")):
            return "site_google"
        if any(w in primeira for w in ("indica", "recomend", "me falou de voc", "me passou o contato")):
            return "indicacao"
        return "outros"

    novos_por_dia: dict[str, dict] = {}
    for phone, ts in primeiro_contato.items():
        dia = ts[:10]
        agg = novos_por_dia.setdefault(dia, {"total": 0, "anuncio_ig": 0, "anuncio_fb": 0,
                                             "site_google": 0, "indicacao": 0, "outros": 0})
        agg["total"] += 1
        agg[classifica(phone)] += 1

    ctwa_por_dia: dict[str, int] = {}
    for lead in leads.values():
        dia = lead["ts"][:10]
        ctwa_por_dia[dia] = ctwa_por_dia.get(dia, 0) + 1

    fluxo = []
    for d in sorted(set(novos_por_dia) | set(msgs_por_dia) | set(ctwa_por_dia)):
        n = novos_por_dia.get(d, {})
        fluxo.append({"dia": d,
                      "contatos_ativos": len(ativos_por_dia.get(d, set())),
                      "contatos_novos": n.get("total", 0),
                      "msgs_inbound": msgs_por_dia.get(d, 0),
                      "ctwa_leads": ctwa_por_dia.get(d, 0),
                      "fonte_anuncio_ig": n.get("anuncio_ig", 0),
                      "fonte_anuncio_fb": n.get("anuncio_fb", 0),
                      "fonte_site_google": n.get("site_google", 0),
                      "fonte_indicacao": n.get("indicacao", 0),
                      "fonte_outros": n.get("outros", 0)})

    json.dump({"leads": out, "fluxo_diario": fluxo, "arquivos": len(files)},
              sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    main()
