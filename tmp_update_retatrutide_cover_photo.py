from pathlib import Path
from io import BytesIO
import requests, subprocess
from PIL import Image, ImageFilter, ImageEnhance

OUT = Path('/root/cerebro-vital-slim/deliverables/retatrutide-tweet-carrossel-2026-04-17/slide_01.jpg')
TMP = Path('/root/cerebro-vital-slim/deliverables/retatrutide-tweet-carrossel-2026-04-17/tmp')
TMP.mkdir(parents=True, exist_ok=True)

FOTO = Path('/root/.openclaw/workspace/fotos_dra/originais/seria_bracos_cruzados.png')
CIRCULO = Path('/root/.openclaw/media/tool-image-generation/retatrutide_adipose_circle---b4ec480f-a7db-4113-b9c1-65ac635d98b0.jpg')
COMPOSE = '/root/.openclaw/workspace/skills/tweet-carrossel/scripts/compose_cover.py'
HEADLINE = 'RETATRUTIDE|NÃO ESTÁ SÓ|FAZENDO O PACIENTE|EMAGRECER'
DESTAQUES = 'RETATRUTIDE,FAZENDO,EMAGRECER'
BG_QUERY = 'medical laboratory dark moody'

resp = requests.get('https://unsplash.com/napi/search/photos', params={'query': BG_QUERY, 'per_page': 10, 'orientation': 'landscape'}, timeout=20)
resp.raise_for_status()
results = resp.json().get('results', [])
if not results:
    raise RuntimeError('No Unsplash results for background')
img_bytes = requests.get(results[0]['urls']['regular'], timeout=30).content
bg = Image.open(BytesIO(img_bytes)).convert('RGB')
bg = bg.resize((1080, 743), Image.LANCZOS)
bg = bg.filter(ImageFilter.GaussianBlur(radius=8))
bg = ImageEnhance.Brightness(bg).enhance(0.35)
bg_path = TMP / 'bg_retatrutide_new.jpg'
bg.save(bg_path, 'JPEG', quality=88, optimize=True)

subprocess.run([
    'python3', COMPOSE,
    '--foto', str(FOTO),
    '--tema', BG_QUERY,
    '--circulo', str(CIRCULO),
    '--headline', HEADLINE,
    '--destaques', DESTAQUES,
    '--skip-bg', str(bg_path),
    '--out', str(OUT),
], check=True)

print(OUT)
