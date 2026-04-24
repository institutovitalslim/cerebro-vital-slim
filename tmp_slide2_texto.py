#!/usr/bin/env python3
from PIL import Image, ImageDraw
import sys
sys.path.insert(0, '/root/.openclaw/workspace/skills/tweet-carrossel/scripts')
from make_tweet_slides import make_circular_avatar, get_font, wrap_text, draw_verified

W, H = 1080, 1350
WHITE = (255, 255, 255)
DARK_TEXT = (30, 30, 30)
GRAY = (100, 100, 100)

MARGIN_L = 64
MARGIN_R = 64
AVATAR_SIZE = 72
NAME_SIZE = 36
HANDLE_SIZE = 30
BODY_SIZE = 46  # Aumentado de 40 para 46

avatar = make_circular_avatar('/root/avatar_hq.png', AVATAR_SIZE)
font_name = get_font(NAME_SIZE, bold=True)
font_handle = get_font(HANDLE_SIZE)
font_body = get_font(BODY_SIZE)
max_text_w = W - MARGIN_L - MARGIN_R

# Criar imagem
img = Image.new("RGB", (W, H), WHITE)
draw = ImageDraw.Draw(img)

# Header com avatar
av = avatar.convert("RGBA")
img_rgba = img.convert("RGBA")
img_rgba.paste(av, (MARGIN_L, 60), av)
img = img_rgba.convert("RGB")
draw = ImageDraw.Draw(img)

# Nome
fh_name = draw.textbbox((0, 0), "A", font=font_name)[3]
fh_handle = draw.textbbox((0, 0), "A", font=font_handle)[3]
x_text = MARGIN_L + AVATAR_SIZE + 16
y_name = 60 + (AVATAR_SIZE - fh_name - 10 - fh_handle) // 2
draw.text((x_text, y_name), "Dra Daniely Freitas", font=font_name, fill=DARK_TEXT)
name_w = draw.textbbox((x_text, y_name), "Dra Daniely Freitas", font=font_name)[2] - x_text
draw_verified(draw, x_text + name_w + 8, y_name + (fh_name - 18) // 2, 18)

y_handle = y_name + fh_name + 6
draw.text((x_text, y_handle), "@dradaniely.freitas", font=font_handle, fill=GRAY)

# Texto do slide - APENAS TEXTO, sem imagem
y_body = 60 + max(AVATAR_SIZE, fh_name + 10 + fh_handle) + 50
paragraphs = [
    "O câncer do endométrio cresce 4,5% ao ano entre mulheres jovens. A obesidade é o principal fator de risco.",
    "",
    "Mas e se o remédio que emagrece também protegesse?",
    "",
    "Um estudo publicado no Clinical Cancer Research mostra que o GLP-1 não só emagrece: ele aumenta a expressão dos receptores de progesterona no tumor, permitindo que a progestina atue onde antes falhava.",
    "",
    "Fonte: Podder et al., CCR 2026; DOI: 10.1158/1078-0432.CCR-25-2819"
]

fh_body = draw.textbbox((0, 0), "A", font=font_body)[3]
lh = int(fh_body * 1.6)

for i, para in enumerate(paragraphs):
    if i > 0:
        y_body += int(fh_body * 0.6) if para == "" else int(fh_body * 0.9)
    if para == "":
        y_body += int(fh_body * 0.6)
        continue
    for line in wrap_text(para, font_body, max_text_w):
        draw.text((MARGIN_L, y_body), line, font=font_body, fill=DARK_TEXT)
        y_body += lh

# Salvar
out_path = '/root/cerebro-vital-slim/deliverables/glp1-cancer-endometrial/corrigido/slide_02.png'
img.save(out_path)
print(f"✓ Slide 2 (apenas texto): {out_path}")
