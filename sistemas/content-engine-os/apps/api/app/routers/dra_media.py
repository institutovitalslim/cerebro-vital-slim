"""
dra_media.py — Banco de fotos da Dra Daniely (Content Engine OS).

Módulo para incluir/gerir as fotos da Dra usadas nos criativos. Fonte única:
/root/cerebro-vital-slim/cerebro/assets/fotos-dra-daniely/ (+ media-metadata.json).

GATE de compliance no upload (Codex GPT-5.5 visão): bloqueia medicação/seringa/caneta
(Mounjaro/Ozempic)/jaleco/clínica/antes-depois/nudez/texto ANTES de entrar no acervo.
Regras: variar imagem/roupa, preferir fotos REAIS, padrão fundo preto.
"""
from __future__ import annotations

import base64
import io
import json
import re
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse

from app.services.codex_client import CodexClient
from app.services.upload_security import MAX_IMAGE_BYTES, save_upload_limited

router = APIRouter(prefix="/assets/dra", tags=["dra-fotos"])

DRA_DIR = Path("/root/cerebro-vital-slim/cerebro/assets/fotos-dra-daniely")
META = DRA_DIR / "media-metadata.json"
BLACKLIST = DRA_DIR / "_BLACKLIST_compliance"
THUMBS = DRA_DIR / ".thumbs"
INCOMING = DRA_DIR / ".incoming"
ALLOWED_EXT = {".png", ".jpg", ".jpeg", ".webp"}

GATE_SYSTEM = (
    "Voce e auditor de compliance de imagens da medica Dra. Daniely Freitas (Instituto Vital Slim), "
    "para um banco de fotos usado em criativos de marketing no Meta Ads. Avalie a FOTO. Regra-mae: na duvida, REPROVE.\n"
    "REPROVE (approved=false) se contiver QUALQUER um: medicacao, comprimido, capsula, ampola, frasco de remedio; "
    "SERINGA, injecao, CANETA de aplicacao (tipo Ozempic/Mounjaro); JALECO ou avental branco; ambiente de "
    "clinica/consultorio/recepcao/hospital; antes-e-depois corporal, barriga/corpo exposto, nudez, lingerie/biquini; "
    "texto promocional legivel ou em ingles.\n"
    "APROVE retrato profissional da medica VESTIDA de forma elegante (blazer, vestido, blusa), de preferencia em "
    "fundo preto/estudio escuro, sem nenhum dos itens acima.\n"
    "Responda SOMENTE JSON valido, sem markdown: "
    '{"approved":bool,"violations":[str],"background":str,"outfit":str,"has_text":bool,"reason":str}'
)
GATE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["approved", "violations", "background", "outfit", "has_text", "reason"],
    "properties": {
        "approved": {"type": "boolean"},
        "violations": {"type": "array", "items": {"type": "string"}},
        "background": {"type": "string"},
        "outfit": {"type": "string"},
        "has_text": {"type": "boolean"},
        "reason": {"type": "string"},
    },
}


def _load_meta() -> list[dict]:
    if not META.exists():
        return []
    try:
        return json.load(open(META, encoding="utf-8"))
    except Exception:
        return []


