from pathlib import Path
from io import BytesIO
import subprocess, json, base64, shutil, requests
from PIL import Image, ImageFilter, ImageEnhance

OUT = Path('/root/cerebro-vital-slim/deliverables/creatina-cerebro-jpeg-2026-04-14')
OUT.mkdir(parents=True, exist_ok=True)
TMP = OUT / 'tmp'
TMP.mkdir(exist_ok=True)

FOTO = Path('/root/.openclaw/workspace/fotos_dra/dra_seria_lateral.png')
CIRCULO = Path('/root/circulo_creatina_v2.png')
AVATAR = Path('/root/.openclaw/media/inbound/avatar_dradaniely_oficial.png')
COMPOSE = '/root/.openclaw/workspace/skills/tweet-carrossel/scripts/compose_cover.py'
SLIDES_SCRIPT = '/root/.openclaw/workspace/skills/tweet-carrossel/scripts/make_tweet_slides.py'

HEADLINE = 'UM DOS SUPLEMENTOS|MAIS SUBESTIMADOS|PARA O CÉREBRO'
DESTAQUES = 'SUPLEMENTOS,SUBESTIMADOS,CÉREBRO'
TEMA = 'supplement store shelves dark'

# Approved internal copy already preserved in workspace artifact.
slides = [
  {
    'num': 3,
    'paragraphs': [
      'Esta revisão analisou 16 estudos clínicos randomizados.',
      'Ao todo, foram 492 participantes, com idades entre 20,8 e 76,4 anos.',
      'Não foi um estudo isolado. →'
    ]
  },
  {
    'num': 4,
    'paragraphs': [
      'Os pesquisadores encontraram melhora significativa na memória.',
      'Isso significa mais facilidade para guardar e recuperar informações.',
      'E esse foi um dos achados mais consistentes da análise. →'
    ]
  },
  {
    'num': 5,
    'paragraphs': [
      'Também houve melhora no tempo de atenção.',
      'Na prática, isso sugere um cérebro mais rápido para responder e sustentar foco.',
      'Especialmente em tarefas mentais mais exigentes. →'
    ]
  },
  {
    'num': 6,
    'paragraphs': [
      'Outro ponto importante foi a melhora na velocidade de processamento.',
      'Ou seja, o cérebro conseguiu lidar melhor com a informação em menos tempo.',
      'Isso importa muito no raciocínio do dia a dia. →'
    ]
  },
  {
    'num': 7,
    'paragraphs': [
      'Os melhores resultados apareceram principalmente em mulheres, em pessoas entre 18 e 60 anos e em pacientes com alguma condição de saúde.',
      'Ou seja, o efeito não apareceu de forma aleatória. →'
    ]
  },
  {
    'num': 8,
    'paragraphs': [
      'Em todos os estudos incluídos, a forma usada foi a creatina monohidratada.',
      'Isso reforça que estamos falando da forma mais estudada da creatina.',
      'E não de uma promessa genérica. →'
    ]
  },
  {
    'num': 9,
    'paragraphs': [
      'A conclusão não é que creatina faz milagre.',
      'A conclusão é outra: ela pode ajudar memória, atenção e velocidade mental quando existe indicação correta. →'
    ]
  },
  {
    'num': 10,
    'paragraphs': [
      'Estamos falando de um suplemento que muita gente associa apenas à força muscular.',
      'Mas a pesquisa mostra que ele também pode apoiar o funcionamento do cérebro.',
      'E isso merece mais atenção.',
      'Se este conteúdo fez sentido para você, salve este post.'
    ]
  }
]


def save_jpeg(src: Path, dst: Path, quality: int = 85):
    img = Image.open(src)
    if img.mode in ('RGBA', 'LA'):
        bg = Image.new('RGB', img.size, (0, 0, 0))
        if img.mode == 'RGBA':
            bg.paste(img, mask=img.getchannel('A'))
        else:
            bg.paste(img)
        img = bg
    else:
        img = img.convert('RGB')
    img.save(dst, 'JPEG', quality=quality, optimize=True, progressive=True)


# 1) Unsplash fallback background
search_url = 'https://unsplash.com/napi/search/photos'
params = {'query': TEMA, 'per_page': 10, 'orientation': 'landscape'}
resp = requests.get(search_url, params=params, timeout=20)
resp.raise_for_status()
results = resp.json().get('results', [])
if not results:
    raise RuntimeError('Nenhum resultado no Unsplash para o fundo')
img_url = results[0]['urls']['regular']
img_bytes = requests.get(img_url, timeout=30).content
bg = Image.open(BytesIO(img_bytes)).convert('RGB')
bg = bg.resize((1080, 743), Image.LANCZOS)
bg = bg.filter(ImageFilter.GaussianBlur(radius=8))
bg = ImageEnhance.Brightness(bg).enhance(0.35)
bg_path = TMP / 'bg_unsplash_creatina.jpg'
bg.save(bg_path, 'JPEG', quality=88, optimize=True)

