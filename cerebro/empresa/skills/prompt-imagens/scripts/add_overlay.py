#!/usr/bin/env python3
"""
add_overlay.py — Adiciona texto/tipografia sobre uma foto REAL preservando 100%
a fisionomia. Use para tributos, homenagens, posters com foto real, cards
motivacionais, etc.

Como preserva 100% a fisionomia: nao regenera a imagem via IA, apenas adiciona
camadas (gradient, texto, bordas) sobre a foto original via Pillow.

Uso:
    python3 add_overlay.py \
        --foto /tmp/ayrton.jpg \
        --frase "A primeira vez que eu ganhei uma corrida, chorei." \
        --autor "Ayrton Senna" \
        --estilo "classico" \
        --aspect-ratio 4:5 \
        --out /root/tributo_ayrton.jpg

Estilos disponiveis:
  classico       - gradient escuro em baixo, serif elegante (tipo poster)
  minimalista    - texto branco grande, gradient discreto
  editorial      - texto em caixa lateral (tipo revista)
  cinema         - letterbox (barras pretas em cima/baixo), texto central
  faixa-lateral  - barra vertical colorida na esquerda com texto branco
"""
import argparse, os, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

ASPECT_SIZES = {
    "4:5":  (1080, 1350),
    "1:1":  (1080, 1080),
    "9:16": (1080, 1920),
    "16:9": (1920, 1080),
    "3:4":  (1080, 1440),
}

FONTS_BOLD = [
    "/usr/local/share/fonts/Montserrat-Black.ttf",
    "/usr/local/share/fonts/Montserrat-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]
FONTS_REG = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]
FONTS_SERIF = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
    "/usr/local/share/fonts/Montserrat-Black.ttf",  # fallback
]


