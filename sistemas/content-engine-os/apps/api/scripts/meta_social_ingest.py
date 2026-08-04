"""meta_social_ingest.py — Interações reais do Instagram → fila de Social Selling.

Coleta pela Graph API oficial (mesmo token do meta_insights_ingest):
  - comentários dos últimos posts (username + texto + em qual post = qual dor/tema)
  - DMs recebidas (via Page Access Token derivado do token de sistema)
  - posts em que a Dra foi marcada (mentions/tags)

e faz upsert em social_selling_interactors — a fila que a tela /social-selling lê.
A abordagem continua 100% manual (guardrails da própria tabela); aqui só entra sinal.

Idempotente: os sinais são recomputados do zero a cada corrida (mesma janela → mesma linha);
curadoria manual é preservada (status nunca é tocado; abertura sugerida só preenche se vazia).

Rodar no host:  docker exec --env-file /root/.openclaw/secure/meta_insights.env \
                  content-engine-api python scripts/meta_social_ingest.py
Config por env: META_IG_TOKEN (obrigatório), META_IG_USER_ID, META_PAGE_ID,
                IG_TENANT_SLUG (default demo), META_SS_MEDIA (default 30, posts varridos),
                META_SS_EXCLUDE (handles ignorados, ex.: equipe/família).
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
PAGE_ID = os.environ.get("META_PAGE_ID", "103952482438650")
TENANT_SLUG = os.environ.get("IG_TENANT_SLUG", "demo")
MEDIA_SCAN = int(os.environ.get("META_SS_MEDIA", "30"))
EXCLUDE = {h.strip().lstrip("@").lower() for h in
           os.environ.get("META_SS_EXCLUDE", "dradaniely.freitas,tiarofneves").split(",") if h.strip()}
GRAPH = "https://graph.facebook.com/v23.0"
HANDLE = "@dradaniely.freitas"

# Sinais de dor no texto → estágio de consciência (heurística simples; a curadoria refina)
PAIN_WORDS = ("emagre", "peso", "tireoide", "cortisol", "menopausa", "insônia", "insonia",
              "ansiedade", "não consigo", "nao consigo", "metabolismo", "compulsão", "compulsao",
              "hormôn", "hormon", "barriga", "inchaç", "inchac", "cansaç", "cansac")


def _get(cli: httpx.Client, path: str, token: str, **params) -> dict:
    params["access_token"] = token
    r = cli.get(f"{GRAPH}/{path}", params=params, timeout=40)
    r.raise_for_status()
    return r.json()


def _paged(cli: httpx.Client, path: str, token: str, max_items: int, **params) -> list[dict]:
    params["limit"] = min(max_items, 100)
    out: list[dict] = []
    payload = _get(cli, path, token, **params)
    while True:
        out.extend(payload.get("data", []))
        nxt = (payload.get("paging") or {}).get("next")
        if not nxt or len(out) >= max_items:
            return out[:max_items]
        r = cli.get(nxt, timeout=40)
        r.raise_for_status()
        payload = r.json()


def collect_comments(cli: httpx.Client) -> dict[str, dict]:
    """{handle: {comments: [{post_url, post_caption, text, ts}], ...}} dos últimos posts."""
    people: dict[str, dict] = {}
    medias = _paged(cli, f"{IG_ID}/media", TOKEN, MEDIA_SCAN,
                    fields="id,permalink,caption,timestamp,comments_count")
    for m in medias:
        if not (m.get("comments_count") or 0):
            continue
        comments = _paged(cli, f"{m['id']}/comments", TOKEN, 200,
                          fields="username,text,timestamp,like_count")
        for c in comments:
            user = (c.get("username") or "").lower()
            if not user or user in EXCLUDE:
                continue
            p = people.setdefault(user, {"comments": [], "dms": [], "mentions": []})
            p["comments"].append({
                "post_url": m.get("permalink"),
                "post_caption": (m.get("caption") or "")[:120],
                "text": (c.get("text") or "")[:200],
                "ts": c.get("timestamp"),
            })
    return people


def collect_dms(cli: httpx.Client, people: dict[str, dict]) -> None:
    """DMs recebidas — exige Page Access Token (derivado do token de sistema, não expira)."""
    page_token = _get(cli, PAGE_ID, TOKEN, fields="access_token").get("access_token")
    if not page_token:
        raise RuntimeError("não consegui derivar o Page Access Token")
    convs = _paged(cli, f"{PAGE_ID}/conversations", page_token, 100,
                   platform="instagram",
                   fields="participants,updated_time,messages.limit(10){from,message,created_time}")
    for conv in convs:
        parts = (conv.get("participants") or {}).get("data") or []
        other = next((p for p in parts
                      if (p.get("username") or "").lower() not in EXCLUDE
                      and str(p.get("id")) not in (IG_ID, PAGE_ID)), None)
        if not other or not other.get("username"):
            continue  # sem username não dá para casar com comentários nem abordar — pula
        user = other["username"].lower()
        if user in EXCLUDE:
            continue
        msgs = ((conv.get("messages") or {}).get("data")) or []
        inbound = [m for m in msgs if str((m.get("from") or {}).get("id")) == str(other.get("id"))]
        if not inbound:
            continue
        p = people.setdefault(user, {"comments": [], "dms": [], "mentions": []})
        p["name"] = other.get("name") or p.get("name")
        for m in inbound[:5]:
            p["dms"].append({"text": (m.get("message") or "")[:200], "ts": m.get("created_time")})


def collect_mentions(cli: httpx.Client, people: dict[str, dict]) -> None:
    tags = _paged(cli, f"{IG_ID}/tags", TOKEN, 50, fields="username,caption,timestamp,permalink")
    for t in tags:
        user = (t.get("username") or "").lower()
        if not user or user in EXCLUDE:
            continue
        p = people.setdefault(user, {"comments": [], "dms": [], "mentions": []})
        p["mentions"].append({
            "caption": (t.get("caption") or "")[:120],
            "url": t.get("permalink"),
            "ts": t.get("timestamp"),
        })


def _classify(p: dict) -> tuple[str, str, int, str | None, str]:
    """(interaction_type dominante, estágio, fit_score, last_at, abertura sugerida)"""
    # a API devolve do mais novo p/ o mais antigo; ordena por ts p/ [-1] ser o mais recente
    for k in ("comments", "dms", "mentions"):
        p[k] = sorted(p[k], key=lambda x: x.get("ts") or "")
    n_c, n_d, n_m = len(p["comments"]), len(p["dms"]), len(p["mentions"])
    all_ts = [x.get("ts") for x in p["comments"] + p["dms"] + p["mentions"] if x.get("ts")]
    last_at = max(all_ts) if all_ts else None
    blob = " ".join(x.get("text", "") for x in p["comments"] + p["dms"]).lower()
    has_pain = any(w in blob for w in PAIN_WORDS)

    if n_d:
        kind = "dm_reply"
        stage = "quase_pronto" if has_pain else "consciente_da_solucao"
    elif n_c:
        kind = "comment"
        stage = "consciente_da_dor" if has_pain else "frio"
    else:
        kind = "mention"
        stage = "consciente_da_solucao"

    recent = False
    if last_at:
        try:
            ts = dt.datetime.fromisoformat(last_at.replace("+0000", "+00:00"))
            recent = (dt.datetime.now(dt.timezone.utc) - ts).days <= 7
        except ValueError:
            pass
    score = min(100, n_c * 15 + n_d * 35 + n_m * 25 + (10 if recent else 0) + (15 if has_pain else 0))

    opening = None
    if p["comments"]:
        ref = p["comments"][-1]
        tema = (ref.get("post_caption") or "").split("\n")[0][:60]
        opening = (f"Vi seu comentário no post \"{tema}…\" — obrigada por participar! "
                   "Me conta: esse tema toca algo que você vive hoje?")
    elif p["dms"]:
        opening = "Retomar a conversa da DM com acolhimento, sem pitch: perguntar como ela está hoje."
    elif p["mentions"]:
        opening = "Ela marcou a Dra em um post — agradecer pessoalmente e puxar conversa leve."
    return kind, stage, score, last_at, opening


def main() -> None:
    if not TOKEN:
        raise SystemExit("META_IG_TOKEN ausente (rode com --env-file /root/.openclaw/secure/meta_insights.env)")

    with httpx.Client() as cli:
        people = collect_comments(cli)
        errors: list[str] = []
        dms_ok = True
        for step, fn in (("dms", collect_dms), ("mentions", collect_mentions)):
            try:
                fn(cli, people)
            except Exception as exc:  # comentários seguem valendo mesmo se DM/tags falhar
                errors.append(f"{step}: {exc}")
                if step == "dms":
                    dms_ok = False

    upserted = 0
    with get_conn() as conn:
        with conn.transaction(), conn.cursor() as cur:
            cur.execute("select id from tenants where slug=%s", (TENANT_SLUG,))
            row = cur.fetchone()
            if not row:
                raise SystemExit(f"tenant '{TENANT_SLUG}' não encontrado")
            tid = row["id"]

            for user, p in people.items():
                kind, stage, score, last_at, opening = _classify(p)
                latest_c = p["comments"][-1] if p["comments"] else {}
                signals = {
                    "fonte": "meta_graph",
                    "comentarios": p["comments"][-5:],
                    "dms_recebidas": p["dms"][-3:],
                    "mencoes": p["mentions"][-3:],
                    "totais": {"comentarios": len(p["comments"]), "dms": len(p["dms"]),
                               "mencoes": len(p["mentions"])},
                }
                # se a coleta de DMs falhou nesta corrida, linhas que já eram dm_reply não podem
                # regredir para comment/frio — o sinal mais quente é preservado até a próxima
                # corrida completa (%(dms_ok)s controla o CASE).
                cur.execute(
                    """
                    insert into social_selling_interactors
                      (tenant_id, profile_handle, public_handle, public_name, interaction_type,
                       publication_url, last_interaction_at, interaction_count, observed_signals,
                       consciousness_stage, fit_score, suggested_opening)
                    values (%(tid)s, %(handle)s, %(user)s, %(name)s, %(kind)s, %(url)s, %(last)s,
                            %(count)s, %(signals)s::jsonb, %(stage)s, %(score)s, %(opening)s)
                    on conflict (tenant_id, profile_handle, public_handle) do update set
                      public_name = coalesce(excluded.public_name, social_selling_interactors.public_name),
                      publication_url = coalesce(excluded.publication_url, social_selling_interactors.publication_url),
                      last_interaction_at = greatest(coalesce(social_selling_interactors.last_interaction_at, excluded.last_interaction_at), excluded.last_interaction_at),
                      suggested_opening = coalesce(nullif(social_selling_interactors.suggested_opening, ''), excluded.suggested_opening),
                      interaction_type = case when %(dms_ok)s or social_selling_interactors.interaction_type <> 'dm_reply'
                                              then excluded.interaction_type else social_selling_interactors.interaction_type end,
                      consciousness_stage = case when %(dms_ok)s or social_selling_interactors.interaction_type <> 'dm_reply'
                                                 then excluded.consciousness_stage else social_selling_interactors.consciousness_stage end,
                      fit_score = case when %(dms_ok)s or social_selling_interactors.interaction_type <> 'dm_reply'
                                       then excluded.fit_score else greatest(social_selling_interactors.fit_score, excluded.fit_score) end,
                      interaction_count = case when %(dms_ok)s or social_selling_interactors.interaction_type <> 'dm_reply'
                                               then excluded.interaction_count else greatest(social_selling_interactors.interaction_count, excluded.interaction_count) end,
                      observed_signals = case when %(dms_ok)s or social_selling_interactors.interaction_type <> 'dm_reply'
                                              then excluded.observed_signals else social_selling_interactors.observed_signals end,
                      updated_at = now()
                    """,
                    {"tid": tid, "handle": HANDLE, "user": "@" + user, "name": p.get("name"),
                     "kind": kind, "url": latest_c.get("post_url"), "last": last_at,
                     "count": len(p["comments"]) + len(p["dms"]) + len(p["mentions"]),
                     "signals": json.dumps(signals, ensure_ascii=False), "stage": stage,
                     "score": score, "opening": opening, "dms_ok": dms_ok})
                upserted += 1

    msg = f"OK social-ingest: pessoas={upserted}"
    if errors:
        msg += " | avisos: " + "; ".join(errors)
    print(msg)


if __name__ == "__main__":
    main()
