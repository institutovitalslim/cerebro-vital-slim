from __future__ import annotations

import json
import os
import re
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any

HOST = "instagram-scraper-stable-api.p.rapidapi.com"
DEFAULT_TAGS = {
    "menopausa": ["menopausa", "climaterio", "fogachos", "menopausaemagrecimento", "terapiahormonal", "saudedamulher", "mulheres40mais", "reposicaohormonal"],
}


def theme_tags(topic: str, tags_csv: str | None = None, max_tags: int = 12) -> list[str]:
    raw = [x.strip().lstrip("#") for x in (tags_csv or "").split(",") if x.strip()]
    if not raw:
        raw = DEFAULT_TAGS.get(topic.lower(), [topic.lower()])
    seen: set[str] = set()
    out: list[str] = []
    for tag in raw:
        clean = re.sub(r"[^a-zA-Z0-9áàâãéêíóôõúçÁÀÂÃÉÊÍÓÔÕÚÇ_]+", "", tag).lower()
        if clean and clean not in seen:
            seen.add(clean)
            out.append(clean)
    return out[:max_tags]


def caption_of(node: dict[str, Any]) -> str:
    edges = ((node.get("edge_media_to_caption") or {}).get("edges") or [])
    if edges:
        return ((edges[0].get("node") or {}).get("text") or "")[:2500]
    cap = node.get("caption")
    if isinstance(cap, dict):
        return (cap.get("text") or "")[:2500]
    if isinstance(cap, str):
        return cap[:2500]
    return ""


def parse_hashtag_posts(topic: str, tag: str, data: dict[str, Any], limit: int = 8) -> list[dict[str, Any]]:
    edges = (((data or {}).get("posts") or {}).get("edges") or [])
    out: list[dict[str, Any]] = []
    for edge in edges[:limit]:
        node = (edge or {}).get("node") or {}
        shortcode = node.get("shortcode") or node.get("code")
        if not shortcode:
            continue
        caption = caption_of(node)
        caption_l = caption.lower()
        topic_l = topic.lower()
        related_terms = {topic_l, "climaterio", "fogacho", "fogachos", "terapia hormonal", "menopausaemagrecimento"}
        if not any(term in caption_l for term in related_terms):
            continue
        comments = ((node.get("edge_media_to_comment") or {}).get("count") or node.get("comment_count") or 0)
        likes = ((node.get("edge_liked_by") or {}).get("count") or node.get("like_count") or 0)
        is_video = bool(node.get("is_video") or node.get("video_url"))
        out.append({
            "topic": topic,
            "hashtag": tag,
            "shortcode": shortcode,
            "url": f"https://www.instagram.com/reel/{shortcode}/" if is_video else f"https://www.instagram.com/p/{shortcode}/",
            "format": "reel" if is_video else "post",
            "caption": caption,
            "likes": int(likes or 0),
            "comments": int(comments or 0),
            "score": int(likes or 0) + 5 * int(comments or 0),
            "is_video": is_video,
            "taken_at": node.get("taken_at_timestamp") or node.get("taken_at"),
        })
    return out


def choose_content_format(caption: str) -> str:
    text = (caption or "").lower()
    if any(term in text for term in ["não é", "nao e", "mito", "frescura", "normal"]):
        return "sinal_escondido"
    if any(term in text for term in ["antes de", "posso fazer", "terapia hormonal", "reposi"]):
        return "antes_da_decisao"
    if any(term in text for term in ["erro", "não faça", "nao faca"]):
        return "erro_comum"
    if any(term in text for term in ["checklist", "sinais", "sintomas"]):
        return "checklist_rapido"
    return "mini_aula_visual"


def compact(text: str, limit: int = 500) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip()[:limit]


