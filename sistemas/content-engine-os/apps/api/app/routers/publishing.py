"""Router /publishing — publica criativo aprovado no Instagram da Dra (1 clique, nunca automático).

Fluxo: o humano aprova no banco de criativos → clica em "Publicar no Instagram" → a UI mostra
o preview (legenda + slides) → confirmação explícita → este router cria os containers na
Graph API e publica. Sem cron, sem trigger automático: só roda quando alguém clica e confirma.

Regras:
  - Só criativo com status='aprovado' e formato carrossel/estatico (reels ficam para a v2).
  - A Meta só aceita JPEG público: os PNGs do render são convertidos para JPG on-the-fly
    e servidos pelo /renders (público, já proxied no nginx).
  - Legenda = caption do criativo + hashtags + rodapé obrigatório (CRM + disclaimer).
  - Publicação registrada em meta_ig_publications; criativo vira status='publicado'.
"""
from __future__ import annotations

import glob
import io
import json
import os
import re
import time
import uuid
import zipfile
from datetime import datetime, timezone
from urllib.parse import urlencode

import httpx
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ..db import get_conn

router = APIRouter(prefix="/publishing", tags=["publishing"])

GRAPH = "https://graph.facebook.com/v23.0"
TOKEN = os.environ.get("META_IG_TOKEN", "")
IG_ID = os.environ.get("META_IG_USER_ID", "17841400449703531")
PUBLIC_BASE = os.environ.get("CONTENT_OS_PUBLIC_BASE", "https://conteudo.institutovitalslim.com.br")
RENDERS_DIR = "/root/cerebro-vital-slim/sistemas/content-engine-os/storage/assets/renders"

FOOTER = ("Dra Daniely Freitas\n"
          "Médica, Farmacêutica e Professora de Medicina\n"
          "CRM-BA 27.588\n"
          "(Este conteúdo tem caráter meramente educativo e não substitui uma consulta médica.)")

DDL = """
create table if not exists meta_ig_publications (
  id bigserial primary key,
  tenant_id uuid not null,
  creative_id uuid not null,
  ig_media_id text not null,
  permalink text,
  caption text,
  published_at timestamptz not null default now(),
  unique (tenant_id, creative_id)
);
"""


class PublishBody(BaseModel):
    tenant_slug: str = "demo"
    creative_id: str
    confirm: bool = False


def _tenant_id(conn, tenant_slug: str) -> str:
    with conn.cursor() as cur:
        cur.execute("select id from tenants where slug=%s", (tenant_slug,))
        row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="tenant não encontrado")
    return row["id"]


def _creative(conn, tid: str, cid: str) -> dict:
    with conn.cursor() as cur:
        cur.execute("select id, format, status, caption, title, hashtags from creatives "
                    "where tenant_id=%s and id=%s", (tid, cid))
        row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="criativo não encontrado")
    return row


def _jpeg_urls(cid: str) -> list[str]:
    """Converte os PNGs do render em JPGs (cacheados no mesmo dir) e devolve URLs públicas."""
    from PIL import Image

    adir = os.path.join(RENDERS_DIR, cid)
    # ordenação natural (slide_2 antes de slide_10, mesmo sem zero à esquerda)
    def _nat(p: str) -> list[int]:
        return [int(x) for x in re.findall(r"\d+", os.path.basename(p))] or [0]
    # 1 slide = 1 imagem. O .jpg cacheado só vence se for MAIS NOVO que o .png:
    # após um re-render o png muda e o jpg velho seria publicado no lugar da arte nova.
    pngs: dict[str, str] = {}
    jpgs: dict[str, str] = {}
    for p in sorted(glob.glob(os.path.join(adir, "slide_*.png")) +
                    glob.glob(os.path.join(adir, "slide_*.jpg")), key=_nat):
        stem = os.path.splitext(os.path.basename(p))[0]
        (jpgs if p.endswith(".jpg") else pngs)[stem] = p
    by_slide: dict[str, str] = {}
    for stem in set(pngs) | set(jpgs):
        png, jpg = pngs.get(stem), jpgs.get(stem)
        if jpg and (not png or os.path.getmtime(jpg) >= os.path.getmtime(png)):
            by_slide[stem] = jpg
        else:
            by_slide[stem] = png  # força reconversão abaixo (sobrescreve o jpg velho)
    urls: list[str] = []
    for src in sorted(by_slide.values(), key=_nat):
        if src.endswith(".jpg"):
            urls.append(f"{PUBLIC_BASE}/renders/{cid}/{os.path.basename(src)}")
            continue
        jpg = src[:-4] + ".jpg"
        if not os.path.exists(jpg) or os.path.getmtime(jpg) < os.path.getmtime(src):
            with Image.open(src) as im:
                im.convert("RGB").save(jpg, "JPEG", quality=90)
        urls.append(f"{PUBLIC_BASE}/renders/{cid}/{os.path.basename(jpg)}")
    return urls


