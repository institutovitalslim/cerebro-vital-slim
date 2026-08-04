# -*- coding: utf-8 -*-
"""gen_cientifico.py — slides do carrossel CIENTÍFICO no system design IVS.

Formato tweet (ideia da skill tweet-carrossel) executado com a identidade do design
system dos demais carrosséis (ivs_brand: fundo seda-sobre-preto premium, Montserrat,
dourado IVS, rodapé CRM):
  - render_tweet : avatar real + "Dra Daniely Freitas ✓" + handle, corpo sans com
                   hierarquia (bullets → em dourado), referência em itálico discreto.
  - render_paper : tweet curto + PRINT REAL do paper (capture_pubmed) emoldurado em
                   card de borda dourada — o slide de credibilidade.
A capa NÃO é renderizada aqui: usa o gen_foto (mesma capa aprovada dos virais).
"""
import os

import ivs_brand as B
from PIL import Image, ImageDraw, ImageOps

AVATAR = "/root/avatar_hq.png"
FEED = (1080, 1350)
MARGIN = 84
TXT_W = FEED[0] - 2 * MARGIN


def _avatar(size: int) -> Image.Image:
    im = Image.open(AVATAR).convert("RGBA")
    im = ImageOps.fit(im, (size, size))
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size, size), fill=255)
    im.putalpha(mask)
    return im


def _verified(d: ImageDraw.ImageDraw, x: int, y: int, s: int = 30) -> None:
    d.ellipse((x, y, x + s, y + s), fill=(29, 155, 240))
    d.line([(x + s * 0.26, y + s * 0.52), (x + s * 0.44, y + s * 0.70),
            (x + s * 0.76, y + s * 0.30)], fill="white", width=4)


