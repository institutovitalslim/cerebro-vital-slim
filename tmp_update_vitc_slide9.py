from pathlib import Path
import json, subprocess
from PIL import Image

BASE = Path('/root/cerebro-vital-slim/deliverables/vitamina-c-alem-da-imunidade-2026-04-21')
TMP = BASE / 'tmp_update_09'
TMP.mkdir(parents=True, exist_ok=True)
slides = [{
  'num': 9,
  'paragraphs': [
    'Mas atenção:',
    'Isso não significa que Vitamina C seja solução universal, nem que qualquer dose serve para qualquer pessoa.',
    'A individualização do tratamento é essencial para o resultado eficaz.'
  ]
}]
config = TMP/'slides_09.json'
config.write_text(json.dumps(slides, ensure_ascii=False, indent=2), encoding='utf-8')
out = TMP/'png'
out.mkdir(exist_ok=True)
subprocess.run([
    'python3', '/root/.openclaw/workspace/skills/tweet-carrossel/scripts/make_tweet_slides.py',
    '--config', str(config),
    '--avatar', '/root/.openclaw/media/inbound/avatar_dradaniely_oficial.png',
    '--out', str(out),
    '--name', 'Dra. Daniely Freitas',
    '--handle', '@dradaniely.freitas'
], check=True)
png = out/'slide_09.png'
Image.open(png).convert('RGB').save(BASE/'slide_09.jpg','JPEG',quality=85,optimize=True,progressive=True)
print(BASE/'slide_09.jpg')
