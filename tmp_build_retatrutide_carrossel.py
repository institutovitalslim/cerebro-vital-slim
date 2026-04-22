from pathlib import Path
from io import BytesIO
import subprocess, json, base64, requests
from PIL import Image, ImageFilter, ImageEnhance

OUT = Path('/root/cerebro-vital-slim/deliverables/retatrutide-tweet-carrossel-2026-04-17')
OUT.mkdir(parents=True, exist_ok=True)
TMP = OUT / 'tmp'
TMP.mkdir(exist_ok=True)

FOTO = Path('/root/.openclaw/workspace/fotos_dra/dra_seria_frontal.png')
CIRCULO = Path('/root/.openclaw/media/tool-image-generation/retatrutide_adipose_circle---b4ec480f-a7db-4113-b9c1-65ac635d98b0.jpg')
AVATAR = Path('/root/.openclaw/media/inbound/avatar_dradaniely_oficial.png')
PDF_PATH = Path('/root/.openclaw/media/inbound/Retatrutide_na_Reprogramac_a_o_Metabo_lica_do_Tecido_Adiposo---c3dd763a-1c41-425a-a56e-e3118a79c501.pdf')
COMPOSE = '/root/.openclaw/workspace/skills/tweet-carrossel/scripts/compose_cover.py'
SLIDES_SCRIPT = '/root/.openclaw/workspace/skills/tweet-carrossel/scripts/make_tweet_slides.py'

HEADLINE = 'RETATRUTIDE|NÃO ESTÁ SÓ|FAZENDO O PACIENTE|EMAGRECER'
DESTAQUES = 'RETATRUTIDE,FAZENDO,EMAGRECER'
BG_QUERY = 'medical laboratory dark moody'

slides = [
  {
    'num': 3,
    'paragraphs': [
      'O ponto mais importante aqui não foi a balança.',
      'Foi o que aconteceu dentro da gordura.',
      '→'
    ]
  },
  {
    'num': 4,
    'paragraphs': [
      'Mesmo sem diferença significativa na ingestão média de alimentos, os animais perderam gordura e melhoraram o metabolismo.',
      'Ou seja: não parece ser só “comer menos”.',
      '→'
    ]
  },
  {
    'num': 5,
    'paragraphs': [
      'O tecido adiposo deixou de funcionar só como depósito.',
      'Passou a quebrar e usar melhor a gordura como energia.',
      '→'
    ]
  },
  {
    'num': 6,
    'paragraphs': [
      'Além disso, o estudo mostrou menos inflamação e menos sinais de fibrose.',
      'Isso sugere um tecido mais funcional e menos disfuncional metabolicamente.',
      '→'
    ]
  },
  {
    'num': 7,
    'paragraphs': [
      'E teve mais um detalhe importante:',
      'não foi simplesmente “transformar gordura branca em gordura marrom”.',
      'Foi gordura branca funcionando melhor.',
      '→'
    ]
  },
  {
    'num': 8,
    'paragraphs': [
      'Isso muda o raciocínio sobre obesidade.',
      'O alvo não é só reduzir peso.',
      'É melhorar a qualidade metabólica do tecido adiposo.',
      '→'
    ]
  },
  {
    'num': 9,
    'paragraphs': [
      'Se esse caminho se confirmar em humanos, o tratamento pode ajudar não só no emagrecimento, mas também na sustentação do resultado.',
      '→'
    ]
  },
  {
    'num': 10,
    'paragraphs': [
      'Mas atenção: este é um estudo em camundongos.',
      'Promissor? Muito.',
      'Prova final em humanos? Ainda não.',
      'Salve este post para acompanhar essa nova fase do tratamento da obesidade.'
    ]
  }
]

slide2_text = 'Este estudo pré-clínico usou análise multiômica e sugere que a retatrutide pode melhorar a qualidade metabólica do tecido adiposo, além de reduzir peso.'


def save_jpeg(src: Path, dst: Path, quality: int = 85):
    img = Image.open(src)
    if img.mode in ('RGBA', 'LA'):
        bg = Image.new('RGB', img.size, (0, 0, 0))
        if 'A' in img.getbands():
            bg.paste(img, mask=img.getchannel('A'))
        else:
            bg.paste(img)
        img = bg
    else:
        img = img.convert('RGB')
    img.save(dst, 'JPEG', quality=quality, optimize=True, progressive=True)


def data_uri(path: Path) -> str:
    mime = 'image/png' if path.suffix.lower() == '.png' else 'image/jpeg'
    return f'data:{mime};base64,' + base64.b64encode(path.read_bytes()).decode('ascii')

# 1. Background via Unsplash search
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
bg_path = TMP / 'bg_retatrutide.jpg'
bg.save(bg_path, 'JPEG', quality=88, optimize=True)

# 2. Cover
cover_path = OUT / 'slide_01.jpg'
subprocess.run([
    'python3', COMPOSE,
    '--foto', str(FOTO),
    '--tema', BG_QUERY,
    '--circulo', str(CIRCULO),
    '--headline', HEADLINE,
    '--destaques', DESTAQUES,
    '--skip-bg', str(bg_path),
    '--out', str(cover_path),
], check=True)

# 3. Render first page of PDF to image
first_page_png = TMP / 'paper_first_page.png'
subprocess.run([
    'pdftoppm', '-png', '-f', '1', '-singlefile', str(PDF_PATH), str(TMP / 'paper_first_page')
], check=True)

# 4. Slide 2 HTML + Chromium
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
.tweet {{ font-size:36px; line-height:1.22; color:#d5d5d5; font-weight:500; letter-spacing:-0.02em; margin-bottom:24px; }}
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
  <div class="tweet">{slide2_text}</div>
  <div class="shot-card"><img src="{data_uri(first_page_png)}"></div>
</div>
</body>
</html>'''
html_path.write_text(html, encoding='utf-8')
subprocess.run([
    'google-chrome', '--headless=new', '--disable-gpu', '--no-sandbox', '--hide-scrollbars',
    '--window-size=1080,1350', f'--screenshot={slide2_png}', f'file://{html_path}'
], check=True)
save_jpeg(slide2_png, OUT / 'slide_02.jpg', quality=85)

# 5. Slides 3+ via generator then convert to JPEG
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
    save_jpeg(png, OUT / f'{png.stem}.jpg', quality=85)

print('DONE', OUT)
for p in sorted(OUT.glob('slide_*.jpg')):
    print(p.name, p.stat().st_size)