def load_font(paths: list, size: int):
    for p in paths:
        if os.path.isfile(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def fit_photo(img: Image.Image, target_w: int, target_h: int, focus_y: float = 0.3) -> Image.Image:
    """Redimensiona/corta a foto para target W x H preservando foco no rosto.
    focus_y=0.3 mantem o rosto visivel quando cortando verticalmente."""
    iw, ih = img.size
    src_ratio = iw / ih
    tgt_ratio = target_w / target_h
    if src_ratio > tgt_ratio:
        # imagem mais larga: corta laterais
        new_w = int(ih * tgt_ratio)
        left = (iw - new_w) // 2
        img = img.crop((left, 0, left + new_w, ih))
    else:
        # imagem mais alta: corta topo/base
        new_h = int(iw / tgt_ratio)
        # Mantem foco no topo (rosto geralmente esta no terco superior)
        top = int((ih - new_h) * focus_y)
        top = max(0, min(top, ih - new_h))
        img = img.crop((0, top, iw, top + new_h))
    return img.resize((target_w, target_h), Image.LANCZOS)


def wrap_text(draw, text: str, font, max_width: int) -> list:
    """Quebra texto em linhas que caibam em max_width."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = f"{cur} {w}".strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def style_classico(base: Image.Image, frase: str, autor: str = None):
    """Gradient escuro em baixo + texto serif + autor. Tipo poster classico."""
    W, H = base.size
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Gradient escuro no terco inferior
    grad_h = int(H * 0.55)
    for y in range(grad_h):
        alpha = int(210 * (y / grad_h) ** 1.8)
        draw.line([(0, H - grad_h + y), (W, H - grad_h + y)], fill=(0, 0, 0, alpha))

    # Texto principal (serif bold)
    font_size = int(H * 0.048)
    font = load_font(FONTS_SERIF, font_size)
    margin = int(W * 0.08)
    max_text_w = W - margin * 2
    lines = wrap_text(draw, f'"{frase}"', font, max_text_w)
    line_h = int(font_size * 1.28)

    # Bloco de texto na parte inferior
    total_h = len(lines) * line_h
    y_text = H - total_h - int(H * 0.10)
    if autor:
        y_text -= int(H * 0.04)

    for i, ln in enumerate(lines):
        bbox = draw.textbbox((0, 0), ln, font=font)
        w = bbox[2] - bbox[0]
        x = (W - w) // 2
        # Sombra
        draw.text((x + 2, y_text + i * line_h + 2), ln, fill=(0, 0, 0, 180), font=font)
        # Texto branco
        draw.text((x, y_text + i * line_h), ln, fill=(255, 255, 255, 255), font=font)

    # Autor
    if autor:
        autor_size = int(font_size * 0.55)
        fa = load_font(FONTS_REG, autor_size)
        ay = y_text + total_h + int(H * 0.018)
        ab = draw.textbbox((0, 0), f"— {autor}", font=fa)
        aw = ab[2] - ab[0]
        ax = (W - aw) // 2
        draw.text((ax, ay), f"— {autor}", fill=(212, 175, 55, 255), font=fa)

    return Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB")


def style_minimalista(base: Image.Image, frase: str, autor: str = None):
    """Texto branco grande no centro, gradient discreto."""
    W, H = base.size
    # Escurecer levemente a imagem
    darkened = ImageEnhance.Brightness(base).enhance(0.65)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    font_size = int(H * 0.065)
    font = load_font(FONTS_BOLD, font_size)
    margin = int(W * 0.1)
    max_text_w = W - margin * 2
    lines = wrap_text(draw, frase, font, max_text_w)
    line_h = int(font_size * 1.2)
    total_h = len(lines) * line_h
    y_start = (H - total_h) // 2

    for i, ln in enumerate(lines):
        bbox = draw.textbbox((0, 0), ln, font=font)
        w = bbox[2] - bbox[0]
        x = (W - w) // 2
        draw.text((x, y_start + i * line_h), ln, fill=(255, 255, 255, 255), font=font)

    if autor:
        asize = int(font_size * 0.45)
        fa = load_font(FONTS_REG, asize)
        ay = y_start + total_h + int(H * 0.03)
        ab = draw.textbbox((0, 0), f"— {autor}", font=fa)
        aw = ab[2] - ab[0]
        draw.text(((W - aw) // 2, ay), f"— {autor}", fill=(212, 175, 55, 255), font=fa)

    return Image.alpha_composite(darkened.convert("RGBA"), overlay).convert("RGB")


def style_cinema(base: Image.Image, frase: str, autor: str = None):
    """Letterbox preto em cima/baixo, texto em serif no rodape."""
    W, H = base.size
    bar_h = int(H * 0.15)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    draw.rectangle([(0, 0), (W, bar_h)], fill=(0, 0, 0, 255))
    draw.rectangle([(0, H - bar_h), (W, H)], fill=(0, 0, 0, 255))

    font_size = int(H * 0.032)
    font = load_font(FONTS_SERIF, font_size)
    margin = int(W * 0.05)
    lines = wrap_text(draw, f'"{frase}"', font, W - margin * 2)
    line_h = int(font_size * 1.25)
    total_h = len(lines) * line_h
    y_start = H - bar_h + (bar_h - total_h) // 2 - int(H * 0.005)

    for i, ln in enumerate(lines):
        bbox = draw.textbbox((0, 0), ln, font=font)
        w = bbox[2] - bbox[0]
        x = (W - w) // 2
        draw.text((x, y_start + i * line_h), ln, fill=(240, 230, 210, 255), font=font)

    if autor:
        asize = int(font_size * 0.7)
        fa = load_font(FONTS_REG, asize)
        at = f"— {autor}"
        ab = draw.textbbox((0, 0), at, font=fa)
        aw = ab[2] - ab[0]
        # Autor discreto no topo
        draw.text(((W - aw) // 2, bar_h // 2 - asize // 2), at, fill=(200, 180, 150, 255), font=fa)

    return Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB")


def style_editorial(base: Image.Image, frase: str, autor: str = None):
    """Caixa semitransparente lateral direita com texto (tipo revista)."""
    W, H = base.size
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    # Caixa lateral direita
    box_w = int(W * 0.42)
    draw.rectangle([(W - box_w, 0), (W, H)], fill=(0, 0, 0, 210))

    font_size = int(H * 0.042)
    font = load_font(FONTS_BOLD, font_size)
    margin = int(box_w * 0.12)
    lines = wrap_text(draw, frase, font, box_w - margin * 2)
    line_h = int(font_size * 1.2)
    y_start = (H - len(lines) * line_h) // 2
    for i, ln in enumerate(lines):
        draw.text((W - box_w + margin, y_start + i * line_h), ln,
                  fill=(255, 255, 255, 255), font=font)
    if autor:
        asize = int(font_size * 0.5)
        fa = load_font(FONTS_REG, asize)
        draw.text((W - box_w + margin, y_start + len(lines) * line_h + int(H * 0.025)),
                  f"— {autor}", fill=(212, 175, 55, 255), font=fa)
    return Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB")


def style_faixa_lateral(base: Image.Image, frase: str, autor: str = None):
    """Barra vertical dourada esquerda + frase ao lado."""
    W, H = base.size
    # Escurece levemente
    darkened = ImageEnhance.Brightness(base).enhance(0.75)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    bar_w = int(W * 0.015)
    # Barra dourada da marca
    draw.rectangle([(int(W * 0.07), int(H * 0.28)), (int(W * 0.07) + bar_w, int(H * 0.72))],
                   fill=(212, 175, 55, 255))

    font_size = int(H * 0.04)
    font = load_font(FONTS_BOLD, font_size)
    x_text = int(W * 0.07) + bar_w + int(W * 0.025)
    max_w = W - x_text - int(W * 0.07)
    lines = wrap_text(draw, frase, font, max_w)
    line_h = int(font_size * 1.3)
    total = len(lines) * line_h
    y_start = (H - total) // 2
    for i, ln in enumerate(lines):
        # Sombra suave
        draw.text((x_text + 2, y_start + i * line_h + 2), ln, fill=(0, 0, 0, 180), font=font)
        draw.text((x_text, y_start + i * line_h), ln, fill=(255, 255, 255, 255), font=font)

    if autor:
        asize = int(font_size * 0.5)
        fa = load_font(FONTS_REG, asize)
        draw.text((x_text, y_start + total + int(H * 0.025)), f"— {autor}",
                  fill=(212, 175, 55, 255), font=fa)
    return Image.alpha_composite(darkened.convert("RGBA"), overlay).convert("RGB")


STYLES = {
    "classico":      style_classico,
    "minimalista":   style_minimalista,
    "cinema":        style_cinema,
    "editorial":     style_editorial,
    "faixa-lateral": style_faixa_lateral,
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--foto", required=True, help="Foto real (JPG/PNG)")
    ap.add_argument("--frase", required=True, help="Frase / quote a ser exibida")
    ap.add_argument("--autor", default=None, help="Atribuicao (opcional)")
    ap.add_argument("--estilo", default="classico", choices=list(STYLES.keys()))
    ap.add_argument("--aspect-ratio", default="4:5", choices=list(ASPECT_SIZES.keys()))
    ap.add_argument("--out", required=True, help="Arquivo de saida (.jpg)")
    ap.add_argument("--focus-y", type=float, default=0.3, help="Foco vertical (0=topo, 1=base)")
    args = ap.parse_args()

    W, H = ASPECT_SIZES[args.aspect_ratio]

    base = Image.open(args.foto).convert("RGB")
    print(f"Foto original: {base.size}")
    base = fit_photo(base, W, H, args.focus_y)
    print(f"Redimensionada para: {base.size}")

    fn = STYLES[args.estilo]
    print(f"Aplicando estilo: {args.estilo}")
    result = fn(base, args.frase, args.autor)

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    result.save(args.out, "JPEG", quality=90, optimize=True)
    size_kb = os.path.getsize(args.out) // 1024
    print(f"✅ {args.out} ({size_kb}KB)")


if __name__ == "__main__":
    main()
