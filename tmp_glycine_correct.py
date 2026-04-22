#!/usr/bin/env python3
"""Gerar carrossel GLICINA corretamente - copy original aprovada + skill tweet-carrossel."""

from pathlib import Path
import subprocess
import json
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = Path('/root/cerebro-vital-slim/deliverables/glicina-carrossel-correto-2026-04-22')
OUT.mkdir(parents=True, exist_ok=True)

# ── Paths ──
MAKE_COVER = '/root/.openclaw/workspace/skills/tweet-carrossel/scripts/make_cover.py'
AVATAR = '/root/avatar_hq.png'  # Avatar oficial com frame dourado
FOTO = '/root/.openclaw/workspace/fotos_dra/originais/Imagem PNG 124.png'

# ── CAPA (Slide 1) ──
# Copy original aprovada:
# Headline: A MAIORIA|DOS MEDICOS|IGNORA ISSO.
# Destaques: MAIORIA, MEDICOS, IGNORA

# Precisamos gerar fundo contextual para a Dra.
# Usar compose_cover.py ou make_cover.py com foto já composta

# Primeiro, vamos compor a foto da Dra. com fundo contextual via rembg + Unsplash
import requests
from io import BytesIO

# Buscar fundo contextual: laboratório, aminoácidos, ciência
resp = requests.get('https://unsplash.com/napi/search/photos',
    params={'query': 'dark laboratory science molecular biology research', 'per_page': 10, 'orientation': 'landscape'},
    timeout=20)
resp.raise_for_status()
results = resp.json()['results']
img_bytes = requests.get(results[0]['urls']['regular'], timeout=30).content
bg = Image.open(BytesIO(img_bytes)).convert('RGB').resize((1080, 820), Image.LANCZOS)
bg = bg.filter(ImageFilter.GaussianBlur(radius=8))
from PIL import ImageEnhance
bg = ImageEnhance.Brightness(bg).enhance(0.35)

# Remover fundo da foto da Dra. (simulação - usar foto com fundo escuro já)
# Como não temos rembg funcionando perfeitamente, vamos usar a foto original
# que já tem fundo escuro de estúdio, e aplicar o gradiente via make_cover.py

# Salvar fundo
bg_path = OUT / 'bg_contextual.jpg'
bg.save(bg_path, 'JPEG', quality=88)

# Gerar círculo temático: aminoácido/glicina
# Buscar imagem de cápsulas/pó de suplemento
circ_resp = requests.get('https://unsplash.com/napi/search/photos',
    params={'query': 'white powder supplement amino acid close up', 'per_page': 10, 'orientation': 'squarish'},
    timeout=20)
circ_resp.raise_for_status()
circ_results = circ_resp.json()['results']
circ_bytes = requests.get(circ_results[0]['urls']['regular'], timeout=30).content
circ = Image.open(BytesIO(circ_bytes)).convert('RGB').resize((200, 200), Image.LANCZOS)
circ_path = OUT / 'circulo_tematico.jpg'
circ.save(circ_path, 'JPEG', quality=88)

# Gerar capa com make_cover.py
headline = 'A MAIORIA|DOS MEDICOS|IGNORA ISSO.'
destaques = 'MAIORIA,MEDICOS,IGNORA'

subprocess.run([
    'python3', MAKE_COVER,
    '--foto', FOTO,
    '--circulo', str(circ_path),
    '--headline', headline,
    '--destaques', destaques,
    '--out', str(OUT / 'slide_01.jpg')
], check=True)

print('Capa gerada.')
print('Próximo passo: gerar slides 2-10 no formato tweet com fundo PRETO.')