def _caption(creative: dict) -> str:
    parts = [p for p in [(creative.get("caption") or "").strip()] if p]
    tags = creative.get("hashtags")
    if isinstance(tags, str):
        try:
            tags = json.loads(tags)
        except ValueError:
            tags = []
    tags = [t for t in tags if isinstance(t, str) and t.strip()] if isinstance(tags, list) else []
    if tags:
        parts.append(" ".join(t if t.startswith("#") else f"#{t}" for t in tags[:15]))
    body = "\n\n".join(parts)
    if "CRM-BA" in body:
        return body[:2200]  # limite da legenda no Instagram
    # o rodapé obrigatório (CRM + disclaimer) nunca pode ser cortado pela truncagem
    body = body[: 2200 - len(FOOTER) - 2]
    return (body + "\n\n" if body else "") + FOOTER


def _validate(creative: dict, urls: list[str]) -> None:
    if creative["status"] not in ("aprovado", "publicado"):
        raise HTTPException(status_code=422, detail="só criativo APROVADO pode ser publicado")
    if creative["format"] not in ("carrossel", "estatico"):
        raise HTTPException(status_code=422, detail="v1 publica carrossel e estático; reels ainda manual")
    if not urls:
        raise HTTPException(status_code=422, detail="criativo sem slides renderizados")
    if len(urls) > 10:
        raise HTTPException(status_code=422, detail="Instagram aceita no máximo 10 slides por carrossel")


def _meta_post(cli: httpx.Client, path: str, **data) -> dict:
    data["access_token"] = TOKEN
    r = cli.post(f"{GRAPH}/{path}", data=data, timeout=60)
    if r.status_code >= 400:
        try:
            msg = r.json().get("error", {}).get("message", r.text)
        except ValueError:
            msg = r.text
        raise HTTPException(status_code=502, detail=f"Meta recusou: {msg}")
    return r.json()


def _wait_finished(cli: httpx.Client, container_id: str, timeout_s: int = 90) -> None:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        r = cli.get(f"{GRAPH}/{container_id}", params={"fields": "status_code", "access_token": TOKEN}, timeout=30)
        status = r.json().get("status_code")
        if status == "FINISHED":
            return
        if status == "ERROR":
            raise HTTPException(status_code=502, detail="Meta reportou erro ao processar a mídia")
        time.sleep(3)
    raise HTTPException(status_code=504, detail="tempo esgotado processando a mídia na Meta")


@router.post("/instagram/preview")
def preview(body: PublishBody) -> dict:
    with get_conn() as conn:
        tid = _tenant_id(conn, body.tenant_slug)
        creative = _creative(conn, tid, body.creative_id)
        with conn.cursor() as cur:
            cur.execute(DDL)
            cur.execute("select permalink, published_at from meta_ig_publications "
                        "where tenant_id=%s and creative_id=%s", (tid, body.creative_id))
            done = cur.fetchone()
    urls = _jpeg_urls(body.creative_id)
    _validate(creative, urls)
    return {
        "creative_id": body.creative_id,
        "format": creative["format"],
        "slides": len(urls),
        "image_urls": urls,
        "caption": _caption(creative),
        "ja_publicado": dict(done) if done else None,
        "aviso": "Nada é publicado neste passo. A publicação só acontece no /publish com confirm=true.",
    }


