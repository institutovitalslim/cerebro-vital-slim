from pathlib import Path
from io import BytesIO
import requests, subprocess, os
from PIL import Image, ImageFilter, ImageEnhance, ImageOps

OUT = Path('/root/cerebro-vital-slim/deliverables/menopausa-nutrientes-carrossel-2026-04-21/slide_01.jpg')
TMP = Path('/root/cerebro-vital-slim/deliverables/menopausa-nutrientes-carrossel-2026-04-21/tmp')
TMP.mkdir(parents=True, exist_ok=True)

FOTO = Path('/root/.openclaw/workspace/fotos_dra/originais/Imagem PNG 124.png')
CIRCULO = Path('/root/.openclaw/media/tool-image-generation/menopausa_nutrientes_circle---046136d8-41df-4cce-a575-93a6035a4429.jpg')
MAKE = '/root/.openclaw/workspace/skills/tweet-carrossel/scripts/make_cover.py'
HEADLINE = 'NUTRIENTES QUE|PODEM AJUDAR|A MULHER NA|MENOPAUSA'
DESTAQUES = 'PODEM,AJUDAR,MENOPAUSA'
BG_QUERY = 'women vitamins supplements capsules wellness flatlay'

# 1) Contextual background, visibly related to supplements/women health
resp = requests.get('https://unsplash.com/napi/search/photos', params={'query': BG_QUERY, 'per_page': 10, 'orientation': 'landscape'}, timeout=20)
resp.raise_for_status()
results = resp.json().get('results', [])
if not results:
    raise RuntimeError('No background results')
img_bytes = requests.get(results[0]['urls']['regular'], timeout=30).content
bg = Image.open(BytesIO(img_bytes)).convert('RGB').resize((1080, 820), Image.LANCZOS)
bg = bg.filter(ImageFilter.GaussianBlur(radius=4))
bg = ImageEnhance.Brightness(bg).enhance(0.52)
bg = ImageEnhance.Contrast(bg).enhance(0.95)
# warm tint
warm = Image.new('RGB', bg.size, (205, 170, 130))
bg = Image.blend(bg, warm, 0.08)

# 2) Remove background from Dra. using rembg CLI if available
nobg = TMP / 'dra_nobg.png'
soft = TMP / 'dra_nobg_soft.png'
if nobg.exists():
    nobg.unlink()
if soft.exists():
    soft.unlink()
subprocess.run(['rembg', 'i', str(FOTO), str(nobg)], check=True)

# 3) Soften alpha edges to avoid halo
fg = Image.open(nobg).convert('RGBA')
alpha = fg.getchannel('A').filter(ImageFilter.GaussianBlur(radius=1.2))
fg.putalpha(alpha)
# crop transparent margins
bbox = fg.getbbox()
fg = fg.crop(bbox)

# 4) Scale and center better, keeping background visible behind her
scale_h = 760
ratio = scale_h / fg.height
fg = fg.resize((int(fg.width * ratio), scale_h), Image.LANCZOS)

canvas = bg.convert('RGBA')
# add subtle dark gradient at bottom-left for separation while preserving bg context
shadow = Image.new('RGBA', canvas.size, (0,0,0,0))
for y in range(canvas.height):
    a = int(70 * (y / canvas.height))
    for x in range(int(canvas.width*0.55)):
        shadow.putpixel((x, y), (0,0,0,a))
canvas = Image.alpha_composite(canvas, shadow)

# center-left placement, not stuck to edge
x = 120
y = 35
canvas.alpha_composite(fg, (x, y))
photo_comp = TMP / 'photo_context_v3.png'
canvas.convert('RGB').save(photo_comp, 'PNG')

# 5) Build final cover in official style
subprocess.run([
    'python3', MAKE,
    '--foto', str(photo_comp),
    '--circulo', str(CIRCULO),
    '--headline', HEADLINE,
    '--destaques', DESTAQUES,
    '--out', str(OUT)
], check=True)
print(OUT)
