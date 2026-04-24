#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont
import sys
sys.path.insert(0, '/root/.openclaw/workspace/skills/tweet-carrossel/scripts')
from make_tweet_slides import make_circular_avatar, get_font, wrap_text, sanitize_text, draw_verified

W, H = 1080, 1350
WHITE = (255, 255, 255)
DARK_TEXT = (30, 30, 30)
GRAY = (100, 100, 100)

MARGIN_L = 64
MARGIN_R = 64
AVATAR_SIZE = 72
NAME_SIZE = 36
HANDLE_SIZE = 30
BODY_SIZE = 40

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

# Texto do slide
y_body = 60 + max(AVATAR_SIZE, fh_name + 10 + fh_handle) + 40
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
lh = int(fh_body * 1.55)

for i, para in enumerate(paragraphs):
    if i > 0:
        y_body += int(fh_body * 0.6) if para == "" else int(fh_body * 0.9)
    if para == "":
        y_body += int(fh_body * 0.6)
        continue
    for line in wrap_text(para, font_body, max_text_w):
        draw.text((MARGIN_L, y_body), line, font=font_body, fill=DARK_TEXT)
        y_body += lh

# Adicionar recorte da capa do paper
pubmed = Image.open('/root/cerebro-vital-slim/deliverables/glp1-cancer-endometrial/corrigido/pubmed_correct.png')
# Recortar apenas a área da capa do paper (header + título + autores)
w, h = pubmed.size
# Recortar a parte superior onde está o conteúdo do paper
crop_area = (0, 0, w, min(h, 500))
paper_crop = pubmed.crop(crop_area)

# Redimensionar para caber no slide
max_paper_w = W - MARGIN_L - MARGIN_R
paper_ratio = max_paper_w / paper_crop.size[0]
new_paper_h = int(paper_crop.size[1] * paper_ratio)
paper_resized = paper_crop.resize((max_paper_w, new_paper_h), Image.LANCZOS)

# Calcular posição Y para a imagem (após o texto)
y_paper = y_body + 40
if y_paper + new_paper_h > H - 60:
    # Se não cabe, ajustar
    available_h = H - 60 - y_paper
    if available_h < 100:
        # Se não há espaço suficiente, reduzir texto ou imagem
        pass
    else:
        ratio = available_h / new_paper_h
        new_w = int(max_paper_w * ratio)
        paper_resized = paper_crop.resize((new_w, available_h), Image.LANCZOS)
        new_paper_h = available_h

# Centralizar horizontalmente
x_paper = MARGIN_L

# Colar imagem do paper
img.paste(paper_resized, (x_paper, y_paper))

# Salvar
out_path = '/root/cerebro-vital-slim/deliverables/glp1-cancer-endometrial/corrigido/slide_02_CORRETO.png'
img.save(out_path)
print(f"✓ Slide 2 correto gerado: {out_path}")