@router.post("/instagram/publish")
def publish(body: PublishBody) -> dict:
    if not TOKEN:
        raise HTTPException(status_code=503, detail="META_IG_TOKEN ausente no ambiente da API")
    if not body.confirm:
        raise HTTPException(status_code=422, detail="publicação exige confirm=true (confirmação humana)")

    # RESERVA ANTES de qualquer chamada à Meta: um insert atômico impede que dois cliques
    # (ou dois workers) publiquem o mesmo criativo duas vezes — o perdedor recebe 409 na hora.
    with get_conn() as conn:
        tid = _tenant_id(conn, body.tenant_slug)
        creative = _creative(conn, tid, body.creative_id)
        with conn.transaction(), conn.cursor() as cur:
            cur.execute(DDL)
            cur.execute(
                "insert into meta_ig_publications (tenant_id, creative_id, ig_media_id) "
                "values (%s, %s, 'pending') on conflict (tenant_id, creative_id) do nothing",
                (tid, body.creative_id))
            reserved = cur.rowcount == 1
            if not reserved:
                cur.execute("select ig_media_id, permalink from meta_ig_publications "
                            "where tenant_id=%s and creative_id=%s", (tid, body.creative_id))
                done = cur.fetchone()
    if not reserved:
        if done and done["ig_media_id"] == "pending":
            raise HTTPException(status_code=409, detail="publicação já em andamento — aguarde")
        raise HTTPException(status_code=409, detail=f"já publicado: {(done or {}).get('permalink')}")

    def _abort_reservation() -> None:
        with get_conn() as conn2:
            with conn2.transaction(), conn2.cursor() as cur2:
                cur2.execute("delete from meta_ig_publications "
                             "where tenant_id=%s and creative_id=%s and ig_media_id='pending'",
                             (tid, body.creative_id))

    # Fase 1 — nada publicado ainda: qualquer falha aqui devolve a reserva e propaga o erro.
    try:
        urls = _jpeg_urls(body.creative_id)
        _validate(creative, urls)
        caption = _caption(creative)

        with httpx.Client() as cli:
            if len(urls) == 1:
                container = _meta_post(cli, f"{IG_ID}/media", image_url=urls[0], caption=caption)["id"]
                _wait_finished(cli, container)
            else:
                children = []
                for u in urls:
                    child = _meta_post(cli, f"{IG_ID}/media", image_url=u, is_carousel_item="true")["id"]
                    children.append(child)
                for child in children:
                    _wait_finished(cli, child)
                container = _meta_post(cli, f"{IG_ID}/media", media_type="CAROUSEL",
                                       children=",".join(children), caption=caption)["id"]
                _wait_finished(cli, container)

            media_id = _meta_post(cli, f"{IG_ID}/media_publish", creation_id=container)["id"]
    except Exception:
        _abort_reservation()  # containers órfãos expiram sozinhos na Meta; nada foi publicado
        raise

    # Fase 2 — o post ESTÁ vivo: a reserva nunca mais é apagada (bloqueia repost em retry).
    try:
        with get_conn() as conn:
            with conn.transaction(), conn.cursor() as cur:
                cur.execute("update meta_ig_publications set ig_media_id=%s, caption=%s "
                            "where tenant_id=%s and creative_id=%s",
                            (media_id, caption, tid, body.creative_id))
                cur.execute("update creatives set status='publicado' where tenant_id=%s and id=%s",
                            (tid, body.creative_id))
    except Exception:
        raise HTTPException(status_code=500,
                            detail=f"PUBLICADO no Instagram (media {media_id}), mas falhou o registro local. "
                                   "NÃO republique — o bloqueio de duplicata segue ativo.")

    permalink = None
    try:
        with httpx.Client() as cli:
            r = cli.get(f"{GRAPH}/{media_id}", params={"fields": "permalink", "access_token": TOKEN}, timeout=30)
            permalink = r.json().get("permalink")
        if permalink:
            with get_conn() as conn:
                with conn.transaction(), conn.cursor() as cur:
                    cur.execute("update meta_ig_publications set permalink=%s "
                                "where tenant_id=%s and creative_id=%s", (permalink, tid, body.creative_id))
    except Exception:
        pass  # permalink é cosmético; o post já está publicado e registrado

    return {"published": True, "ig_media_id": media_id, "permalink": permalink, "slides": len(urls)}


