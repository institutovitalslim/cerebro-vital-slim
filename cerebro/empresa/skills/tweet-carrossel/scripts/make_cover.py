#!/usr/bin/env python3
"""
make_cover.py — Gera capa de carrossel no padrao aprovado do Instituto Vital Slim.

Uso:
    python3 make_cover.py \
        --foto foto_dra.png \
        --circulo capsulas.png \
        --headline "SEU MAGNESIO ESTA|'NORMAL'|MAS SEU CORPO|DISCORDA." \
        --destaques "MAGNESIO,NORMAL,DISCORDA." \
        --out capa.png

    # Palavras em dourado separadas por virgula em --destaques
    # Linhas da headline separadas por | (pipe)
    # A foto da Dra deve ter fundo contextual (lab, clinica, etc.)
    # A foto do circulo deve ter contexto do tema (capsulas, alimentos, etc.)
"""

import argparse
import os
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ── Constants ──
W, H = 1080, 1350
BG_COLOR = (0, 0, 0)
WHITE = (255, 255, 255)
GOLD = (159, 136, 68)  # #9F8844
GOLD_LINE = (159, 136, 68, 180)
GRAY_TEXT = (180, 180, 180)

# Layout proportions
PHOTO_HEIGHT_RATIO = 0.58  # Photo occupies top 58%
TEXT_AREA_START = 0.62     # Text area starts at 62% (menos espaço vazio)
CIRCLE_SIZE = 120          # Circle inset size
CIRCLE_MARGIN = 30         # Margin from top-right
CIRCLE_BORDER = 4          # Gold border width
LINE_Y_RATIO = 0.59        # Gold divider line position (mais próximo do texto)
V_SIZE = 20                # V symbol size

# Font paths (try multiple locations)
FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/root/.openclaw/workspace/skills/tweet-carrossel/assets/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
]

FONT_REG_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/root/.openclaw/workspace/skills/tweet-carrossel/assets/DejaVuSans.ttf",
]

FOOTER_TEXT = "Dra. Daniely Freitas  |  CRM-BA 27588"

# Try to find Montserrat (preferred)
MONTSERRAT_PATHS = [
    "/usr/share/fonts/truetype/montserrat/Montserrat-Black.ttf",
    "/root/.openclaw/workspace/fonts/Montserrat-Black.ttf",
    "/usr/local/share/fonts/Montserrat-Black.ttf",
]


def find_font(paths, fallback_size=48):
    for p in paths:
        if os.path.isfile(p):
            return p
    return None


def load_font(paths, size):
    path = find_font(paths)
    if path:
        return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def make_circle_mask(size):
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size - 1, size - 1), fill=255)
    return mask


def add_circle_inset(canvas, circle_img_path):
    """Add circular inset image in top-right corner with gold border."""
    circle_img = Image.open(circle_img_path).convert("RGBA")

    # Resize to circle size
    inner_size = CIRCLE_SIZE - CIRCLE_BORDER * 2
    circle_img = circle_img.resize((inner_size, inner_size), Image.LANCZOS)

    # Create circular mask
    mask = make_circle_mask(inner_size)

    # Create gold border circle
    border_img = Image.new("RGBA", (CIRCLE_SIZE, CIRCLE_SIZE), (0, 0, 0, 0))
    border_draw = ImageDraw.Draw(border_img)
    border_draw.ellipse((0, 0, CIRCLE_SIZE - 1, CIRCLE_SIZE - 1), fill=(*GOLD, 255))

    # Paste inner image onto border
    offset = CIRCLE_BORDER
    border_img.paste(circle_img, (offset, offset), mask)

    # Position in top-right
    x = W - CIRCLE_SIZE - CIRCLE_MARGIN
    y = CIRCLE_MARGIN
    canvas.paste(border_img, (x, y), border_img)


