#!/usr/bin/env python3
"""render_daemon.py — Worker de render FOTO-LED no host do Content Engine OS.
Regra-mãe (Tiaro 2026-06-14): todo criativo nasce sobre uma IMAGEM com contexto.
Capa/CTA = foto da Dra. (autoridade); miolo = imagem de tema; overlay via gen_foto
(design-system-ivs canônico). Polling em creatives (gerado, gate score>=60).
Sem deps de DB no host: psql via docker exec.
"""
import hashlib
import json
import os
import re
import signal
import subprocess
import sys
import time
import urllib.request

DS = "/root/cerebro-vital-slim/skills/design-system-ivs"
sys.path.insert(0, DS)
import gen_foto  # noqa: E402

ASSETS = os.path.join(DS, "assets")
DRA_COVER = os.path.join(ASSETS, "dra_blazer.jpg")     # autoridade clínica (capa)
DRA_CTA = os.path.join(ASSETS, "dra_vestido.jpg")      # programa (CTA)
TEMAS = [os.path.join(ASSETS, "tema_card%d.png" % i) for i in (1, 2, 3, 4)]          # 4:5
TEMAS_916 = [os.path.join(ASSETS, "tema_card%d_916.png" % i) for i in (1, 2, 3, 4)]  # 9:16
# REGRA CANÔNICA (Tiaro): CARROSSEL/ESTÁTICO = 4:5 (feed) | STORIES/REELS = 9:16
FEED = (1080, 1350)
STORY = (1080, 1920)

RENDERS = "/root/cerebro-vital-slim/sistemas/content-engine-os/storage/assets/renders"
HF_CACHE = "/root/cerebro-vital-slim/sistemas/content-engine-os/storage/assets/hf_cache"
# Produção deve priorizar estabilidade: Higgsfield fica opt-in.
# Quando ligado, cada chamada tem timeout hard com kill do process group para não travar a fila.
HF_ENABLE = os.environ.get("HF_ENABLE", "0") == "1"
HF_TIMEOUT = int(os.environ.get("HF_TIMEOUT", "220"))
HF_STYLE = ("{ctx}. Estilo: fotografia editorial cinematográfica premium, luz natural quente, "
            "tons terrosos e dourados discretos, profundidade de campo, atmosfera sofisticada e íntima, "
            "sem texto, sem palavras, sem letras, sem logotipo, alta qualidade")
PG = ["docker", "exec", "content-engine-postgres", "psql", "-U", "content_engine",
      "-d", "content_engine", "-tAc"]


def hf_image(ctx: str, aspect: str, idx) -> str | None:
    """Gera (ou reusa do cache) a foto de tema do slide via Higgsfield nano_banana_2.
    Retorna o caminho do PNG, ou None p/ cair no banco de assets."""
    if not HF_ENABLE or not ctx.strip():
        return None
    prompt = HF_STYLE.format(ctx=ctx.strip()[:160])
    os.makedirs(HF_CACHE, exist_ok=True)
    dest = os.path.join(HF_CACHE, hashlib.md5((prompt + aspect).encode()).hexdigest()[:16] + ".png")
    if os.path.exists(dest) and os.path.getsize(dest) > 2000:
        return dest
    try:
        cmd = [
            "higgsfield", "generate", "create", "nano_banana_2", "--prompt", prompt,
            "--aspect_ratio", aspect, "--resolution", "2k", "--wait", "--json",
        ]
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True,
        )
        try:
            stdout, stderr = proc.communicate(timeout=HF_TIMEOUT)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            stdout, stderr = proc.communicate()
            raise TimeoutError(f"higgsfield timeout após {HF_TIMEOUT}s")
        if proc.returncode != 0:
            raise RuntimeError((stderr or stdout or f"higgsfield rc={proc.returncode}").strip()[:500])
        url = json.loads(stdout)[0]["result_url"]
        urllib.request.urlretrieve(url, dest)
        if os.path.getsize(dest) > 2000:
            print("[hf] idx%s gerado: %s" % (idx, os.path.basename(dest)), flush=True)
            return dest
    except Exception as e:
        print("[hf-erro] idx%s: %s" % (idx, e), flush=True)
    return None


def psql(sql: str) -> str:
    return subprocess.run(PG + [sql], capture_output=True, text=True).stdout.strip()


def esc(s: str) -> str:
    return (s or "").replace("'", "''")


def clean(s) -> str:
    s = str(s or "").strip()
    s = re.sub(r"^\s*(slide|cena|frame)\s*\d+\s*(\([^)]*\))?\s*[–\-:]\s*", "", s, flags=re.I)
    if ":" in s[:24]:
        s = re.sub(r"^\s*[A-Za-zÀ-ú ]{2,18}:\s*", "", s)
    s = s.strip().strip('"')
    return " ".join(s.split())


def split_head_body(s: str):
    s = clean(s)
    m = re.split(r"[:–]\s+", s, maxsplit=1)
    if len(m) == 2 and len(m[0]) <= 42:
        return m[0].strip(), m[1].strip()
    parts = re.split(r"(?<=[.!?])\s+", s, maxsplit=1)
    return parts[0][:60].strip(), (parts[1].strip() if len(parts) > 1 else None)


def sentences_fit(s, n):
    s = clean(s)
    if not s:
        return None
    acc = ""
    for sent in re.findall(r"[^.!?]*[.!?]", s):
        if len(acc) + len(sent) > n:
            break
        acc += sent
    return acc.strip() or None