# ---------------------------------------------------------------------------
# Pacote de anúncio — handoff /planejamento → Ads Manager (download; NADA é publicado aqui)
# ---------------------------------------------------------------------------

ADS_TITULO_MAX = 40      # limite do campo "Título" no Ads Manager
ADS_DESCRICAO_MAX = 30   # limite do campo "Descrição" no Ads Manager
PACOTE_EXTS = (".png", ".jpg", ".jpeg", ".webp", ".mp4", ".mov", ".mp3")


# ── Agendamento de publicação (fuso America/Bahia) ──────────────────────────
# A confirmação humana acontece no ATO DE AGENDAR; o runner (cron host, 2 em 2
# min) reusa o publish() com toda a segurança (reserva atômica, 409, rollback).

TZ_BAHIA = ZoneInfo("America/Bahia")

DDL_AGENDA = """
create table if not exists ig_publicacoes_agendadas (
  id bigserial primary key,
  tenant_id uuid not null,
  creative_id uuid not null,
  agendado_para timestamptz not null,
  status text not null default 'agendada',
  erro text,
  permalink text,
  criado_em timestamptz not null default now(),
  executado_em timestamptz
);
create unique index if not exists ig_agenda_um_por_criativo
  on ig_publicacoes_agendadas (tenant_id, creative_id) where status = 'agendada';
"""


class AgendarBody(BaseModel):
    tenant_slug: str = "demo"
    creative_id: str
    quando: str  # "YYYY-MM-DDTHH:MM" SEMPRE interpretado como hora da Bahia


def _quando_utc(quando: str) -> datetime:
    try:
        naive = datetime.fromisoformat(quando.strip())
    except ValueError:
        raise HTTPException(422, "quando deve ser YYYY-MM-DDTHH:MM (hora da Bahia)")
    if naive.tzinfo is not None:
        return naive.astimezone(timezone.utc)
    return naive.replace(tzinfo=TZ_BAHIA).astimezone(timezone.utc)


def _local_str(dt: datetime) -> str:
    return dt.astimezone(TZ_BAHIA).strftime("%d/%m %H:%M")


@router.post("/instagram/agendar")
def agendar(body: AgendarBody) -> dict:
    alvo = _quando_utc(body.quando)
    if alvo <= datetime.now(timezone.utc):
        raise HTTPException(422, "o horário precisa estar no futuro (hora da Bahia)")
    with get_conn() as conn:
        tid = _tenant_id(conn, body.tenant_slug)
        creative = _creative(conn, tid, body.creative_id)
        urls = _jpeg_urls(body.creative_id)
        _validate(creative, urls)  # falha AGORA, não às 18h: aprovado, formato, <=10 slides
        with conn.transaction(), conn.cursor() as cur:
            cur.execute(DDL)
            cur.execute("select permalink from meta_ig_publications "
                        "where tenant_id=%s and creative_id=%s", (tid, body.creative_id))
            done = cur.fetchone()
            if done:
                raise HTTPException(409, f"já publicado: {done['permalink']}")
            cur.execute(DDL_AGENDA)
            cur.execute("update ig_publicacoes_agendadas set status='cancelada' "
                        "where tenant_id=%s and creative_id=%s and status='agendada'",
                        (tid, body.creative_id))
            cur.execute("insert into ig_publicacoes_agendadas (tenant_id, creative_id, agendado_para) "
                        "values (%s, %s, %s)", (tid, body.creative_id, alvo))
    return {"ok": True, "agendado_para_bahia": _local_str(alvo),
            "aviso": "o robô publica no horário marcado e avisa no Telegram"}


