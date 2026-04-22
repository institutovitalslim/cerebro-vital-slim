from pathlib import Path
import subprocess, json
from PIL import Image

OUT = Path('/root/cerebro-vital-slim/deliverables/glicina-carrossel-2026-04-22')
OUT.mkdir(parents=True, exist_ok=True)
TMP = OUT / 'tmp'
TMP.mkdir(exist_ok=True)

MAKE = '/root/.openclaw/workspace/skills/tweet-carrossel/scripts/make_cover.py'
SLIDES_SCRIPT = '/root/.openclaw/workspace/skills/tweet-carrossel/scripts/make_tweet_slides.py'
AVATAR = '/root/.openclaw/media/inbound/avatar_dradaniely_oficial.png'
FOTO = '/root/.openclaw/workspace/fotos_dra/originais/Imagem PNG 124.png'

# Gerar imagem contextual para círculo
import requests
from io import BytesIO
from PIL import ImageFilter, ImageEnhance

resp = requests.get('https://unsplash.com/napi/search/photos', 
    params={'query': 'glycine amino acid supplement capsules medical', 'per_page': 10, 'orientation': 'landscape'}, 
    timeout=20)
resp.raise_for_status()
results = resp.json()['results']
img_bytes = requests.get(results[0]['urls']['regular'], timeout=30).content
bg = Image.open(BytesIO(img_bytes)).convert('RGB').resize((1080, 820), Image.LANCZOS)
bg = bg.filter(ImageFilter.GaussianBlur(radius=6))
bg = ImageEnhance.Brightness(bg).enhance(0.38)
warm = Image.new('RGB', bg.size, (210, 178, 140))
bg = Image.blend(bg, warm, 0.10)
circulo_path = TMP / 'circulo_glycine.jpg'
bg.save(circulo_path, 'JPEG', quality=88, optimize=True)

# Capa
headline = 'GLICINA|O AMINOÁCIDO|QUE VOCÊ|NÃO CONHECE'
destaques = 'GLICINA,AMINOÁCIDO,NÃO,CONHECE'

subprocess.run([
    'python3', MAKE,
    '--foto', FOTO,
    '--circulo', str(circulo_path),
    '--headline', headline,
    '--destaques', destaques,
    '--out', str(OUT / 'slide_01.jpg')
], check=True)

# Slides 2-10
slides = [
    {'num': 2, 'paragraphs': [
        'E se eu te dissesse que um aminoácido simples pode:',
        '',
        '→ Aumentar sua expectativa de vida',
        '→ Apagar a inflamação crônica',
        '→ Curar seu intestino',
        '→ Fazer você dormir como um bebê'
    ]},
    {'num': 3, 'paragraphs': [
        'Esse aminoácido é a GLICINA.',
        '',
        'Ela é um componente essencial do colágeno,',
        'responsável pela firmeza da pele,',
        'saúde das articulações e',
        'integridade do trato intestinal.'
    ]},
    {'num': 4, 'paragraphs': [
        'A glicina também é um potente',
        'ANTI-INFLAMATÓRIO natural.',
        '',
        'Ela reduz a produção de citocinas pró-inflamatórias,',
        'ajudando a combater doenças crônicas',
        'ligadas à inflamação de baixo grau.'
    ]},
    {'num': 5, 'paragraphs': [
        'Além disso, a glicina é fundamental',
        'para a QUALIDADE DO SONO.',
        '',
        'Ela regula a temperatura corporal',
        'e promove relaxamento muscular,',
        'facilitando o sono profundo e restaurador.'
    ]},
    {'num': 6, 'paragraphs': [
        'Mas aqui está o que poucos sabem:',
        '',
        'A glicina contrabalanceia os efeitos',
        'pró-envelhecimento da METIONINA em excesso,',
        'principal componente das carnes vermelhas.',
        '',
        'Quem come muita carne precisa',
        'URGENTE de mais glicina.'
    ]},
    {'num': 7, 'paragraphs': [
        'A deficiência de glicina está associada a:',
        '',
        '• Envelhecimento prematuro',
        '• Deterioração da pele',
        '• Dor articular',
        '• Síndrome do intestino permeável',
        '• Dificuldade para dormir'
    ]},
    {'num': 8, 'paragraphs': [
        'E a boa notícia?',
        '',
        'Você pode aumentar seus níveis de glicina',
        'de forma simples e natural.',
        '',
        'A suplementação adequada pode trazer',
        'benefícios em poucas semanas.'
    ]},
    {'num': 9, 'paragraphs': [
        'Mas atenção:',
        '',
        'Isso não significa que glicina seja',
        'solução universal, nem que qualquer dose',
        'serve para qualquer pessoa.',
        '',
        'A individualização do tratamento é',
        'essencial para o resultado eficaz.'
    ]},
    {'num': 10, 'paragraphs': [
        'Quer saber se a glicina faz sentido',
        'para o seu caso?',
        '',
        'Agende uma consulta de avaliação',
        'e descubra o que seu corpo realmente precisa.',
        '',
        'Link na bio'
    ]}
]

slides_json = TMP / 'slides.json'
slides_json.write_text(json.dumps(slides, ensure_ascii=False, indent=2), encoding='utf-8')
png_out = TMP / 'png'
png_out.mkdir(exist_ok=True)

subprocess.run([
    'python3', SLIDES_SCRIPT,
    '--config', str(slides_json),
    '--avatar', AVATAR,
    '--out', str(png_out),
    '--name', 'Dra. Daniely Freitas',
    '--handle', '@dradaniely.freitas'
], check=True)

for png in sorted(png_out.glob('slide_*.png')):
    Image.open(png).convert('RGB').save(OUT / f'{png.stem}.jpg', 'JPEG', quality=85, optimize=True, progressive=True)

print(OUT)
for p in sorted(OUT.glob('slide_*.jpg')):
    print(p.name)
