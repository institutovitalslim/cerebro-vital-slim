#!/usr/bin/env python3
"""Carrossel GLICINA - Copy original aprovada + padrão skill tweet-carrossel v4."""

from pathlib import Path
import subprocess
import json
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import requests
from io import BytesIO

OUT = Path('/root/cerebro-vital-slim/deliverables/glicina-carrossel-final-2026-04-22')
OUT.mkdir(parents=True, exist_ok=True)
TMP = OUT / 'tmp'
TMP.mkdir(exist_ok=True)

MAKE_COVER = '/root/.openclaw/workspace/skills/tweet-carrossel/scripts/make_cover.py'
AVATAR = '/root/avatar_hq.png'
FOTO = '/root/.openclaw/workspace/fotos_dra/originais/Imagem PNG 124.png'

# ── CAPA (Slide 1) ──
# Copy original aprovada: headline "A MAIORIA|DOS MEDICOS|IGNORA ISSO."

# Fundo contextual via Unsplash
resp = requests.get('https://unsplash.com/napi/search/photos',
    params={'query': 'dark laboratory science molecular biology research', 'per_page': 10, 'orientation': 'landscape'},
    timeout=20)
resp.raise_for_status()
results = resp.json()['results']
img_bytes = requests.get(results[0]['urls']['regular'], timeout=30).content
bg = Image.open(BytesIO(img_bytes)).convert('RGB').resize((1080, 820), Image.LANCZOS)
bg = bg.filter(ImageFilter.GaussianBlur(radius=8))
bg = ImageEnhance.Brightness(bg).enhance(0.35)
bg_path = TMP / 'bg_contextual.jpg'
bg.save(bg_path, 'JPEG', quality=88)

# Círculo temático: usar imagem local de suplemento ou criar um gradiente
# Buscar imagem de cápsulas/pó branco com termo mais simples
circ_resp = requests.get('https://unsplash.com/napi/search/photos',
    params={'query': 'white powder medical', 'per_page': 10, 'orientation': 'squarish'},
    timeout=20)
circ_resp.raise_for_status()
circ_results = circ_resp.json()['results']
if circ_results:
    circ_bytes = requests.get(circ_results[0]['urls']['regular'], timeout=30).content
    circ = Image.open(BytesIO(circ_bytes)).convert('RGB').resize((200, 200), Image.LANCZOS)
else:
    # Fallback: gradiente dourado
    circ = Image.new('RGB', (200, 200), (210, 178, 140))
    
circ_path = TMP / 'circulo_tematico.jpg'
circ.save(circ_path, 'JPEG', quality=88)

# Gerar capa
subprocess.run([
    'python3', MAKE_COVER,
    '--foto', FOTO,
    '--circulo', str(circ_path),
    '--headline', 'A MAIORIA|DOS MEDICOS|IGNORA ISSO.',
    '--destaques', 'MAIORIA,MEDICOS,IGNORA',
    '--out', str(OUT / 'slide_01.jpg')
], check=True)

# ── SLIDES 2-10 (formato tweet, fundo PRETO) ──
W, H = 1080, 1350
BG = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (140, 150, 145)
VERIFIED_BG = (29, 155, 240)
MARGIN_L = 64
MARGIN_R = 64
AVATAR_SIZE = 96
NAME_SIZE = 48
HANDLE_SIZE = 34
BODY_SIZE = 50
LINE_HEIGHT = 72
PARA_GAP = 36

FONT_BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FONT_REG = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

def get_font(size, bold=False):
    path = FONT_BOLD if bold else FONT_REG
    return ImageFont.truetype(path, size)

def make_circular_avatar(path, size):
    av = Image.open(path).convert('RGBA')
    w, h = av.size
    min_dim = min(w, h)
    left = (w - min_dim) // 2
    top = (h - min_dim) // 2
    av = av.crop((left, top, left + min_dim, top + min_dim))
    av = av.resize((size, size), Image.LANCZOS)
    mask = Image.new('L', (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size, size), fill=255)
    out = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    out.paste(av, mask=mask)
    return out

def wrap_text(text, font, max_width):
    d = ImageDraw.Draw(Image.new('RGB', (1, 1)))
    words = text.split(' ')
    lines, current = [], ''
    for w in words:
        test = (current + ' ' + w).strip()
        if d.textbbox((0, 0), test, font=font)[2] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines

def make_slide(paragraphs, out_path, name='Dra. Daniely Freitas', handle='@dradaniely.freitas'):
    img = Image.new('RGB', (W, H), BG)
    draw = ImageDraw.Draw(img)
    font_name = get_font(NAME_SIZE, bold=True)
    font_handle = get_font(HANDLE_SIZE)
    font_body = get_font(BODY_SIZE)
    max_w = W - MARGIN_L - MARGIN_R
    
    # Measure total height
    header_h = max(AVATAR_SIZE, NAME_SIZE + 8 + HANDLE_SIZE)
    body_h = 0
    for i, para in enumerate(paragraphs):
        if i > 0:
            if para == '':
                body_h += int(BODY_SIZE * 0.5)
                continue
            body_h += PARA_GAP
        if para == '':
            body_h += int(BODY_SIZE * 0.5)
            continue
        body_h += len(wrap_text(para, font_body, max_w)) * LINE_HEIGHT
    total_h = header_h + 36 + body_h
    
    # Center vertically
    y_start = max(60, (H - total_h) // 2 - 20)
    
    # Avatar
    av = make_circular_avatar(AVATAR, AVATAR_SIZE)
    img_rgba = img.convert('RGBA')
    img_rgba.paste(av, (MARGIN_L, y_start), av)
    img = img_rgba.convert('RGB')
    draw = ImageDraw.Draw(img)
    
    # Name + verified
    name_x = MARGIN_L + AVATAR_SIZE + 20
    name_y = y_start + 8
    draw.text((name_x, name_y), name, font=font_name, fill=WHITE)
    nb = draw.textbbox((name_x, name_y), name, font=font_name)
    # Verified badge
    bx = nb[2] + 12
    by = name_y + 8
    draw.ellipse((bx, by, bx + 24, by + 24), fill=VERIFIED_BG)
    draw.text((bx + 6, by + 3), '✓', fill=WHITE, font=get_font(14, bold=True))
    
    # Handle
    draw.text((name_x, name_y + NAME_SIZE + 6), handle, font=font_handle, fill=GRAY)
    
    # Body
    ty = y_start + header_h + 36
    for i, para in enumerate(paragraphs):
        if i > 0:
            if para == '':
                ty += int(BODY_SIZE * 0.5)
                continue
            ty += PARA_GAP
        if para == '':
            ty += int(BODY_SIZE * 0.5)
            continue
        for line in wrap_text(para, font_body, max_w):
            draw.text((MARGIN_L, ty), line, font=font_body, fill=WHITE)
            ty += LINE_HEIGHT
    
    img.save(out_path, 'JPEG', quality=85, optimize=True)
    print(f'  ✓ {out_path}')

# Copy original aprovada - slides 2-10
slides_data = [
    {'num': 2, 'paragraphs': [
        'E se eu te dissesse que um aminoácido simples pode:',
        '',
        '→ Aumentar sua expectativa de vida',
        '→ Apagar a inflamação crônica',
        '→ Curar seu intestino',
        '→ Fazer você dormir como um bebê'
    ]},
    {'num': 3, 'paragraphs': [
        'Você já se sentiu:',
        '',
        'Cansado o tempo todo?',
        'Com intestino irritado?',
        'Dormindo mal e acordando pior?',
        'Com pele envelhecendo rápido demais?',
        '',
        'A maioria acha que isso é "normal" da idade.'
    ]},
    {'num': 4, 'paragraphs': [
        'Isso tem nome:',
        '',
        'GLICINA.',
        '',
        'Um aminoácido que seu corpo produz, mas em quantidades insuficientes.',
        '',
        'Especialmente depois dos 30 anos.',
        '',
        'Ref: Razak et al. (2017). PMID: 28337245'
    ]},
    {'num': 5, 'paragraphs': [
        'A glicina é o maior anti-inflamatório natural.',
        '',
        'Ela suprime o NF-KB:',
        'o "regulador mestre" da inflamação.',
        '',
        'Está elevado em TODA doença crônica.',
        '',
        'Ref: Razak et al. (2017). PMID: 28337245'
    ]},
    {'num': 6, 'paragraphs': [
        'Ela também:',
        '',
        '→ Limpa a homocisteína (tóxica)',
        '→ Produz glutationa (antioxidante)',
        '→ É precursora da creatina',
        '→ Sintetiza colágeno',
        '→ Promove autofagia',
        '',
        'Ref: Razak et al. (2017). PMID: 28337245'
    ]},
    {'num': 7, 'paragraphs': [
        'Glicina + NAC = combo anti-aging.',
        '',
        'Estudo clínico mostrou melhora em:',
        'Glutationa, estresse oxidativo,',
        'função mitocondrial, inflamação,',
        'resistência à insulina...',
        '',
        'Ref: Kumar et al. (2021). PMID: 33783984'
    ]},
    {'num': 8, 'paragraphs': [
        'Aqui está o que poucos sabem:',
        '',
        'A glicina contrabalanceia os efeitos pró-envelhecimento da METIONINA em excesso — principal componente das carnes vermelhas.',
        '',
        'Quem come muita carne precisa URGENTE de mais glicina.',
        '',
        'Ref: Miller et al. (2019). PMID: 30916479'
    ]},
    {'num': 9, 'paragraphs': [
        'Como usar:',
        '',
        '→ 3g antes de dormir (melhora sono profundo)',
        '→ 1-2g pela manhã (energia e foco)',
        '',
        'Fontes naturais:',
        'Caldo de ossos, pele de frango,',
        'colágeno hidrolisado',
        '',
        'Ref: Bannai et al. (2012). PMID: 22529837'
    ]},
    {'num': 10, 'paragraphs': [
        'Salva isso antes que suma.',
        '',
        'Qual desses benefícios você mais precisa?',
        '',
        'Comenta aqui 👇',
        '',
        '',
        'Dra. Daniely Freitas',
        'CRM-BA 27588'
    ]}
]

for slide in slides_data:
    make_slide(
        slide['paragraphs'],
        OUT / f'slide_{slide["num"]:02d}.jpg'
    )

print(f'\n✅ Carrossel completo em: {OUT}')
for p in sorted(OUT.glob('slide_*.jpg')):
    print(f'  {p.name}')