@router.post("/instagram/agendar/cancelar")
def agendar_cancelar(body: PublishBody) -> dict:
    with get_conn() as conn:
        tid = _tenant_id(conn, body.tenant_slug)
        with conn.transaction(), conn.cursor() as cur:
            cur.execute(DDL_AGENDA)
            cur.execute("update ig_publicacoes_agendadas set status='cancelada' "
                        "where tenant_id=%s and creative_id=%s and status='agendada'",
                        (tid, body.creative_id))
            n = cur.rowcount
    return {"ok": True, "cancelados": n}


@router.get("/instagram/agendadas")
def agendadas(tenant_slug: str = "demo") -> dict:
    with get_conn() as conn:
        tid = _tenant_id(conn, tenant_slug)
        with conn.cursor() as cur:
            cur.execute(DDL_AGENDA)
            cur.execute("""
                select a.creative_id::text as creative_id, a.agendado_para, a.status,
                       a.erro, a.permalink, c.title, c.format
                from ig_publicacoes_agendadas a
                left join creatives c on c.id = a.creative_id
                where a.tenant_id=%s and (a.status = 'agendada'
                      or a.executado_em > now() - interval '7 days')
                order by a.agendado_para
                """, (tid,))
            rows = cur.fetchall()
    return {"items": [{**dict(r),
                       "agendado_para": r["agendado_para"].isoformat(),
                       "quando_bahia": _local_str(r["agendado_para"])} for r in rows]}


@router.post("/instagram/executar-agendadas")
def executar_agendadas(tenant_slug: str = "demo") -> dict:
    """Runner (cron host). Reivindica atomicamente o que venceu e publica via publish()."""
    with get_conn() as conn:
        tid = _tenant_id(conn, tenant_slug)
        with conn.transaction(), conn.cursor() as cur:
            cur.execute(DDL_AGENDA)
            cur.execute("""
                update ig_publicacoes_agendadas set status='publicando'
                where id in (select id from ig_publicacoes_agendadas
                             where tenant_id=%s and status='agendada' and agendado_para <= now())
                returning id, creative_id::text as creative_id, agendado_para
                """, (tid,))
            due = cur.fetchall()
    executadas, erros, detalhes = 0, 0, []
    for row in due:
        try:
            res = publish(PublishBody(tenant_slug=tenant_slug,
                                      creative_id=row["creative_id"], confirm=True))
            permalink = res.get("permalink")
            executadas += 1
            fim = ("publicada", permalink, None)
        except HTTPException as e:
            if e.status_code == 409 and "já publicado" in str(e.detail):
                fim = ("publicada", None, None)
                executadas += 1
            else:
                erros += 1
                fim = ("erro", None, str(e.detail)[:400])
        except Exception as e:  # noqa: BLE001 — runner não pode morrer no meio da fila
            erros += 1
            fim = ("erro", None, str(e)[:400])
        with get_conn() as conn:
            with conn.transaction(), conn.cursor() as cur:
                cur.execute("update ig_publicacoes_agendadas set status=%s, permalink=%s, "
                            "erro=%s, executado_em=now() where id=%s",
                            (fim[0], fim[1], fim[2], row["id"]))
        detalhes.append({"creative_id": row["creative_id"], "status": fim[0],
                         "permalink": fim[1], "erro": fim[2],
                         "horario_bahia": _local_str(row["agendado_para"])})
    return {"executadas": executadas, "erros": erros, "detalhes": detalhes}