def add_gold_line(canvas):
    """Add horizontal gold divider line with real V symbol."""
    draw = ImageDraw.Draw(canvas)
    y = int(H * LINE_Y_RATIO)
    margin = 40

    # Symbol V real da marca - busca em múltiplos caminhos
    SYMBOL_CANDIDATES = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "simbolo_v.png"),
        "/root/.openclaw/workspace/skills/tweet-carrossel/assets/simbolo_v.png",
        "/root/cerebro-vital-slim/cerebro/empresa/skills/tweet-carrossel/assets/simbolo_v.png",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "simbolo_v.png"),
    ]
    SYMBOL_PATH = next((p for p in SYMBOL_CANDIDATES if os.path.isfile(p)), None)
    SYMBOL_SIZE = 120  # Tamanho do simbolo V

    if SYMBOL_PATH:
        # Load symbol
        symbol = Image.open(SYMBOL_PATH).convert("RGBA")
        symbol = symbol.resize((SYMBOL_SIZE, SYMBOL_SIZE), Image.LANCZOS)

        # Center position
        cx = W // 2
        sym_x = cx - SYMBOL_SIZE // 2
        sym_y = y - SYMBOL_SIZE // 2

        # Draw lines on both sides of symbol (with gap for symbol)
        gap = SYMBOL_SIZE // 2 + 10
        draw.line([(margin, y), (cx - gap, y)], fill=GOLD_LINE, width=2)
        draw.line([(cx + gap, y), (W - margin, y)], fill=GOLD_LINE, width=2)

        # Paste symbol
        canvas.paste(symbol, (sym_x, sym_y), symbol)
    else:
        # Fallback: full line with text V
        draw.line([(margin, y), (W - margin, y)], fill=GOLD_LINE, width=2)
        v_font = load_font(FONT_REG_PATHS, 24)
        draw.text((W // 2, y - 14), "V", fill=(*GOLD, 200), font=v_font, anchor="mt")


def render_headline(draw, headline_lines, highlight_words, start_y):
    """Render headline with mixed white/gold colors."""
    # Find best font
    montserrat = find_font(MONTSERRAT_PATHS)
    if montserrat:
        font_path = montserrat
    else:
        font_path = find_font(FONT_PATHS)

    # Calculate font size to fit - prefer larger text to fill space
    num_lines = len(headline_lines)
    max_font_size = min(160, int((H - start_y - 20) / (num_lines * 1.05)))

    # Try to find the best font size
    font_size = max_font_size
    while font_size > 30:
        font = ImageFont.truetype(font_path, font_size) if font_path else ImageFont.load_default()
        max_width = max(draw.textlength(line, font=font) for line in headline_lines)
        if max_width <= W - 30:  # margem mínima 15px cada lado
            break
        font_size -= 2

    font = ImageFont.truetype(font_path, font_size) if font_path else ImageFont.load_default()
    line_height = int(font_size * 1.05)  # bem tight pra ocupar mais texto

    # Calculate total text block height
    total_height = num_lines * line_height

    # Alinhar texto próximo ao topo da área (logo após a linha dourada)
    # para eliminar espaço vazio entre linha e texto
    y_offset = start_y + 10

    highlight_set = set(w.strip().upper() for w in highlight_words)

    for i, line in enumerate(headline_lines):
        y = y_offset + i * line_height

        # Render word-by-word with individual color highlighting
        words = line.split(" ")

        # Calculate total line width first (for centering)
        total_line_width = draw.textlength(line, font=font)
        x_cursor = (W - total_line_width) // 2

        for j, word in enumerate(words):
            # Check if this specific word should be gold
            word_clean = word.strip().upper().strip('"').strip("'").strip(",").strip(".")
            is_gold = word_clean in highlight_set
            color = GOLD if is_gold else WHITE

            draw.text((x_cursor, y), word, fill=color, font=font)
            word_width = draw.textlength(word + " ", font=font)
            x_cursor += word_width


def add_footer(draw):
    """Add footer with doctor name and CRM."""
    font = load_font(FONT_REG_PATHS, 18)
    y = H - 40
    bbox = draw.textbbox((0, 0), FOOTER_TEXT, font=font)
    text_width = bbox[2] - bbox[0]
    x = (W - text_width) // 2
    draw.text((x, y), FOOTER_TEXT, fill=GRAY_TEXT, font=font)


def build_cover(foto_path, circulo_path, headline_lines, highlight_words, output_path):
    """Build the complete cover image."""
    # Create canvas
    canvas = Image.new("RGB", (W, H), BG_COLOR)

    # Load and place photo
    photo = Image.open(foto_path).convert("RGB")
    photo_h = int(H * PHOTO_HEIGHT_RATIO)

    # Resize photo to fill width, crop to height
    photo_ratio = photo.width / photo.height
    target_ratio = W / photo_h

    if photo_ratio > target_ratio:
        # Photo is wider - fit by height
        new_h = photo_h
        new_w = int(photo_h * photo_ratio)
    else:
        # Photo is taller - fit by width
        new_w = W
        new_h = int(W / photo_ratio)

    photo = photo.resize((new_w, new_h), Image.LANCZOS)

    # Center crop
    left = (new_w - W) // 2
    top = 0
    photo = photo.crop((left, top, left + W, top + photo_h))

    # Add gradient fade at bottom of photo
    gradient = Image.new("RGBA", (W, photo_h), (0, 0, 0, 0))
    gradient_draw = ImageDraw.Draw(gradient)
    fade_start = int(photo_h * 0.6)
    for y in range(fade_start, photo_h):
        alpha = int(255 * (y - fade_start) / (photo_h - fade_start))
        gradient_draw.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))

    photo_rgba = photo.convert("RGBA")
    photo_rgba = Image.alpha_composite(photo_rgba, gradient)
    canvas.paste(photo_rgba.convert("RGB"), (0, 0))

    # Add circle inset
    if circulo_path and os.path.isfile(circulo_path):
        canvas_rgba = canvas.convert("RGBA")
        add_circle_inset(canvas_rgba, circulo_path)
        canvas = canvas_rgba.convert("RGB")

    # Gold divider line + V symbol
    add_gold_line(canvas)

    # Draw overlay elements
    draw = ImageDraw.Draw(canvas)

    # Headline
    text_start_y = int(H * TEXT_AREA_START)
    render_headline(draw, headline_lines, highlight_words, text_start_y)

    # Footer
    add_footer(draw)

    # Save as JPEG (compressed) to stay under Claude's 20MB limit
    if output_path.lower().endswith('.png'):
        output_path = output_path[:-4] + '.jpg'
    canvas.save(output_path, "JPEG", quality=85, optimize=True)
    print(f"Cover saved: {output_path} ({W}x{H}) [JPEG]")


def main():
    parser = argparse.ArgumentParser(description="Gera capa de carrossel IVS")
    parser.add_argument("--foto", required=True, help="Foto da Dra. com fundo contextual")
    parser.add_argument("--circulo", default=None, help="Imagem para o circulo inset (canto superior direito)")
    parser.add_argument("--headline", required=True, help="Texto da headline. Separe linhas com | (pipe)")
    parser.add_argument("--destaques", default="", help="Palavras em dourado, separadas por virgula")
    parser.add_argument("--out", default="capa.jpg", help="Caminho do arquivo de saida")
    args = parser.parse_args()

    headline_lines = [line.strip() for line in args.headline.split("|")]
    highlight_words = [w.strip() for w in args.destaques.split(",") if w.strip()]

    build_cover(args.foto, args.circulo, headline_lines, highlight_words, args.out)


if __name__ == "__main__":
    main()