def _save_meta(items: list[dict]) -> None:
    json.dump(items, open(META, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def _safe(filename: str) -> str:
    name = Path(filename or "").name  # impede path traversal
    if not name or name.startswith("."):
        raise HTTPException(status_code=400, detail="nome invalido")
    return name


def _slug(*parts: str) -> str:
    raw = "-".join(p for p in parts if p).lower()
    raw = re.sub(r"[^a-z0-9]+", "-", raw).strip("-")
    return raw or "upload"


def _next_index(items: list[dict]) -> int:
    mx = 0
    for it in items:
        m = re.match(r"daniely-(\d+)", it.get("file", ""))
        if m:
            mx = max(mx, int(m.group(1)))
    for f in DRA_DIR.glob("daniely-*.*"):
        m = re.match(r"daniely-(\d+)", f.name)
        if m:
            mx = max(mx, int(m.group(1)))
    return mx + 1


def _dims(path: Path) -> tuple[int, int]:
    try:
        from PIL import Image
        with Image.open(path) as im:
            return im.size
    except Exception:
        return (0, 0)


def _data_url(path: Path, max_side: int = 1024) -> str:
    """Imagem -> data-URL JPEG reduzida (cabe bem na visao)."""
    try:
        from PIL import Image
        with Image.open(path) as im:
            im = im.convert("RGB")
            w, h = im.size
            scale = min(1.0, max_side / max(w, h))
            if scale < 1.0:
                im = im.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
            buf = io.BytesIO()
            im.save(buf, format="JPEG", quality=85)
            b64 = base64.b64encode(buf.getvalue()).decode()
            return f"data:image/jpeg;base64,{b64}"
    except Exception:
        mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
        return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}"


@router.get("")
def list_dra(ads: bool = False) -> dict:
    """ads=true => modo anúncio: oculta fotos ads_safe=false (medicação/caneta/biomeds, que só valem no feed orgânico)."""
    items = _load_meta()
    out = []
    for it in items:
        f = it.get("file", "")
        if not f.startswith("daniely-"):
            continue
        if not (DRA_DIR / f).exists():
            continue
        ads_safe = it.get("ads_safe", True)
        if ads and not ads_safe:
            continue
        out.append({
            "file": f,
            "width": it.get("width", 0),
            "height": it.get("height", 0),
            "bytes": it.get("bytes", 0),
            "background": it.get("background", ""),
            "outfit": it.get("outfit", ""),
            "tags": it.get("tags", []),
            "source": it.get("source", "ensaio"),
            "ads_safe": ads_safe,
            "url": f"/assets/dra/photo/{f}",
            "thumb": f"/assets/dra/thumb/{f}",
        })
    return {"items": out, "total": len(out), "ads_only": ads}


@router.get("/photo/{filename}")
def get_photo(filename: str) -> FileResponse:
    name = _safe(filename)
    path = DRA_DIR / name
    if not path.exists():
        raise HTTPException(status_code=404, detail="foto nao encontrada")
    return FileResponse(str(path))


@router.get("/thumb/{filename}")
def get_thumb(filename: str) -> FileResponse:
    name = _safe(filename)
    src = DRA_DIR / name
    if not src.exists():
        raise HTTPException(status_code=404, detail="foto nao encontrada")
    THUMBS.mkdir(exist_ok=True)
    thumb = THUMBS / (name + ".jpg")
    if not thumb.exists() or thumb.stat().st_mtime < src.stat().st_mtime:
        try:
            from PIL import Image
            with Image.open(src) as im:
                im = im.convert("RGB")
                im.thumbnail((480, 720), Image.LANCZOS)
                im.save(thumb, format="JPEG", quality=82)
        except Exception:
            return FileResponse(str(src))  # sem PIL: serve original
    return FileResponse(str(thumb), media_type="image/jpeg")


@router.post("/upload")
async def upload_dra(
    file: UploadFile = File(...),
    outfit: str = Form(""),
    background: str = Form("preto"),
    tags: str = Form(""),
) -> JSONResponse:
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXT:
        raise HTTPException(status_code=400, detail=f"formato {ext or '?'} nao suportado (use png/jpg/webp)")
    INCOMING.mkdir(exist_ok=True)
    tmp = INCOMING / f"{uuid.uuid4().hex}{ext}"
    await save_upload_limited(file, tmp, max_bytes=MAX_IMAGE_BYTES)

    # GATE de compliance (Codex visao) — NUNCA OpenRouter
    try:
        cx = CodexClient()
        res = await cx.generate(
            prompt="Esta foto pode entrar no banco de imagens da Dra para criativos do Meta Ads?",
            system=GATE_SYSTEM,
            images=[_data_url(tmp)],
            output_schema=GATE_SCHEMA,
            timeout=150,
        )
        content = res.get("content", "")
        m = re.search(r"\{.*\}", content, re.S)
        verdict = json.loads(m.group(0)) if m else {"approved": False, "reason": "parse_fail", "violations": []}
    except Exception as e:
        tmp.unlink(missing_ok=True)
        raise HTTPException(status_code=502, detail=f"gate de compliance falhou: {str(e)[:160]}")

    approved = bool(verdict.get("approved")) and not verdict.get("violations") and not verdict.get("has_text")
    if not approved:
        tmp.unlink(missing_ok=True)
        return JSONResponse(status_code=200, content={
            "approved": False,
            "violations": verdict.get("violations", []),
            "reason": verdict.get("reason", ""),
            "has_text": verdict.get("has_text", False),
        })

    # aprovado -> entra no acervo + catalogo
    items = _load_meta()
    idx = _next_index(items)
    bg = (background or verdict.get("background") or "preto").strip()
    outfit_final = (outfit or verdict.get("outfit") or "").strip()
    fname = f"daniely-{idx:02d}-{_slug(outfit_final, bg)}{ext}"
    final = DRA_DIR / fname
    shutil.move(str(tmp), str(final))
    w, h = _dims(final)
    items.append({
        "file": fname,
        "path": str(final),
        "width": w,
        "height": h,
        "mode": "RGB",
        "bytes": final.stat().st_size,
        "background": bg,
        "outfit": outfit_final,
        "tags": [t.strip() for t in tags.split(",") if t.strip()],
        "source": "upload",
        "added_at": datetime.now(timezone.utc).isoformat(),
    })
    _save_meta(items)
    return JSONResponse(status_code=200, content={
        "approved": True,
        "file": fname,
        "background": bg,
        "outfit": outfit_final,
        "url": f"/assets/dra/photo/{fname}",
        "reason": verdict.get("reason", ""),
    })


@router.post("/quarantine")
def quarantine_dra(filename: str = Form(...)) -> dict:
    name = _safe(filename)
    src = DRA_DIR / name
    if not src.exists():
        raise HTTPException(status_code=404, detail="foto nao encontrada")
    BLACKLIST.mkdir(exist_ok=True)
    shutil.move(str(src), str(BLACKLIST / name))
    items = [it for it in _load_meta() if it.get("file") != name]
    _save_meta(items)
    return {"ok": True, "file": name, "quarantined_to": str(BLACKLIST / name)}