def _plain(text: str | None) -> str:
    """Copy de anúncio vai limpa: remove marcação markdown (*/_) e colapsa espaços."""
    return re.sub(r"\s+", " ", re.sub(r"[*_]+", "", text or "")).strip()


def _corta_em_palavra(text: str, limite: int) -> str:
    """Encaixa o texto no limite SEM cortar palavra no meio (regra dos campos do Ads Manager)."""
    text = text.strip()
    if len(text) <= limite:
        return text
    corte = text[:limite]
    if text[limite] != " " and " " in corte:
        corte = corte[: corte.rfind(" ")]
    return corte.rstrip(" ,;:—–-.!?…")


def _pacote_assets(cid: str) -> list[str]:
    """Todos os assets renderizados da peça — 1 arquivo por slide (o .png original vence o .jpg derivado)."""
    adir = os.path.join(RENDERS_DIR, cid)
    if not os.path.isdir(adir):
        return []

    def _nat(p: str) -> list[int]:
        return [int(x) for x in re.findall(r"\d+", os.path.basename(p))] or [0]

    by_stem: dict[str, str] = {}
    for p in sorted(glob.glob(os.path.join(adir, "*"))):
        if not p.lower().endswith(PACOTE_EXTS) or not os.path.isfile(p):
            continue
        stem = os.path.splitext(os.path.basename(p))[0]
        atual = by_stem.get(stem)
        if atual is None or (atual.lower().endswith((".jpg", ".jpeg")) and p.lower().endswith(".png")):
            by_stem[stem] = p
    return sorted(by_stem.values(), key=_nat)


PACOTE_IMG_EXTS = (".png", ".jpg", ".jpeg", ".webp")  # slides que ganham variação 1:1 e 9:16


