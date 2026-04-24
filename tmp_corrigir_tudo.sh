#!/bin/bash
set -e

echo "=== CORREÇÃO TOTAL DO CARROSSEL ==="
echo ""
echo "1. Usando foto NÃO usada recentemente: Imagem PNG 20.png"
echo "2. Usando avatar correto: /root/avatar_hq.png"
echo "3. Gerando fundo adequado ao tema via Unsplash"
echo ""

# Criar diretório
mkdir -p /root/cerebro-vital-slim/deliverables/glp1-cancer-endometrial/corrigido

echo "=== Gerando capa com foto nova ==="
cd /root/.openclaw/workspace/skills/tweet-carrossel
python3 scripts/compose_cover.py \
  --foto /root/.openclaw/workspace/fotos_dra/originais/Imagem\ PNG\ 20.png \
  --tema "cancer endometrial pesquisa medica laboratorio celulas" \
  --headline "UM REMEDIO PARA EMAGRECER|PODE SALVAR SEU UTERO" \
  --destaques "REMEDIO,EMAGRECER,SALVAR,UTERO" \
  --out /root/cerebro-vital-slim/deliverables/glp1-cancer-endometrial/corrigido/capa.jpg 2>&1

echo ""
echo "=== Regenerando slides 3-10 com avatar correto ==="
cd /root/cerebro-vital-slim/deliverables/glp1-cancer-endometrial/corrigido

python3 << 'PYTHON_EOF'
import sys
sys.path.insert(0, '/root/.openclaw/workspace/skills/tweet-carrossel/scripts')

from make_tweet_slides import make_circular_avatar, get_font, wrap_text, sanitize_text, draw_verified
from PIL import Image, ImageDraw

WHITE = (255, 255, 255)
DARK_TEXT = (30, 30, 30)
GRAY = (100, 100, 100)

W, H = 1080, 1350
MARGIN_L = 64
MARGIN_R = 64
AVATAR_SIZE = 72
NAME_SIZE = 36
HANDLE_SIZE = 30
BODY_SIZE = 40

# AVATAR CORRETO
avatar = make_circular_avatar('/root/avatar_hq.png', AVATAR_SIZE)
font_name = get_font(NAME_SIZE, bold=True)
font_handle = get_font(HANDLE_SIZE)
font_body = get_font(BODY_SIZE)
max_text_w = W - MARGIN_L - MARGIN_R

def measure_block(paragraphs, font_body, font_name, font_handle, max_w):
    d = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    fh_body = d.textbbox((0, 0), "A", font=font_body)[3]
    fh_name = d.textbbox((0, 0), "A", font=font_name)[3]
    fh_handle = d.textbbox((0, 0), "A", font=font_handle)[3]
    lh = int(fh_body * 1.55)
    header_h = max(AVATAR_SIZE, fh_name + 10 + fh_handle)
    body_h = 0
    for i, para in enumerate(paragraphs):
        if i > 0:
            body_h += int(fh_body * 0.6) if para == "" else int(fh_body * 0.9)
        if para == "":
            body_h += int(fh_body * 0.6)
            continue
        body_h += len(wrap_text(para, font_body, max_w)) * lh
    return header_h + 36 + body_h, lh, fh_body, fh_name, fh_handle

