"""Router /ideias — fila unificada de ideias de conteúdo.

Junta num ranking só tudo o que pode virar conteúdo: os 593 roteiros do banco,
os posts que bombaram nos perfis monitorados (sinais), os conteúdos externos
garimpados, os temas anotados à mão e as oportunidades detectadas.

Cada item ganha uma nota determinística (mesma entrada = mesma nota) e a fila
sai ordenada da melhor ideia para a pior. Itens já produzidos ou descartados
somem da fila (tabela ideias_estado).
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from urllib.parse import urlsplit, urlunsplit

from fastapi import APIRouter, HTTPException, Request

from ..config import settings
from ..db import get_conn

router = APIRouter(prefix="/ideias", tags=["ideias"])

_TIPOS = {"roteiro", "sinal", "externo", "tema", "oportunidade"}
_ESTADOS = {"guardada", "produzida", "descartada"}
_FORMATOS = {"reel", "carrossel", "estatico", "stories"}

# quantos itens buscamos de cada fonte antes de rankear (paginação real é sobre
# o ranking final; aqui só evitamos carregar tabelas inteiras a cada request)
_PER_SOURCE_LIMIT = 200

# pilares editoriais do rodízio da sugestão do dia (ordem fixa = determinístico)
_PILARES = [
    "emagrecimento sustentável",
    "saúde hormonal 40+",
    "mitos e verdades",
    "bastidores e autoridade",
    "prova social",
]

_PILAR_KEYWORDS = {
    "emagrecimento sustentável": ["emagrec", "peso", "dieta", "gordura", "metabol", "saciedade"],
    "saúde hormonal 40+": ["hormon", "menopausa", "tireoide", "insulina", "cortisol", "40+", "40 anos"],
    "mitos e verdades": ["mito", "verdade", "mentira", "engano", "não funciona", "cuidado com"],
    "bastidores e autoridade": ["bastidor", "consultório", "rotina", "estudo", "ciência", "médic", "dra"],
    "prova social": ["resultado", "antes e depois", "depoimento", "transform", "paciente", "kg", "elimin"],
}

# seg/qua/sex = reel, ter/qui = carrossel, sáb = estático, dom = stories
_FORMATO_POR_DIA = {0: "reel", 1: "carrossel", 2: "reel", 3: "carrossel", 4: "reel", 5: "estatico", 6: "stories"}

def _tenant_id(conn, tenant_slug: str) -> str:
    with conn.cursor() as cur:
        cur.execute("select id from tenants where slug=%s", (tenant_slug,))
        row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="tenant não encontrado")
    return row["id"]


def _tenant_id_for_request(conn, tenant_slug: str, request: Request) -> str:
    session = getattr(request.state, "session", None)
    session_tenant_id = session.get("tid") if isinstance(session, dict) else None
    if not session_tenant_id:
        raise HTTPException(status_code=401, detail="sessão sem tenant")
    requested_tenant_id = _tenant_id(conn, tenant_slug)
    if str(session_tenant_id) != str(requested_tenant_id):
        raise HTTPException(status_code=403, detail="tenant_slug não pertence à sessão autenticada")
    return requested_tenant_id


# ---------------------------------------------------------------- score


def _decay(dt, half_life_days: float = 7.0) -> float:
    """Peso que cai pela metade a cada `half_life_days` desde `dt` (0..1)."""
    if dt is None:
        return 0.5
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    age_days = max(0.0, (datetime.now(timezone.utc) - dt).total_seconds() / 86400.0)
    return 0.5 ** (age_days / half_life_days)


def _eng_norm(engajamento: int) -> float:
    """Normaliza engajamento bruto para 0..1 (200 interações ≈ 0.5)."""
    e = max(0, int(engajamento or 0))
    return e / (e + 200.0)


def _score_roteiro(classe: str | None) -> float:
    c = (classe or "").lower()
    if c.startswith("hook"):
        return 0.6
    if "stories" in c:
        return 0.45
    return 0.5


# ---------------------------------------------------------------- normalização


def _norm_url(url: str | None) -> str | None:
    """URL sem querystring e sem barra final — chave de dedup."""
    if not url:
        return None
    try:
        parts = urlsplit(url.strip())
        path = parts.path.rstrip("/")
        return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path, "", "")) or None
    except Exception:
        return url.strip().lower() or None


def _clip(text: str | None, size: int = 220) -> str:
    t = " ".join((text or "").split())
    return t[: size - 1] + "…" if len(t) > size else t


def _formato_externo(fmt: str | None) -> str:
    f = (fmt or "").lower()
    if "carrossel" in f or "carousel" in f:
        return "carrossel"
    if "clip" in f or "reel" in f or "video" in f:
        return "reel"
    if f in {"feed", "post", "image"}:
        return "estatico"
    return "reel"


def _formato_tema(format_targets) -> str:
    targets = format_targets if isinstance(format_targets, list) else []
    for t in targets:
        f = str(t).lower()
        if "reel" in f:
            return "reel"
        if "carrossel" in f or "carousel" in f:
            return "carrossel"
        if "storie" in f:
            return "stories"
        if "estatico" in f or "estático" in f or "post" in f:
            return "estatico"
    return "carrossel"


# ---------------------------------------------------------------- coleta


def _coletar(conn, tid: str) -> list[dict]:
    itens: list[dict] = []
    with conn.cursor() as cur:
        # roteiros do banco (593): globais (tenant_id null) + do tenant
        cur.execute(
            """
            select id, codigo, classe_ivs, hook_base, tese_central, adaptacao_ivs,
                   origem, plataforma, created_at
            from viral_scripts
            where tenant_id is null or tenant_id=%s
            order by created_at desc
            limit %s
            """,
            (tid, _PER_SOURCE_LIMIT),
        )
        for r in cur.fetchall():
            titulo = _clip(r["hook_base"] or r["tese_central"] or r["codigo"] or "Roteiro sem título", 140)
            itens.append({
                "id": f"roteiro:{r['id']}",
                "tipo": "roteiro",
                "titulo": titulo,
                "resumo": _clip(r["tese_central"] or r["adaptacao_ivs"]),
                "hook": _clip(r["hook_base"], 180) or None,
                "formato_sugerido": "stories" if "stories" in (r["classe_ivs"] or "") else "reel",
                "origem": r["plataforma"] or r["origem"] or "banco de roteiros",
                "engajamento": None,
                "criado_em": r["created_at"],
                "url": None,
                "score": _score_roteiro(r["classe_ivs"]),
            })

        # sinais dos perfis monitorados
        cur.execute(
            """
            select id, network, url, caption, likes, comments, engagement,
                   coalesce(taken_at, first_seen) as quando
            from source_signals
            where tenant_id=%s or tenant_id is null
            order by engagement desc nulls last
            limit %s
            """,
            (tid, _PER_SOURCE_LIMIT),
        )
        for r in cur.fetchall():
            eng = max(int(r["engagement"] or 0), int(r["likes"] or 0) + int(r["comments"] or 0))
            titulo = _clip(r["caption"], 140) or "Post monitorado sem legenda"
            itens.append({
                "id": f"sinal:{r['id']}",
                "tipo": "sinal",
                "titulo": titulo,
                "resumo": _clip(r["caption"]),
                "hook": None,
                "formato_sugerido": "reel",
                "origem": r["network"] or "monitoramento",
                "engajamento": eng,
                "criado_em": r["quando"],
                "url": r["url"],
                "score": _eng_norm(eng) * _decay(r["quando"]),
            })

        # conteúdo externo elegível: só toca nas tabelas 022 com a feature ativa.
        if settings.content_radar_v1_enabled:
            cur.execute(
                """
                select e.id, e.source_network, e.source_profile, e.url,
                       e.canonical_format as format, e.caption,
                       coalesce(e.published_at, e.created_at) as quando, e.metrics,
                       b.metric_basis, b.performance_ratio, b.signal_state
                from external_content_items e
                join external_radar_sources rs on rs.id=e.radar_source_id
                join lateral (
                  select metric_basis, performance_ratio, signal_state
                  from external_content_baselines b
                  where b.candidate_content_item_id=e.id
                  order by b.computed_at desc
                  limit 1
                ) b on true
                where e.tenant_id=%s
                  and rs.active=true
                  and rs.source_kind in ('approved','own_account')
                  and b.signal_state in ('outlier','breakout')
                order by b.performance_ratio desc nulls last, e.updated_at desc
                limit %s
                """,
                (tid, _PER_SOURCE_LIMIT),
            )
            for r in cur.fetchall():
                m = r["metrics"] if isinstance(r["metrics"], dict) else {}
                observed_total = 0.0
                has_observed_interactions = False
                for key in ("likes", "comments"):
                    value = m.get(key)
                    if isinstance(value, (int, float)) and not isinstance(value, bool):
                        observed_total += float(value)
                        has_observed_interactions = True
                eng = int(observed_total) if has_observed_interactions else None
                ratio = float(r["performance_ratio"] or 0)
                titulo = _clip(r["caption"], 140) or f"Conteúdo de @{r['source_profile']}"
                itens.append({
                    "id": f"externo:{r['id']}",
                    "tipo": "externo",
                    "titulo": titulo,
                    "resumo": _clip(r["caption"]),
                    "hook": None,
                    "formato_sugerido": _formato_externo(r["format"]),
                    "origem": f"{r['source_network'] or 'instagram'}/@{r['source_profile']}",
                    "engajamento": eng,
                    "criado_em": r["quando"],
                    "url": r["url"],
                    "score": min(1.0, ratio / 10.0) * _decay(r["quando"]),
                })

        # temas anotados à mão
        cur.execute(
            """
            select id, theme, objective, format_targets, notes, created_at
            from manual_themes
            where tenant_id=%s
            order by created_at desc
            limit %s
            """,
            (tid, _PER_SOURCE_LIMIT),
        )
        for r in cur.fetchall():
            itens.append({
                "id": f"tema:{r['id']}",
                "tipo": "tema",
                "titulo": _clip(r["theme"], 140),
                "resumo": _clip(r["objective"] or r["notes"]),
                "hook": None,
                "formato_sugerido": _formato_tema(r["format_targets"]),
                "origem": "tema manual",
                "engajamento": None,
                "criado_em": r["created_at"],
                "url": None,
                # decaimento mais lento (meia-vida 30d): tema anotado não "estraga" em uma semana
                "score": max(0.08, 0.4 * _decay(r["created_at"], half_life_days=30.0)),
            })

        # oportunidades detectadas
        cur.execute(
            """
            select id, title, thesis, angle, source_type, created_at
            from opportunities
            where tenant_id=%s
            order by created_at desc
            limit %s
            """,
            (tid, _PER_SOURCE_LIMIT),
        )
        for r in cur.fetchall():
            itens.append({
                "id": f"oportunidade:{r['id']}",
                "tipo": "oportunidade",
                "titulo": _clip(r["title"], 140),
                "resumo": _clip(r["thesis"] or r["angle"]),
                "hook": None,
                "formato_sugerido": "carrossel",
                "origem": r["source_type"] or "radar de oportunidades",
                "engajamento": None,
                "criado_em": r["created_at"],
                "url": None,
                "score": max(0.08, 0.4 * _decay(r["created_at"], half_life_days=30.0)),
            })
    return itens


def _excluidos(conn, tid: str) -> set[str]:
    with conn.cursor() as cur:
        cur.execute(
            "select ideia_id from ideias_estado where tenant_id=%s and estado in ('produzida','descartada')",
            (tid,),
        )
        return {r["ideia_id"] for r in cur.fetchall()}


def _dedup(itens: list[dict]) -> list[dict]:
    """Mesma URL (sem querystring) ou mesmo título → fica só o de maior score."""
    ordenados = sorted(itens, key=lambda i: (-i["score"], i["id"]))
    vistos_url: set[str] = set()
    vistos_titulo: set[str] = set()
    unicos: list[dict] = []
    for it in ordenados:
        u = _norm_url(it.get("url"))
        t = (it["titulo"] or "").strip().lower()
        if u and u in vistos_url:
            continue
        if t and t in vistos_titulo:
            continue
        if u:
            vistos_url.add(u)
        if t:
            vistos_titulo.add(t)
        unicos.append(it)
    return unicos


def _fila_rankeada(conn, tid: str) -> list[dict]:
    itens = _coletar(conn, tid)
    if not settings.content_radar_v1_enabled:
        itens = [i for i in itens if i["tipo"] != "externo"]
    if settings.content_radar_v1_enabled:
        fora = _excluidos(conn, tid)
        itens = [i for i in itens if i["id"] not in fora]
    return _dedup(itens)


def _publico(it: dict) -> dict:
    """Formato de saída (sem campos internos como url crua de dedup)."""
    return {
        "id": it["id"],
        "tipo": it["tipo"],
        "titulo": it["titulo"],
        "resumo": it["resumo"],
        "hook": it["hook"],
        "formato_sugerido": it["formato_sugerido"],
        "origem": it["origem"],
        "engajamento": it["engajamento"],
        "criado_em": it["criado_em"].isoformat() if it["criado_em"] else None,
        "score": round(it["score"], 4),
        "url": it.get("url"),
    }


# ---------------------------------------------------------------- endpoints


@router.get("/fila")
def fila(
    request: Request,
    tenant_slug: str = "demo",
    limit: int = 15,
    offset: int = 0,
    q: str = "",
    tipo: str = "",
) -> dict:
    limit = max(1, min(limit, 100))
    offset = max(0, offset)
    tipo = tipo.strip().lower()
    if tipo and tipo not in _TIPOS:
        raise HTTPException(status_code=400, detail=f"tipo inválido — use um de: {', '.join(sorted(_TIPOS))}")
    termo = q.strip().lower()

    with get_conn() as conn:
        tid = _tenant_id_for_request(conn, tenant_slug, request)
        itens = _fila_rankeada(conn, tid)

    if tipo:
        itens = [i for i in itens if i["tipo"] == tipo]
    if termo:
        itens = [i for i in itens if termo in (i["titulo"] or "").lower() or termo in (i["resumo"] or "").lower()]

    total = len(itens)
    pagina = itens[offset : offset + limit]
    return {
        "itens": [_publico(i) for i in pagina],
        "total": total,
        "gerado_em": datetime.now(timezone.utc).isoformat(),
    }


@router.post("/estado")
def marcar_estado(
    request: Request,
    tenant_slug: str = "demo",
    ideia_id: str = "",
    estado: str = "",
) -> dict:
    ideia_id = ideia_id.strip()
    estado = estado.strip().lower()
    if not ideia_id:
        raise HTTPException(status_code=400, detail="ideia_id é obrigatório")
    if estado not in _ESTADOS:
        raise HTTPException(status_code=400, detail=f"estado inválido — use um de: {', '.join(sorted(_ESTADOS))}")

    with get_conn() as conn:
        tid = _tenant_id_for_request(conn, tenant_slug, request)
        with conn.cursor() as cur:
            cur.execute(
                """
                insert into ideias_estado (tenant_id, ideia_id, estado)
                values (%s, %s, %s)
                on conflict (tenant_id, ideia_id)
                do update set estado=excluded.estado, criado_em=now()
                """,
                (tid, ideia_id, estado),
            )
    return {"ok": True, "ideia_id": ideia_id, "estado": estado}


@router.get("/sugestao_do_dia")
def sugestao_do_dia(request: Request, tenant_slug: str = "demo") -> dict:
    hoje = datetime.now(timezone.utc)
    pilar = _PILARES[hoje.timetuple().tm_yday % len(_PILARES)]
    formato = _FORMATO_POR_DIA[hoje.weekday()]
    keywords = _PILAR_KEYWORDS[pilar]

    with get_conn() as conn:
        tid = _tenant_id_for_request(conn, tenant_slug, request)
        itens = _fila_rankeada(conn, tid)

    corte_48h = hoje - timedelta(hours=48)

    def _casa_pilar(it: dict) -> bool:
        texto = f"{it['titulo']} {it['resumo'] or ''} {it['hook'] or ''}".lower()
        return any(k in texto for k in keywords)

    recentes = [
        i for i in itens
        if i["criado_em"]
        and (i["criado_em"] if i["criado_em"].tzinfo else i["criado_em"].replace(tzinfo=timezone.utc)) >= corte_48h
    ]
    candidatos = [i for i in recentes if _casa_pilar(i)]
    escolhido = candidatos[0] if candidatos else ([i for i in itens if _casa_pilar(i)] or itens or [None])[0]

    return {
        "pilar": pilar,
        "formato_sugerido": formato,
        "item": _publico(escolhido) if escolhido else None,
        "degrade": "as sugestões ficam mais espertas quando o ciclo de medição fechar",
        "gerado_em": hoje.isoformat(),
    }
