from pathlib import Path
import subprocess, json
from PIL import Image

TMP = Path('/root/cerebro-vital-slim/tmp_fix_glynac')
TMP.mkdir(parents=True, exist_ok=True)

# Slide 2 corrigido (badge + avatar)
slide2 = [{
    'num': 2,
    'paragraphs': [
        'E se eu te dissesse que um aminoácido simples pode:',
        '',
        '→ Aumentar sua expectativa de vida',
        '→ Apagar a inflamação crônica',
        '→ Curar seu intestino',
        '→ Fazer você dormir como um bebê'
    ]
}]

# Slide 8 corrigido (símbolo)
slide8 = [{
    'num': 8,
    'paragraphs': [
        'Aqui está o que poucos sabem:',
        '',
        'A glicina contrabalanceia os efeitos pró-envelhecimento da METIONINA em excesso — principal componente das carnes vermelhas.',
        '',
        'Quem come muita carne precisa URGENTE de mais glicina.',
        '',
        '• Miller et al. (2019). PMID: 30916479'
    ]
}]

out_dir = TMP / 'png'
out_dir.mkdir(exist_ok=True)

for slides, label in [(slide2, 'slide_02'), (slide8, 'slide_08')]:
    config = TMP / f'{label}.json'
    config.write_text(json.dumps(slides, ensure_ascii=False, indent=2), encoding='utf-8')
    
    subprocess.run([
        'python3', '/root/.openclaw/workspace/skills/tweet-carrossel/scripts/make_tweet_slides.py',
        '--config', str(config),
        '--avatar', '/root/.openclaw/media/inbound/avatar_dradaniely_oficial.png',
        '--out', str(out_dir),
        '--name', 'Dra. Daniely Freitas',
        '--handle', '@dradaniely.freitas'
    ], check=True)
    
    png = out_dir / f'{label}.png'
    out_jpg = Path(f'/root/cerebro-vital-slim/deliverables/{label}_fixed.jpg')
    Image.open(png).convert('RGB').save(out_jpg, 'JPEG', quality=90, optimize=True, progressive=True)
    print(f'Gerado: {out_jpg}')
