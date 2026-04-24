#!/usr/bin/env python3
"""
Regenerar slides 3-10 com centralização vertical correta
e fonte consistente conforme SKILL.md v4
"""

from PIL import Image, ImageDraw, ImageFont
import os, sys

sys.path.insert(0, '/root/.openclaw/workspace/skills/tweet-carrossel/scripts')
from make_tweet_slides import make_circular_avatar, wrap_text, draw_verified

# ── Constants conforme SKILL.md v4 ──
W, H = 1080, 1350
WHITE = (255, 255, 255)
DARK_TEXT = (30, 30, 30)
GRAY = (113, 118, 123)  # #71767b

MARGIN_L = 64
MARGIN_R = 64
AVATAR_SIZE = 96

# Font paths
MONTSERRAT = "/usr/local/share/fonts/Montserrat-Black.ttf"
if not os.path.isfile(MONTSERRAT):
    MONTSERRAT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

REG_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
if not os.path.isfile(REG_FONT):
    REG_FONT = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"

# Font sizes conforme SKILL.md
NAME_SIZE = 58
HANDLE_SIZE = 41
BODY_SIZE = 60

avatar = make_circular_avatar('/root/avatar_hq.png', AVATAR_SIZE)
font_name = ImageFont.truetype(MONTSERRAT, NAME_SIZE)
font_handle = ImageFont.truetype(REG_FONT, HANDLE_SIZE)
font_body = ImageFont.truetype(REG_FONT, BODY_SIZE)

max_text_w = W - MARGIN_L - MARGIN_R

def measure_content(paragraphs):
    """Mede altura total do conteúdo."""
    d = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    fh_name = d.textbbox((0, 0), "A", font=font_name)[3]
    fh_handle = d.textbbox((0, 0), "A", font=font_handle)[3]
    fh_body = d.textbbox((0, 0), "A", font=font_body)[3]
    
    # Header height
    header_h = max(AVATAR_SIZE, fh_name + 10 + fh_handle)
    
    # Body height
    line_height = int(fh_body * 1.28)
    para_gap = 36  # margin-bottom entre parágrafos
    empty_gap = int(fh_body * 0.6)
    
    body_h = 0
    for i, para in enumerate(paragraphs):
        if i > 0:
            body_h += empty_gap if para == "" else para_gap
        if para == "":
            continue
        lines = wrap_text(para, font_body, max_text_w)
        body_h += len(lines) * line_height
    
    # Gap entre header e body
    gap_header_body = 50
    
    total_h = header_h + gap_header_body + body_h
    return total_h, header_h, line_height, para_gap, empty_gap

def make_slide_vcenter(paragraphs, out_path):
    paragraphs = [p for p in paragraphs]
    
    # Medir altura total
    total_h, header_h, line_height, para_gap, empty_gap = measure_content(paragraphs)
    
    # Centralizar verticalmente
    y_start = (H - total_h) // 2
    y_start = max(60, y_start)  # Mínimo 60px do topo
    
    # Criar imagem
    img = Image.new("RGB", (W, H), WHITE)
    
    # Header com avatar
    av = avatar.convert("RGBA")
    img_rgba = img.convert("RGBA")
    img_rgba.paste(av, (MARGIN_L, y_start), av)
    img = img_rgba.convert("RGB")
    draw = ImageDraw.Draw(img)
    
    # Nome e handle
    x_text = MARGIN_L + AVATAR_SIZE + 28  # gap de 28px conforme SKILL
    fh_name = draw.textbbox((0, 0), "A", font=font_name)[3]
    fh_handle = draw.textbbox((0, 0), "A", font=font_handle)[3]
    
    y_name = y_start + (AVATAR_SIZE - fh_name - 10 - fh_handle) // 2
    draw.text((x_text, y_name), "Dra Daniely Freitas", font=font_name, fill=DARK_TEXT)
    
    # Verified badge
    name_w = draw.textbbox((x_text, y_name), "Dra Daniely Freitas", font=font_name)[2] - x_text
    draw_verified(draw, x_text + name_w + 12, y_name + (fh_name - 38) // 2, 38)
    
    y_handle = y_name + fh_name + 6
    draw.text((x_text, y_handle), "@dradaniely.freitas", font=font_handle, fill=GRAY)
    
    # Body
    y_body = y_start + header_h + 50
    
    for i, para in enumerate(paragraphs):
        if i > 0:
            y_body += empty_gap if para == "" else para_gap
        if para == "":
            continue
        lines = wrap_text(para, font_body, max_text_w)
        for line in lines:
            draw.text((MARGIN_L, y_body), line, font=font_body, fill=DARK_TEXT)
            y_body += line_height
    
    img.save(out_path, "PNG")
    print(f"  ✓ {out_path}")

# ── Dados dos slides ──
slides_data = [
    {"num": 3, "paragraphs": [
        "A progestina é o tratamento padrão para proteger o útero.",
        "Mas em pacientes com obesidade, o tumor simplesmente não ouve o medicamento."
    ]},
    {"num": 4, "paragraphs": [
        "O que descobriram: os remédios da classe GLP-1 fazem duas coisas ao mesmo tempo.",
        "",
        "Emagrecem E aumentam os receptores de progesterona no tumor."
    ]},
    {"num": 5, "paragraphs": [
        "É como se o GLP-1 ressuscitasse os receptores que a obesidade tinha silenciado.",
        "",
        "Aí a progestina consegue se ligar e eliminar a célula cancerígena."
    ]},
    {"num": 6, "paragraphs": [
        "Os números são impressionantes.",
        "",
        "Estudo com 165 milhões de pacientes mostrou:",
        "",
        "Mulheres até 45 anos com câncer endometrial:",
        "→ Apenas progestina: 23% precisaram de cirurgia em 18 meses",
        "→ GLP-1 + progestina: apenas 10%",
        "",
        "Redução de 59% no risco de perder o útero",
        "Fonte: TriNetX (2017-2025)"
    ]},
    {"num": 7, "paragraphs": [
        "E funciona até nos casos mais difíceis:",
        "",
        "Mulheres com menos de 40 anos:",
        "→ Antes: 21% de cirurgias",
        "→ Depois: 9%",
        "",
        "Câncer invasivo confirmado:",
        "→ Antes: 30%",
        "→ Depois: 12%",
        "",
        "Fonte: Podder et al., CCR 2026"
    ]},
    {"num": 8, "paragraphs": [
        "O que isso significa para você:",
        "",
        "→ Se usa GLP-1 + terapia hormonal, o efeito pode ser sinérgico",
        "→ Seu endométrio pode ficar mais sensível",
        "→ Na reposição hormonal futura, talvez doses menores de progesterona sejam suficientes",
        "",
        "A medicina personalizada está chegando."
    ]},
    {"num": 9, "paragraphs": [
        "Cada organismo é único.",
        "",
        "Seu metabolismo, seus hormônios, sua história.",
        "",
        "Na Vital Slim, tratamos a raiz, não apenas o sintoma."
    ]},
    {"num": 10, "paragraphs": [
        "Comenta AVALIAÇÃO para agendar sua consulta com a Dra. Daniely Freitas."
    ]}
]

print("Regenerando slides 3-10 com centralização vertical...")
for slide in slides_data:
    out_path = f"/root/cerebro-vital-slim/deliverables/glp1-cancer-endometrial/corrigido/slide_{slide['num']:02d}.png"
    make_slide_vcenter(slide['paragraphs'], out_path)

print("\n✅ Todos os slides regenerados!")
