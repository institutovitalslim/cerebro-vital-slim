from pathlib import Path
from io import BytesIO
import requests, subprocess
from PIL import Image, ImageFilter, ImageEnhance

OUT = Path('/root/cerebro-vital-slim/deliverables/menopausa-nutrientes-carrossel-2026-04-21/slide_01.jpg')
TMP = Path('/root/cerebro-vital-slim/deliverables/menopausa-nutrientes-carrossel-2026-04-21/tmp')
TMP.mkdir(parents=True, exist_ok=True)

FOTO = Path('/root/.openclaw/workspace/fotos_dra/originais/Imagem PNG 124.png')
CIRCULO = Path('/root/.openclaw/media/tool-image-generation/menopausa_nutrientes_circle---046136d8-41df-4cce-a575-93a6035a4429.jpg')
MAKE = '/root/.openclaw/workspace/skills/tweet-carrossel/scripts/make_cover.py'
HEADLINE = 'NUTRIENTES QUE|PODEM AJUDAR|A MULHER NA|MENOPAUSA'
DESTAQUES = 'PODEM,AJUDAR,MENOPAUSA'
BG_QUERY = 'women vitamins supplements beige aesthetic'

resp = requests.get('https://unsplash.com/napi/search/photos', params={'query': BG_QUERY, 'per_page': 10, 'orientation': 'landscape'}, timeout=20)
resp.raise_for_status()
results = resp.json().get('results', [])
if not results:
    raise RuntimeError('No background results')
img_bytes = requests.get(results[0]['urls']['regular'], timeout=30).content
bg = Image.open(BytesIO(img_bytes)).convert('RGB').resize((1080, 820), Image.LANCZOS)
bg = bg.filter(ImageFilter.GaussianBlur(radius=6))
bg = ImageEnhance.Brightness(bg).enhance(0.38)
# subtle warm overlay
warm = Image.new('RGB', bg.size, (210, 178, 140))
bg = Image.blend(bg, warm, 0.10)

fg = Image.open(FOTO).convert('RGBA')
# scale to a flattering waist-up/3x4 prominence
scale_h = 770
ratio = scale_h / fg.height
fg = fg.resize((int(fg.width * ratio), scale_h), Image.LANCZOS)
canvas = bg.convert('RGBA')
# place more to the left to keep text area open
x = -10
y = 40
canvas.alpha_composite(fg, (x, y))
photo_comp = TMP / 'photo_context_v2.png'
canvas.convert('RGB').save(photo_comp, 'PNG')

subprocess.run([
    'python3', MAKE,
    '--foto', str(photo_comp),
    '--circulo', str(CIRCULO),
    '--headline', HEADLINE,
    '--destaques', DESTAQUES,
    '--out', str(OUT)
], check=True)
print(OUT)
