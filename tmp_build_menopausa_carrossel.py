from pathlib import Path
from io import BytesIO
import subprocess, json, requests, base64
from PIL import Image, ImageFilter, ImageEnhance

OUT = Path('/root/cerebro-vital-slim/deliverables/menopausa-nutrientes-carrossel-2026-04-21')
OUT.mkdir(parents=True, exist_ok=True)
TMP = OUT / 'tmp'
TMP.mkdir(exist_ok=True)

FOTO = Path('/root/.openclaw/workspace/fotos_dra/originais/seria_lateralizada.png')
CIRCULO = Path('/root/.openclaw/media/tool-image-generation/menopausa_nutrientes_circle---046136d8-41df-4cce-a575-93a6035a4429.jpg')
AVATAR = Path('/root/.openclaw/media/inbound/avatar_dradaniely_oficial.png')
SLIDES_SCRIPT = '/root/.openclaw/workspace/skills/tweet-carrossel/scripts/make_tweet_slides.py'
HEADLINE = ['NUTRIENTES QUE','PODEM AJUDAR','A MULHER NA','MENOPAUSA']
BG_QUERY = 'elegant women health clinic dark beige'

slides = [
  {'num': 2, 'paragraphs': ['Na menopausa, a queda do estrogênio pode repercutir em osso, músculo, pele, humor, sono, cognição e metabolismo.','Por isso, alguns nutrientes passam a ser ainda mais relevantes nessa fase.','Ref.: PubMed | menopause nutrition review']},
  {'num': 3, 'paragraphs': ['Vitamina D','A base científica mais sólida está aqui, principalmente para saúde óssea e muscular.','Em mulheres na pós-menopausa, manter níveis adequados é uma peça importante na prevenção de perda óssea e fragilidade.','Ref.: PubMed | vitamin D | postmenopausal bone health']},
  {'num': 4, 'paragraphs': ['Cálcio + Vitamina D','Diretrizes e revisões mostram que essa dupla pode ser importante no contexto certo, especialmente quando há ingestão insuficiente, risco de osteopenia ou osteoporose.','Ref.: PubMed | calcium + vitamin D | postmenopausal bone']},
  {'num': 5, 'paragraphs': ['Magnésio','O magnésio participa de função neuromuscular, metabolismo energético e saúde óssea.','Ele também entra no raciocínio clínico quando há piora de sono, tensão, fadiga ou baixa ingestão alimentar.','Ref.: PubMed | magnesium | menopause review']},
  {'num': 6, 'paragraphs': ['Vitamina B12','É importante para função neurológica, energia e produção de células sanguíneas.','Faz ainda mais sentido investigar quando há fadiga, piora cognitiva, dieta restritiva, gastrite, uso de metformina ou antiácidos.','Ref.: PubMed | vitamin B12 | fatigue cognition review']},
  {'num': 7, 'paragraphs': ['Vitamina C','Participa da defesa antioxidante e da síntese de colágeno.','Não é a vitamina da menopausa, mas pode conversar com pele, envelhecimento e recuperação tecidual dentro do contexto global.','Ref.: PubMed | vitamin C | collagen skin aging']},
  {'num': 8, 'paragraphs': ['Ômega-3 e Coenzima Q10','Podem entrar como coadjuvantes em contextos específicos, especialmente quando pensamos em inflamação, saúde cardiovascular, fadiga e bem-estar metabólico.','Ref.: PubMed | omega-3 review | CoQ10 review']},
  {'num': 9, 'paragraphs': ['Mas aqui está o ponto central:','a ciência não sustenta suplementação genérica para toda mulher.','O que faz sentido é reposição guiada por sintomas, alimentação, exames e contexto metabólico.','Ref.: PubMed | personalized nutrition | menopause']},
  {'num': 10, 'paragraphs': ['Na menopausa, não basta tomar mais.','É preciso corrigir melhor.','Salve este post.']},
]

def data_uri(path: Path) -> str:
    mime = 'image/png' if path.suffix.lower()=='.png' else 'image/jpeg'
    return f'data:{mime};base64,' + base64.b64encode(path.read_bytes()).decode('ascii')