# 2) Cover via compose_cover.py
cover_path = OUT / 'slide_01.jpg'
subprocess.run([
    'python3', COMPOSE,
    '--foto', str(FOTO),
    '--tema', TEMA,
    '--circulo', str(CIRCULO),
    '--headline', HEADLINE,
    '--destaques', DESTAQUES,
    '--skip-bg', str(bg_path),
    '--out', str(cover_path),
], check=True)

# 3) Slide 2 via HTML + Chromium headless, output JPEG
pubmed_png = TMP / 'pubmed_39070254.png'
subprocess.run([
    'google-chrome', '--headless=new', '--disable-gpu', '--no-sandbox', '--hide-scrollbars',
    '--window-size=1400,1700', f'--screenshot={pubmed_png}', 'https://pubmed.ncbi.nlm.nih.gov/39070254/'
], check=True)

def data_uri(path: Path) -> str:
    mime = 'image/png' if path.suffix.lower() == '.png' else 'image/jpeg'
    return f'data:{mime};base64,' + base64.b64encode(path.read_bytes()).decode('ascii')

html_path = TMP / 'slide_02.html'
slide2_png = TMP / 'slide_02.png'
html = f'''<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=1080, initial-scale=1">
<style>
* {{ box-sizing:border-box; }}
html, body {{ margin:0; width:1080px; height:1350px; background:#000; overflow:hidden; font-family:Inter,Arial,sans-serif; }}
body {{ color:#e8e8e8; }}
.wrap {{ width:1080px; height:1350px; padding:42px 48px 44px; position:relative; }}
.header {{ display:flex; align-items:center; gap:18px; margin-bottom:26px; }}
.avatar {{ width:72px; height:72px; border-radius:50%; overflow:hidden; border:2px solid #1d1d1d; flex:0 0 auto; }}
.avatar img {{ width:100%; height:100%; object-fit:cover; }}
.meta {{ line-height:1.1; }}
.name {{ font-size:28px; font-weight:700; color:#fff; }}
.handle {{ font-size:22px; color:#8b8b8b; margin-top:6px; }}
.tweet {{ font-size:38px; line-height:1.22; color:#d5d5d5; font-weight:500; letter-spacing:-0.02em; margin-bottom:26px; }}
.shot-card {{ width:100%; border:1px solid #242424; border-radius:26px; overflow:hidden; background:#0c0c0c; box-shadow:0 0 0 1px rgba(255,255,255,0.03) inset; }}
.shot-card img {{ width:100%; display:block; }}
</style>
</head>
<body>
<div class="wrap">
  <div class="header">
    <div class="avatar"><img src="{data_uri(AVATAR)}"></div>
    <div class="meta">
      <div class="name">Dra. Daniely Freitas</div>
      <div class="handle">@dradaniely.freitas</div>
    </div>
  </div>
  <div class="tweet">Este estudo reuniu 16 estudos clínicos randomizados, com 492 participantes, e encontrou melhora em memória, atenção e velocidade de processamento.</div>
  <div class="shot-card"><img src="{data_uri(pubmed_png)}"></div>
</div>
</body>
</html>'''
html_path.write_text(html, encoding='utf-8')
subprocess.run([
    'google-chrome', '--headless=new', '--disable-gpu', '--no-sandbox', '--hide-scrollbars',
    '--window-size=1080,1350', f'--screenshot={slide2_png}', f'file://{html_path}'
], check=True)
save_jpeg(slide2_png, OUT / 'slide_02.jpg', quality=85)

# 4) Slides 3+ via skill generator, then convert to JPEG
slides_json = TMP / 'slides.json'
slides_json.write_text(json.dumps(slides, ensure_ascii=False, indent=2), encoding='utf-8')
png_out = TMP / 'png_slides'
png_out.mkdir(exist_ok=True)
subprocess.run([
    'python3', SLIDES_SCRIPT,
    '--config', str(slides_json),
    '--avatar', str(AVATAR),
    '--out', str(png_out),
    '--name', 'Dra. Daniely Freitas',
    '--handle', '@dradaniely.freitas'
], check=True)
for png in sorted(png_out.glob('slide_*.png')):
    stem = png.stem
    save_jpeg(png, OUT / f'{stem}.jpg', quality=85)

# Clean any accidental png/junk in final dir
for p in OUT.iterdir():
    if p.suffix.lower() in {'.png', '.html', '.json'}:
        p.unlink()

print('DONE', OUT)
for p in sorted(OUT.glob('slide_*.jpg')):
    print(p.name, p.stat().st_size)