def make_slide_custom(paragraphs, out_path, bg_color, text_color, avatar_img,
                      name="Dra Daniely Freitas", handle="@dradaniely.freitas",
                      show_verified=True):
    paragraphs = [sanitize_text(p) for p in paragraphs]
    total_h, lh, fh_body, fh_name, fh_handle = measure_block(
        paragraphs, font_body, font_name, font_handle, max_text_w)
    y_start = max(60, (H - total_h) // 2 - 30)
    if total_h < H * 0.6:
        y_start = max(80, (H - total_h) // 2 - 80)
    y_start = max(60, min(y_start, 250))
    
    img = Image.new("RGB", (W, H), bg_color)
    av = avatar_img.convert("RGBA")
    img_rgba = img.convert("RGBA")
    img_rgba.paste(av, (MARGIN_L, y_start), av)
    img = img_rgba.convert("RGB")
    draw = ImageDraw.Draw(img)
    
    x_text = MARGIN_L + AVATAR_SIZE + 16
    y_name = y_start + (AVATAR_SIZE - fh_name - 10 - fh_handle) // 2
    draw.text((x_text, y_name), name, font=font_name, fill=text_color)
    
    if show_verified:
        name_w = draw.textbbox((x_text, y_name), name, font=font_name)[2] - x_text
        draw_verified(draw, x_text + name_w + 8, y_name + (fh_name - 18) // 2, 18)
    
    y_handle = y_name + fh_name + 6
    handle_color = GRAY if bg_color == WHITE else (140, 150, 145)
    draw.text((x_text, y_handle), handle, font=font_handle, fill=handle_color)
    
    y_body = y_start + max(AVATAR_SIZE, fh_name + 10 + fh_handle) + 36
    for i, para in enumerate(paragraphs):
        if i > 0:
            y_body += int(fh_body * 0.6) if para == "" else int(fh_body * 0.9)
        if para == "":
            y_body += int(fh_body * 0.6)
            continue
        for line in wrap_text(para, font_body, max_text_w):
            draw.text((MARGIN_L, y_body), line, font=font_body, fill=text_color)
            y_body += lh
    
    img.save(out_path)
    print(f"  ✓ {out_path}")

slides_data = [
  {"num": 3, "paragraphs": ["A progestina é o tratamento padrão para proteger o útero. Mas em pacientes com obesidade, o tumor simplesmente não ouve o medicamento."]},
  {"num": 4, "paragraphs": ["O que descobriram: os remédios da classe GLP-1 fazem duas coisas ao mesmo tempo. Emagrecem E aumentam os receptores de progesterona no tumor."]},
  {"num": 5, "paragraphs": ["É como se o GLP-1 ressuscitasse os receptores que a obesidade tinha silenciado. Aí a progestina consegue se ligar e eliminar a célula cancerígena."]},
  {"num": 6, "paragraphs": ["Os números são impressionantes. Estudo com 165 milhões de pacientes mostrou:", "", "Mulheres até 45 anos com câncer endometrial:", "→ Apenas progestina: 23% precisaram de cirurgia em 18 meses", "→ GLP-1 + progestina: apenas 10%", "", "Redução de 59% no risco de perder o útero", "Fonte: TriNetX (2017-2025)"]},
  {"num": 7, "paragraphs": ["E funciona até nos casos mais difíceis:", "", "Mulheres com menos de 40 anos:", "→ Antes: 21% de cirurgias", "→ Depois: 9%", "", "Câncer invasivo confirmado:", "→ Antes: 30%", "→ Depois: 12%", "", "Fonte: Podder et al., CCR 2026"]},
  {"num": 8, "paragraphs": ["O que isso significa para você:", "", "→ Se usa GLP-1 + terapia hormonal, o efeito pode ser sinérgico", "→ Seu endométrio pode ficar mais sensível", "→ Na reposição hormonal futura, talvez doses menores de progesterona sejam suficientes", "", "A medicina personalizada está chegando."]},
  {"num": 9, "paragraphs": ["Cada organismo é único. Seu metabolismo, seus hormônios, sua história.", "", "Na Vital Slim, tratamos a raiz, não apenas o sintoma."]},
  {"num": 10, "paragraphs": ["Comenta AVALIAÇÃO para agendar sua consulta com a Dra. Daniely Freitas."]}
]

for slide in slides_data:
    out_path = f"/root/cerebro-vital-slim/deliverables/glp1-cancer-endometrial/corrigido/slide_{slide['num']:02d}.png"
    make_slide_custom(slide['paragraphs'], out_path, WHITE, DARK_TEXT, avatar)

print("\n✅ Todos os slides corrigidos gerados!")
PYTHON_EOF

echo ""
echo "=== Renomeando e verificando ==="
mv capa.jpg slide_01.jpg
cp /root/cerebro-vital-slim/deliverables/glp1-cancer-endometrial/refazer/pubmed.png slide_02.png
ls -la /root/cerebro-vital-slim/deliverables/glp1-cancer-endometrial/corrigido/
