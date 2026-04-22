from pathlib import Path
import subprocess, json
from PIL import Image

TMP = Path('/root/cerebro-vital-slim/tmp_fix_slide8')
TMP.mkdir(parents=True, exist_ok=True)

# Slide 8 com o símbolo corrigido
slides = [{
    'num': 8,
    'paragraphs': [
        'Aqui está o que poucos sabem:',
        '',
        'A glicina contrabalanceia os efeitos pró-envelhecimento da METIONINA em excesso — principal componente das carnes vermelhas.',
        '',
        'Quem come muita carne precisa URGENTE de mais glicina.',
        '',
        '☐ Miller et al. (2019). PMID: 30916479'
    ]
}]

config = TMP / 'slide_08.json'
config.write_text(json.dumps(slides, ensure_ascii=False, indent=2), encoding='utf-8')

out_dir = TMP / 'png'
out_dir.mkdir(exist_ok=True)

subprocess.run([
    'python3', '/root/.openclaw/workspace/skills/tweet-carrossel/scripts/make_tweet_slides.py',
    '--config', str(config),
    '--avatar', '/root/.openclaw/media/inbound/avatar_dradaniely_oficial.png',
    '--out', str(out_dir),
    '--name', 'Dra. Daniely Freitas',
    '--handle', '@dradaniely.freitas'
], check=True)

png = out_dir / 'slide_08.png'
out_jpg = Path('/root/cerebro-vital-slim/deliverables/slide_08_fixed_symbol.jpg')
Image.open(png).convert('RGB').save(out_jpg, 'JPEG', quality=90, optimize=True, progressive=True)
print(out_jpg)