def _variacoes_slide(path: str) -> dict[str, bytes]:
    """Gera em memória as variações Meta Ads de um slide 4:5 (nada é salvo no dir de render).

    - 1:1 (1080x1080): crop central vertical ancorado a 40% do topo — a sobra vertical é
      cortada 40% acima / 60% abaixo, preservando o terço superior quando há rosto.
    - 9:16 (1080x1920): o slide 4:5 em largura cheia, centrado sobre fundo = ele mesmo
      ampliado em cover com blur gaussiano forte e escurecido 40% (padrão stories).
    """
    from PIL import Image, ImageEnhance, ImageFilter  # PIL puro, já disponível no container

    with Image.open(path) as raw:
        im = raw.convert("RGB")

    # 1:1 — crop quadrado ancorado (horizontal centrado; vertical a 40% do topo).
    lado = min(im.width, im.height)
    x0 = (im.width - lado) // 2
    y0 = int((im.height - lado) * 0.4)
    quadrado = im.crop((x0, y0, x0 + lado, y0 + lado)).resize((1080, 1080), Image.LANCZOS)

    # 9:16 — fundo cover (blur 40 + brilho 0.6), slide centrado por cima.
    W, H = 1080, 1920
    escala = max(W / im.width, H / im.height)
    fundo = im.resize((round(im.width * escala), round(im.height * escala)), Image.LANCZOS)
    fx, fy = (fundo.width - W) // 2, (fundo.height - H) // 2
    fundo = fundo.crop((fx, fy, fx + W, fy + H))
    fundo = fundo.filter(ImageFilter.GaussianBlur(40))
    fundo = ImageEnhance.Brightness(fundo).enhance(0.6)  # escurece 40%
    frente = im.resize((W, round(im.height * W / im.width)), Image.LANCZOS)
    fundo.paste(frente, (0, (H - frente.height) // 2))

    def _jpg(img) -> bytes:
        b = io.BytesIO()
        img.save(b, "JPEG", quality=92, optimize=True)
        return b.getvalue()

    return {"1x1": _jpg(quadrado), "9x16": _jpg(fundo)}


def _montar_pacote(creative_id: str, tenant_slug: str) -> tuple[str, bytes]:
    """Monta o ZIP do pacote de anúncio: assets/{4x5,1x1,9x16}/ + copy.txt (3 campos) + checklist.md."""
    from .orchestrate import TRACKING_BASE_URL, _utm_slug  # padrão UTM canônico do sistema

    try:
        uuid.UUID(creative_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="criativo não encontrado")

    with get_conn() as conn:
        tid = _tenant_id(conn, tenant_slug)
        with conn.cursor() as cur:
            cur.execute(
                "select id::text as id, format, status, caption, title, hashtags, script, network "
                "from creatives where tenant_id=%s and id=%s", (tid, creative_id))
            creative = cur.fetchone()
    if not creative:
        raise HTTPException(status_code=404, detail="criativo não encontrado")
    if creative["status"] not in ("aprovado", "publicado"):
        raise HTTPException(status_code=422, detail="só peça APROVADA vira pacote de anúncio")

    paths = _pacote_assets(creative["id"])
    if not paths:
        raise HTTPException(status_code=422,
                            detail="criativo sem assets renderizados — renderize a peça antes de baixar o pacote")

    # Slides (imagens 4:5) ganham as variações 1:1 e 9:16; extras (áudio/vídeo) ficam em assets/.
    imagens = [p for p in paths if p.lower().endswith(PACOTE_IMG_EXTS)]
    extras = [p for p in paths if not p.lower().endswith(PACOTE_IMG_EXTS)]

    # Ângulo (conjunto Meta Ads) vem do script JSON, igual ao /generation/creatives.
    try:
        script_meta = json.loads(creative.get("script") or "{}")
    except ValueError:
        script_meta = {}
    if not isinstance(script_meta, dict):
        script_meta = {}
    angulo_nome = (script_meta.get("angulo_nome") or "").strip() or None
    angulo_slug = _utm_slug(script_meta.get("angulo") or angulo_nome, "geral")

    # Copy multiformato (regra do dono): texto principal + título ≤40 + descrição ≤30, corte em palavra inteira.
    texto_principal = _caption(creative)
    linhas = [ln for ln in (creative.get("caption") or "").splitlines() if ln.strip()]
    base = _plain(creative.get("title")) or (_plain(linhas[0]) if linhas else "")
    titulo = _corta_em_palavra(base, ADS_TITULO_MAX)
    descricao = _corta_em_palavra(base, ADS_DESCRICAO_MAX)

    fmt_slug = _utm_slug(creative.get("format"), "post")
    cid8 = creative["id"][:8]
    utm = {
        "utm_source": "meta",
        "utm_medium": "paid_social",
        "utm_campaign": f"aquisicao-{angulo_slug}",
        "utm_content": f"{fmt_slug}-{cid8}",
    }
    url_final = f"{TRACKING_BASE_URL}?{urlencode(utm)}"

    gerado = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    falta_copy = "" if base else (
        "\nATENÇÃO: a peça não tem título/caption salvos — escreva título e descrição na mão "
        "antes de subir. Campo vazio no Ads Manager derruba a entrega.\n")
    copy_txt = (
        f"PACOTE DE ANÚNCIO — criativo {cid8} ({creative.get('format') or 'peça'})\n"
        f"Conjunto (ângulo): {angulo_nome or '— sem ângulo salvo na peça'}\n"
        f"Gerado em {gerado}\n"
        "\n"
        "Regra do dono: todo anúncio Meta Ads sobe em 3 formatos (9:16, 4:5 e 1:1)\n"
        "com os 3 campos de copy preenchidos — nenhum vazio.\n"
        f"{falta_copy}"
        "\n"
        "=== TEXTO PRINCIPAL (campo \"Texto principal\") ===\n"
        f"{texto_principal}\n"
        "\n"
        f"=== TÍTULO (campo \"Título\" — limite {ADS_TITULO_MAX}, este tem {len(titulo)}) ===\n"
        f"{titulo}\n"
        "\n"
        f"=== DESCRIÇÃO (campo \"Descrição\" — limite {ADS_DESCRICAO_MAX}, este tem {len(descricao)}) ===\n"
        f"{descricao}\n"
    )

    conjunto_txt = angulo_nome or "defina pelo tema da peça (veio sem ângulo salvo)"
    if imagens:
        linha_assets = (f"- Assets no pacote: {len(imagens)} slide(s) × 3 formatos "
                        "(`assets/4x5`, `assets/1x1`, `assets/9x16`)"
                        + (f" + {len(extras)} arquivo(s) extra em `assets/`" if extras else ""))
        item_formatos = ("- [ ] Formatos: as variações 9:16, 4:5 e 1:1 JÁ VÃO no pacote "
                         "(`assets/9x16`, `assets/4x5`, `assets/1x1`) — subir as 3 no anúncio, nada a gerar na mão")
    else:
        linha_assets = f"- Assets no pacote: {len(paths)} arquivo(s) em `assets/`"
        item_formatos = "- [ ] Formatos: gerar as variações 9:16 e 1:1 além do asset original"
    checklist_md = (
        "# Checklist — subir este anúncio no Ads Manager\n"
        "\n"
        f"- Criativo: `{creative['id']}`\n"
        f"- Peça: {titulo or '(sem título salvo)'}\n"
        f"- Conjunto (ângulo): **{conjunto_txt}**\n"
        f"{linha_assets}\n"
        "\n"
        "## Estrutura padrão da conta\n"
        "1 campanha ABO de aquisição · 5 conjuntos (1 ângulo por conjunto) · "
        "3 criativos ativos por conjunto · público amplo.\n"
        "\n"
        "- [ ] Campanha: usar a campanha ABO de aquisição vigente (só criar nova se não existir)\n"
        f"- [ ] Conjunto: selecionar/nomear pelo ângulo — \"{conjunto_txt}\"\n"
        "- [ ] Régua 5×3: conferir se o conjunto fecha 3 criativos ativos depois desta subida\n"
        f"{item_formatos}\n"
        "- [ ] Copy: colar os 3 campos do copy.txt (texto principal + título + descrição)\n"
        "- [ ] URL de destino com a UTM padrão abaixo — sem UTM o lead chega sem origem no relatório\n"
        "- [ ] Subir PAUSADO, revisar o preview em feed/stories/reels e só então ativar\n"
        "\n"
        "## UTM padrão\n"
        "\n"
        "```\n"
        + "\n".join(f"{k}={v}" for k, v in utm.items()) +
        "\n```\n"
        "\n"
        f"URL final pronta:\n{url_final}\n"
    )

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in imagens:
            stem = os.path.splitext(os.path.basename(p))[0]
            zf.write(p, arcname=f"assets/4x5/{os.path.basename(p)}")
            variacoes = _variacoes_slide(p)  # on-the-fly, em memória — não polui a galeria de renders
            zf.writestr(f"assets/1x1/{stem}.jpg", variacoes["1x1"])
            zf.writestr(f"assets/9x16/{stem}.jpg", variacoes["9x16"])
        for p in extras:
            zf.write(p, arcname=f"assets/{os.path.basename(p)}")
        zf.writestr("copy.txt", copy_txt)
        zf.writestr("checklist.md", checklist_md)
    return f"pacote-ads-{cid8}.zip", buf.getvalue()


@router.get("/pacote-ads/{creative_id}")
def pacote_ads(creative_id: str, tenant_slug: str = "demo") -> StreamingResponse:
    """ZIP de subida no Ads Manager: assets nos 3 formatos (4:5 + variações 1:1 e 9:16
    geradas on-the-fly) + copy.txt + checklist.md.

    Handoff do /planejamento: a peça aprovada para Meta Ads é só leitura na UI — quem sobe
    o anúncio baixa este pacote e segue o checklist. Nada é publicado por este endpoint.
    """
    nome, blob = _montar_pacote(creative_id, tenant_slug)
    return StreamingResponse(
        io.BytesIO(blob), media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{nome}"',
                 "Content-Length": str(len(blob))})