def _seta(d, x, y, size, color):
    """Seta vetorial (a Montserrat não tem o glifo '→' — texto virava tofu)."""
    cy = y + size * 0.60
    x1 = x + size * 0.78
    lw = max(4, size // 11)
    d.line([(x, cy), (x1, cy)], fill=color, width=lw)
    ah = size * 0.20
    d.polygon([(x1, cy - ah), (x1 + ah * 1.4, cy), (x1, cy + ah)], fill=color)


def _wrap(d, text, fnt, max_w):
    words, lines, cur = (text or "").split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if d.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def _header(img, d, y: int) -> int:
    """Avatar + nome verificado + handle. Retorna o y após o header."""
    av_size = 100
    av = _avatar(av_size)
    img.paste(av, (MARGIN, y), av)
    name_f = B.font("sans_med", 40)
    handle_f = B.font("sans", 30)
    nx = MARGIN + av_size + 24
    d.text((nx, y + 10), "Dra Daniely Freitas", font=name_f, fill=B.C.INK)
    _verified(d, nx + int(d.textlength("Dra Daniely Freitas", font=name_f)) + 16, y + 16)
    d.text((nx, y + 62), "@dradaniely.freitas", font=handle_f, fill=(140, 134, 126))
    return y + av_size + 54


def _tweet_paragraphs(text: str) -> list[str]:
    return [p.strip() for p in (text or "").split("\n")]


def _measure(d, paragraphs, body_f, ref_f, max_w):
    h = 0
    for p in paragraphs:
        if not p:
            h += 34
            continue
        fnt = ref_f if p.lower().startswith("ref:") else body_f
        h += len(_wrap(d, p, fnt, max_w)) * (int(fnt.size * 1.36)) + 18
    return h


def render_tweet(spec: dict, outdir: str, prefix: str) -> list[str]:
    w, h = FEED
    img = B.background(FEED)
    d = ImageDraw.Draw(img)
    paragraphs = _tweet_paragraphs(spec.get("tweet") or "")

    # tipografia adaptativa: corpo 46 -> 40 -> 36 até caber com respiro
    for body_size in (46, 42, 38, 34):
        body_f = B.font("sans", body_size)
        ref_f = B.font("serif_italic", max(26, body_size - 12))
        content_h = _measure(d, paragraphs, body_f, ref_f, TXT_W)
        header_est = 154
        if 150 + header_est + content_h < h - 170:
            break

    total = 154 + content_h
    y = max(130, (h - total - 120) // 2)
    y = _header(img, d, y)

    for p in paragraphs:
        if not p:
            y += 34
            continue
        is_ref = p.lower().startswith("ref:")
        is_bullet = p.startswith("→")
        fnt = ref_f if is_ref else body_f
        color = B.C.GOLD if is_ref else B.C.INK
        lh = int(fnt.size * 1.36)
        indent = MARGIN + (52 if is_bullet else 0)
        first = True
        for line in _wrap(d, p[1:].strip() if is_bullet else p, fnt, TXT_W - (52 if is_bullet else 0)):
            if is_bullet and first:
                _seta(d, MARGIN, y, fnt.size, B.C.GOLD)
            d.text((indent, y), line, font=fnt, fill=color)
            y += lh
            first = False
        y += 18
    B.footer(img)
    return [B.save(img, os.path.join(outdir, prefix + "_01.png"))]


def render_paper(spec: dict, outdir: str, prefix: str) -> list[str]:
    """Slide de credibilidade: frase curta + print do paper em card dourado + referência."""
    w, h = FEED
    img = B.background(FEED)
    d = ImageDraw.Draw(img)
    y = _header(img, d, 120)

    intro = (spec.get("intro") or "O estudo existe. Publicado e revisado:").strip()
    body_f = B.font("sans", 42)
    for line in _wrap(d, intro, body_f, TXT_W):
        d.text((MARGIN, y), line, font=body_f, fill=B.C.INK)
        y += int(42 * 1.36)
    y += 28

    paper_path = spec.get("paper_image") or ""
    ref = (spec.get("reference") or "").strip()
    card_x0, card_x1 = MARGIN, w - MARGIN
    inner = 22
    # zona proibida: nada pode encostar na linha do rodapé (h*0.945) — respiro de 30px
    footer_top = int(h * 0.945) - 30

    # mede a referência ANTES do print: o card encolhe p/ ela caber inteira
    ref_f = B.font("serif_italic", 32)
    ref_lines = _wrap(d, ref, ref_f, TXT_W) if ref else []
    if ref_lines and len(ref_lines) * int(ref_f.size * 1.38) > 220:
        ref_f = B.font("serif_italic", 27)  # referência longa: encolhe 1 passo
        ref_lines = _wrap(d, ref, ref_f, TXT_W)
    ref_lh = int(ref_f.size * 1.38)
    ref_h = (len(ref_lines) * ref_lh + 26) if ref_lines else 0

    if paper_path and os.path.exists(paper_path):
        paper = Image.open(paper_path).convert("RGB")
        target_w = (card_x1 - card_x0) - 2 * inner
        scale = target_w / paper.width
        ph = int(paper.height * scale)
        paper = paper.resize((target_w, ph))
        max_ph = footer_top - y - ref_h - 2 * inner - 26
        if paper.height > max_ph:
            paper = paper.crop((0, 0, paper.width, max_ph))  # LIÇÃO: corta embaixo, nunca a largura
        card_h = paper.height + 2 * inner
        d.rounded_rectangle((card_x0, y, card_x1, y + card_h), radius=16,
                            outline=B.C.GOLD, width=3, fill=(10, 8, 5))
        img.paste(paper, (card_x0 + inner, y + inner))
        y += card_h + 26
    for line in ref_lines:
        if y + ref_lh > footer_top:
            break  # nunca invade o rodapé, aconteça o que acontecer
        d.text((w / 2, y), line, font=ref_f, fill=B.C.GOLD, anchor="ma")
        y += ref_lh
    B.footer(img)
    return [B.save(img, os.path.join(outdir, prefix + "_01.png"))]