def parse_out(c):
    out = c.get("script")
    if isinstance(out, str):
        try:
            out = json.loads(out)
        except Exception:
            out = {}
    return out or {}


def build_slides(c):
    """Lista de specs gen_foto (foto-led) — um por peça/slide."""
    fmt = (c.get("format") or "estatico").lower()
    out = parse_out(c)

    if fmt == "carrossel":
        destino = out.get("destino", "feed")
        raw = out.get("slides") or []
        structured = bool(raw) and isinstance(raw[0], dict)
        cta_label = "QUERO SER AVALIADA" if destino == "meta_ads" else "SALVA E COMPARTILHA"
        # CAPA (Dra. blazer) — title com *ênfase* renderizada em dourado pelo gen_foto
        slides = [{
            "photo": DRA_COVER, "label": "INSTITUTO VITAL SLIM", "anchor": 0.62, "zone": "bottom",
            "title": clean(out.get("title")) or "Toda mulher 40+ precisa saber disso.",
            "sub": sentences_fit(out.get("cover_sub") or out.get("hook", ""), 120)
                   or "Os sintomas têm nome. E têm tratamento.",
            "cta": "ARRASTA PRO LADO", "size": FEED}]
        if structured:
            for i, s in enumerate(raw, 1):
                photo = hf_image((s.get("image_prompt") or "").strip(), "4:5", i) \
                    or TEMAS[(i - 1) % len(TEMAS)]
                slides.append({
                    "photo": photo, "label": s.get("label") or ("SINAL %d" % i),
                    "anchor": 0.5, "zone": "bottom", "title": clean(s.get("headline")) or "—",
                    "sub": sentences_fit(s.get("sub", ""), 120),
                    "cta": "ARRASTA PRO LADO", "size": FEED})
        else:  # legado: slides como strings
            mid = raw[1:-1] if len(raw) > 2 else raw
            for i, s in enumerate(mid, 1):
                head, body = split_head_body(s)
                ctx = ("%s %s" % (head, body or "")).strip()
                photo = hf_image(ctx, "4:5", i) or TEMAS[(i - 1) % len(TEMAS)]
                slides.append({
                    "photo": photo, "label": "SINAL %d" % i, "anchor": 0.5, "zone": "bottom",
                    "title": head, "sub": sentences_fit(body, 120),
                    "cta": "ARRASTA PRO LADO", "size": FEED})
        # CTA final (Dra. vestido) — label muda no Meta Ads (conversão)
        slides.append({
            "photo": DRA_CTA, "label": "INSTITUTO VITAL SLIM", "anchor": 0.5, "zone": "bottom",
            "title": clean(out.get("cta_headline")) or "Salve e compartilhe.",
            "sub": sentences_fit(out.get("cta_sub") or out.get("caption", ""), 120)
                   or "Mande para quem precisa ouvir isso.",
            "cta": cta_label, "size": FEED})
        return slides

    if fmt in ("reels", "stories"):
        return [{
            "photo": DRA_COVER, "story": True, "anchor": 0.55, "zone": "bottom",
            "label": "INSTITUTO VITAL SLIM",
            "title": clean(out.get("hook") or out.get("title")) or "Instituto Vital Slim",
            "cta": "SALVA ESSE VÍDEO"}]

    # estático — afirmação única foto-led (4:5 feed)
    return [{
        "photo": DRA_COVER, "anchor": 0.62, "zone": "bottom", "size": FEED,
        "title": clean(out.get("headline") or out.get("title")) or "Instituto Vital Slim",
        "sub": sentences_fit(out.get("body", ""), 160), "cta": "SALVA ESSE POST"}]


def fetch_pending():
    raw = psql("select coalesce(json_agg(t),'[]') from (select id::text, format, network, "
               "script, title, caption from creatives where status='gerado' "
               "and asset_url is null and coalesce(quality_score,0) >= 60 "
               "order by created_at limit 5) t;")
    try:
        return json.loads(raw or "[]")
    except Exception:
        return []


def process(c):
    cid = c["id"]
    outdir = os.path.join(RENDERS, cid)
    os.makedirs(outdir, exist_ok=True)
    for f in os.listdir(outdir):   # limpa renders antigos (evita stale/mistura de versões)
        try:
            os.remove(os.path.join(outdir, f))
        except OSError:
            pass
    try:
        slides = build_slides(c)
        paths = []
        for i, spec in enumerate(slides, 1):
            paths += gen_foto.render(spec, outdir, "slide_%02d" % i)
        if not paths:
            raise RuntimeError("nenhum arquivo gerado")
        first = "/renders/%s/%s" % (cid, os.path.basename(sorted(paths)[0]))
        psql("update creatives set asset_url='%s', status='renderizado' where id='%s';"
             % (esc(first), cid))
        print("[ok] %s -> %d peça(s) foto-led (%s)" % (cid, len(paths), first), flush=True)
    except Exception as e:
        psql("update creatives set status='render_erro' where id='%s';" % cid)
        print("[erro] %s: %s" % (cid, e), flush=True)


def main():
    os.makedirs(RENDERS, exist_ok=True)
    print("render-daemon FOTO-LED iniciado (poll 5s) -> %s" % RENDERS, flush=True)
    while True:
        for c in fetch_pending():
            process(c)
        time.sleep(5)


if __name__ == "__main__":
    main()
