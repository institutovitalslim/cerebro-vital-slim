#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont
import sys
sys.path.insert(0, '/root/.openclaw/workspace/skills/tweet-carrossel/scripts')
from make_tweet_slides import make_circular_avatar, get_font

# Configurações
W, H = 1080, 1350
BG_COLOR = (0, 0, 0)  # Preto
GOLD = (212, 175, 55)  # Dourado
WHITE = (255, 255, 255)

# Criar imagem base
img = Image.new("RGB", (W, H), BG_COLOR)
draw = ImageDraw.Draw(img)

# Carregar foto da Dra. (ainda não usada)
foto_path = '/root/.openclaw/workspace/fotos_dra/originais/Imagem PNG 20.png'
foto = Image.open(foto_path)

# Remover fundo da foto (usar rembg se disponível)
try:
    from rembg import remove
    foto_nobg = remove(foto)
    foto_nobg.save('/tmp/foto_nobg.png')
    foto = Image.open('/tmp/foto_nobg.png')
except Exception as e:
    print(f"rembg não disponível, usando foto original: {e}")

# Redimensionar foto para caber na parte superior
foto_w, foto_h = foto.size
ratio = min(W / foto_w, (H * 0.55) / foto_h)
new_w = int(foto_w * ratio)
new_h = int(foto_h * ratio)
foto_resized = foto.resize((new_w, new_h), Image.LANCZOS)

# Colar foto (centralizar horizontalmente)
x_foto = (W - new_w) // 2
img.paste(foto_resized, (x_foto, 0), foto_resized if foto.mode == 'RGBA' else None)

# Desenhar linha dourada decorativa abaixo da foto
y_line = new_h + 20
draw.line([(80, y_line), (W-80, y_line)], fill=GOLD, width=2)

# Logo "V" estilizado no centro
y_logo = y_line + 30
# Desenhar V simples
v_points = [
    (W//2 - 15, y_logo),
    (W//2, y_logo + 30),
    (W//2 + 15, y_logo)
]
draw.line(v_points, fill=GOLD, width=3)

# Headline MAIOR para preencher espaço
y_text_start = y_logo + 60

# Palavras a serem destacadas em dourado
headline_words = [
    ("UM ", WHITE),
    ("REMÉDIO", GOLD),
    (" PARA ", WHITE),
    ("EMAGRECER", GOLD),
]
line2_words = [
    ("PODE ", WHITE),
    ("SALVAR", GOLD),
    (" SEU ", WHITE),
    ("ÚTERO", GOLD),
]

# Fonte maior
font_headline = get_font(56, bold=True)
font_headline2 = get_font(52, bold=True)

# Desenhar linha 1
x_pos = 80
total_w = 0
for word, color in headline_words:
    bbox = draw.textbbox((0, 0), word, font=font_headline)
    total_w += bbox[2] - bbox[0]

x_pos = (W - total_w) // 2
for word, color in headline_words:
    bbox = draw.textbbox((0, 0), word, font=font_headline)
    draw.text((x_pos, y_text_start), word, font=font_headline, fill=color)
    x_pos += bbox[2] - bbox[0]

# Desenhar linha 2
y_line2 = y_text_start + 70
total_w2 = 0
for word, color in line2_words:
    bbox = draw.textbbox((0, 0), word, font=font_headline2)
    total_w2 += bbox[2] - bbox[0]

x_pos2 = (W - total_w2) // 2
for word, color in line2_words:
    bbox = draw.textbbox((0, 0), word, font=font_headline2)
    draw.text((x_pos2, y_line2), word, font=font_headline2, fill=color)
    x_pos2 += bbox[2] - bbox[0]

# Linha decorativa abaixo do texto
y_bottom_line = y_line2 + 80
draw.line([(120, y_bottom_line), (W-120, y_bottom_line)], fill=GOLD, width=1)

# CRM na parte inferior
font_crm = get_font(22)
crm_text = "Dra. Daniely Freitas  |  CRM-BA 27588"
bbox_crm = draw.textbbox((0, 0), crm_text, font=font_crm)
crm_w = bbox_crm[2] - bbox_crm[0]
draw.text(((W - crm_w) // 2, H - 50), crm_text, font=font_crm, fill=(180, 180, 180))

# Salvar
out_path = '/root/cerebro-vital-slim/deliverables/glp1-cancer-endometrial/corrigido/slide_01_CORRIGIDA.jpg'
img.save(out_path, quality=95)
print(f"✓ Capa corrigida: {out_path}")
