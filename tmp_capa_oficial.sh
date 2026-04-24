#!/bin/bash
# Gerar capa usando make_cover.py oficial

cd /root/.openclaw/workspace/skills/tweet-carrossel

# Primeiro compor foto + fundo contextual
python3 << 'PYTHON_EOF'
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

# Carregar foto da Dra.
foto = Image.open('/root/.openclaw/workspace/fotos_dra/originais/Imagem PNG 20.png')

# Criar fundo contextual escuro (laboratório/pesquisa)
W, H = 1080, 1350
fundo = Image.new("RGB", (W, H), (15, 15, 20))
draw = ImageDraw.Draw(fundo)

# Adicionar elementos sutis de laboratório
# Linhas horizontais sutis
for y in range(0, H, 80):
    draw.line([(0, y), (W, y)], fill=(25, 25, 35), width=1)

# Círculos sutis (representando células/microscópio)
for cx, cy, r in [(200, 300, 150), (800, 500, 200), (400, 900, 180)]:
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=(30, 30, 45), width=2)

# Gradiente escuro no topo
for y in range(int(H * 0.6)):
    alpha = int(255 * (1 - y / (H * 0.6)))
    draw.line([(0, y), (W, y)], fill=(alpha, alpha, alpha + 10))

fundo.save('/tmp/fundo_contextual.jpg')
print("✓ Fundo contextual criado")

# Remover fundo da foto e compor sobre fundo
try:
    from rembg import remove
    foto_nobg = remove(foto)
    foto_nobg.save('/tmp/foto_nobg.png')
    
    # Redimensionar foto
    foto_w, foto_h = foto_nobg.size
    target_h = int(H * 0.58)
    ratio = target_h / foto_h
    new_w = int(foto_w * ratio)
    new_h = target_h
    foto_resized = foto_nobg.resize((new_w, new_h), Image.LANCZOS)
    
    # Centralizar horizontalmente
    x_offset = (W - new_w) // 2
    y_offset = 0
    
    fundo_rgba = fundo.convert("RGBA")
    fundo_rgba.paste(foto_resized, (x_offset, y_offset), foto_resized)
    fundo_rgba.convert("RGB").save('/tmp/foto_composta.jpg', quality=95)
    print("✓ Foto composta sobre fundo")
except Exception as e:
    print(f"rembg erro: {e}")
    # Fallback: usar foto original
    foto.save('/tmp/foto_composta.jpg', quality=95)
    print("✓ Usando foto original (fallback)")
PYTHON_EOF

# Agora gerar capa com make_cover.py oficial
python3 scripts/make_cover.py \
  --foto /tmp/foto_composta.jpg \
  --headline "UM REMEDIO PARA EMAGRECER|PODE SALVAR SEU UTERO" \
  --destaques "REMEDIO,EMAGRECER,SALVAR,UTERO" \
  --out /root/cerebro-vital-slim/deliverables/glp1-cancer-endometrial/corrigido/slide_01_OFICIAL.jpg 2>&1