# background
resp = requests.get('https://unsplash.com/napi/search/photos', params={'query': BG_QUERY, 'per_page': 10, 'orientation': 'landscape'}, timeout=20)
resp.raise_for_status()
results = resp.json().get('results', [])
img_bytes = requests.get(results[0]['urls']['regular'], timeout=30).content
bg = Image.open(BytesIO(img_bytes)).convert('RGB')
bg = bg.resize((1080, 1350), Image.LANCZOS)
bg = bg.filter(ImageFilter.GaussianBlur(radius=10))
bg = ImageEnhance.Brightness(bg).enhance(0.32)
bg_path = TMP / 'bg_full.jpg'
bg.save(bg_path, 'JPEG', quality=88, optimize=True)

# cover html
cover_html = TMP / 'cover.html'
cover_png = TMP / 'cover.png'
html = f'''<!doctype html><html><head><meta charset="utf-8"><style>
*{{box-sizing:border-box}} html,body{{margin:0;width:1080px;height:1350px;overflow:hidden;background:#000;font-family:Arial,sans-serif}}
.wrap{{position:relative;width:1080px;height:1350px;overflow:hidden}}
.bg{{position:absolute;inset:0;background:url({data_uri(bg_path)}) center/cover no-repeat;filter:brightness(.7)}}
.overlay{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.15),rgba(0,0,0,.55) 55%, rgba(0,0,0,.92) 100%)}}
.photo{{position:absolute;left:30px;bottom:0;width:650px;height:1180px;background:url({data_uri(FOTO)}) bottom left/contain no-repeat;filter:drop-shadow(0 12px 22px rgba(0,0,0,.35))}}
.circle{{position:absolute;right:90px;top:120px;width:350px;height:350px;border-radius:50%;background:url({data_uri(CIRCULO)}) center/cover no-repeat;box-shadow:0 16px 34px rgba(0,0,0,.35);border:6px solid rgba(255,255,255,.12)}}
.line{{position:absolute;left:0;right:0;top:560px;height:4px;background:linear-gradient(90deg,transparent,#caa56a,transparent)}}
.text{{position:absolute;left:68px;bottom:140px;color:#fff;max-width:720px;font-weight:800;line-height:.96;letter-spacing:-2px}}
.text div{{font-size:84px;margin:6px 0}}
.gold{{color:#d5a95d}}
</style></head><body><div class="wrap"><div class="bg"></div><div class="overlay"></div><div class="circle"></div><div class="line"></div><div class="photo"></div><div class="text"><div>{HEADLINE[0]}</div><div class="gold">{HEADLINE[1]}</div><div>{HEADLINE[2]}</div><div class="gold">{HEADLINE[3]}</div></div></div></body></html>'''
cover_html.write_text(html, encoding='utf-8')
subprocess.run(['google-chrome','--headless=new','--disable-gpu','--no-sandbox','--hide-scrollbars','--window-size=1080,1350',f'--screenshot={cover_png}',f'file://{cover_html}'], check=True)
img = Image.open(cover_png).convert('RGB'); img.save(OUT / 'slide_01.jpg','JPEG',quality=88,optimize=True,progressive=True)

slides_json = TMP / 'slides.json'
slides_json.write_text(json.dumps(slides, ensure_ascii=False, indent=2), encoding='utf-8')
png_out = TMP / 'png'; png_out.mkdir(exist_ok=True)
subprocess.run(['python3',SLIDES_SCRIPT,'--config',str(slides_json),'--avatar',str(AVATAR),'--out',str(png_out),'--name','Dra. Daniely Freitas','--handle','@dradaniely.freitas'], check=True)
for png in sorted(png_out.glob('slide_*.png')):
    img = Image.open(png).convert('RGB')
    img.save(OUT / f'{png.stem}.jpg','JPEG',quality=85,optimize=True,progressive=True)

print(OUT)
for p in sorted(OUT.glob('slide_*.jpg')): print(p.name)