def build_theme_ingest_payload(item: dict[str, Any], topic: str = "menopausa") -> dict[str, Any]:
    caption = item.get("caption") or ""
    shortcode = item.get("shortcode") or ""
    return {
        "tenant_slug": "demo",
        "content_format": choose_content_format(caption),
        "source_type": "rapidapi_instagram_theme_search",
        "source_handle_or_url": f"theme_search:{topic}:{item.get('hashtag')}",
        "external_id": f"instagram:{shortcode}",
        "content_url": item.get("url"),
        "transcript_summary": compact(caption, 520) or f"Conteúdo público sobre {topic}; caption ausente no payload.",
        "hook_summary": compact(caption.split("\n")[0] if caption else f"Referência pública sobre {topic}", 180),
        "why_this_example_works": "Referência real usada apenas para abstrair mecanismo, hook e retenção; não copiar texto, edição, legenda ou claim clínico.",
        "retention_mechanism": "theme_search_public_signal",
        "compliance_risk": "review_required",
        "ivs_applicability_score": max(40, min(95, 65 + int(item.get("score") or 0) // 20)),
        "winner_candidate_type": "pending",
        "metrics": {"likes": item.get("likes") or 0, "comments": item.get("comments") or 0, "score": item.get("score") or 0},
        "raw_payload_summary": json.dumps({"hashtag": item.get("hashtag"), "format": item.get("format"), "is_video": item.get("is_video")}, ensure_ascii=False),
    }


def rapidapi_key() -> str:
    key = os.environ.get("RAPIDAPI_KEY")
    if not key:
        raise RuntimeError("RAPIDAPI_KEY ausente no container da API")
    return key


def fetch_hashtag(tag: str, timeout: int = 45) -> dict[str, Any]:
    url = f"https://{HOST}/search_hashtag.php?hashtag=" + urllib.parse.quote(tag)
    req = urllib.request.Request(url, headers={
        "x-rapidapi-host": HOST,
        "x-rapidapi-key": rapidapi_key(),
        "User-Agent": "IVS-content-os-motion-phase4/1.0",
        "Content-Type": "application/json",
    })
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read())


def _metric_score(example: dict[str, Any]) -> int:
    meta = example.get("metadata") or {}
    if isinstance(meta, str):
        try:
            meta = json.loads(meta)
        except Exception:
            meta = {}
    raw = meta.get("raw_metrics") or {}
    return int(raw.get("score") or raw.get("likes") or 0)


def build_winner_outputs(example: dict[str, Any], winner_type: str, topic: str) -> dict[str, Any]:
    hook = compact(example.get("hook_summary") or f"Referência sobre {topic}", 140)
    safe_topic = topic.strip() or "tema clínico"
    return {
        "hooks_adaptados": [
            f"{safe_topic.capitalize()} não precisa ser tratada como sentença: quais sinais merecem avaliação?",
            f"O que muda no corpo na {safe_topic} — e por que olhar só para peso confunde?",
            f"Antes de aceitar que é 'normal da idade', vale investigar este padrão com avaliação médica.",
        ],
        "roteiro_reel": {
            "hook": hook,
            "estrutura": ["abrir loop sem promessa", "mostrar mecanismo de forma visual", "separar sintoma de diagnóstico", "fechar com convite para avaliação individual"],
            "cta": "Se isso faz sentido para você, procure avaliação médica individualizada.",
        },
        "stories": ["Enquete: você sente que seu corpo mudou depois dos 40?", "Caixa: qual sintoma mais atrapalha sua rotina?", "Aviso: conteúdo educativo, não substitui consulta."],
        "angulo_anuncio": f"Conteúdo educativo sobre {safe_topic} para mulheres que querem entender sinais do corpo sem promessa de resultado.",
        "hipotese_metrica": "Medir retenção nos 3 primeiros segundos, salvamentos e cliques qualificados para avaliação.",
        "compliance_gate": "review_required: revisar claims, evitar prescrição/diagnóstico público e manter disclaimer educativo.",
        "source_guardrail": "Usar somente o mecanismo abstrato da referência; não copiar texto, edição, legenda, voz ou claim clínico.",
    }


def select_theme_winners(examples: list[dict[str, Any]], topic: str) -> list[dict[str, Any]]:
    if not examples:
        return []
    attention = max(examples, key=lambda x: (_metric_score(x), len(x.get("hook_summary") or "")))
    conversion = max(examples, key=lambda x: (1 if x.get("content_format") in {"antes_da_decisao", "erro_comum", "sinal_escondido"} else 0, _metric_score(x)))
    ivs_fit = max(examples, key=lambda x: (int(x.get("ivs_applicability_score") or 0), -1 if str(x.get("compliance_risk") or "").startswith("high") else 0))
    packs = [("attention", attention, "melhor sinal de atenção/retenção"), ("conversion", conversion, "melhor potencial de quebra de objeção"), ("ivs_fit", ivs_fit, "maior aderência IVS com revisão clínica")]
    winners = []
    for winner_type, example, rationale in packs:
        winners.append({
            "winner_type": winner_type,
            "external_id": example.get("external_id"),
            "content_format": example.get("content_format"),
            "source_url": example.get("content_url"),
            "hook_summary": example.get("hook_summary"),
            "rationale": rationale,
            "selected_for_generation": False,
            "outputs": build_winner_outputs(example, winner_type, topic),
        })
    return winners


def collect_theme_items(topic: str, tags_csv: str | None = None, posts_per_tag: int = 6, limit: int = 8) -> dict[str, Any]:
    tags = theme_tags(topic, tags_csv)
    seen: set[str] = set()
    items: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    for tag in tags:
        try:
            data = fetch_hashtag(tag)
            for item in parse_hashtag_posts(topic, tag, data, posts_per_tag):
                if item["shortcode"] in seen:
                    continue
                seen.add(item["shortcode"])
                items.append(item)
        except Exception as exc:
            errors.append({"tag": tag, "error": str(exc)[:180]})
        time.sleep(0.35)
    items.sort(key=lambda row: row.get("score", 0), reverse=True)
    selected = items[:limit]
    return {
        "topic": topic,
        "tags": tags,
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "collected_count": len(items),
        "selected_count": len(selected),
        "items": selected,
        "errors": errors,
    }
