from pathlib import Path
import json, base64, subprocess, shutil

ROOT = Path('/root/cerebro-vital-slim/deliverables/tweet-carrossel-v3-2026-04-14')
MAG = ROOT / 'magnesio'
CRE = ROOT / 'creatina'
MAG.mkdir(parents=True, exist_ok=True)
CRE.mkdir(parents=True, exist_ok=True)
AVATAR = Path('/root/.openclaw/media/inbound/avatar_dradaniely_oficial.png')
SLIDES_SCRIPT = '/root/.openclaw/workspace/skills/tweet-carrossel/scripts/make_tweet_slides.py'

mag_slides = [
  {
    'num': 3,
    'paragraphs': [
      'E isso não é raro.',
      '2,4 BILHÕES de pessoas no mundo com ingestão insuficiente de magnésio.',
      '31% da população mundial.',
      'E o pior: a maioria nem sabe. Você pode ser um deles.',
      'Mas o que isso causa no seu corpo? →'
    ]
  },
  {
    'num': 4,
    'paragraphs': [
      'O que a falta de magnésio causa:',
      '→ Cãibras e fadiga',
      '→ Insônia',
      '→ Constipação',
      '→ Enxaqueca',
      '→ Pressão descontrolada',
      '→ Resistência insulínica',
      '→ Risco cardiovascular',
      'E se existisse um jeito de investigar isso de verdade? →'
    ]
  },
  {
    'num': 5,
    'paragraphs': [
      'Na Vital Slim, não confiamos só no exame.',
      '1 Contexto clínico — Sintomas + história completa',
      '2 Mapa metabólico — Cruzamento de dados reais',
      '3 Protocolo individual — Baseado em evidência, não achismo',
      'Resultado não é sorte. É precisão clínica. →'
    ]
  },
  {
    'num': 6,
    'paragraphs': [
      'Seu corpo já está pedindo ajuda.',
      'Pare de adivinhar o que falta — descubra com precisão.',
      '[QUERO MINHA AVALIAÇÃO]',
      'Mande MAGNÉSIO no direct →'
    ]
  }
]

cre_slides = [
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

(MAG / 'slides.json').write_text(json.dumps(mag_slides, ensure_ascii=False, indent=2))
(CRE / 'slides.json').write_text(json.dumps(cre_slides, ensure_ascii=False, indent=2))

subprocess.run([
    'python3', SLIDES_SCRIPT,
    '--config', str(MAG / 'slides.json'),
    '--avatar', str(AVATAR),
    '--out', str(MAG),
    '--name', 'Dra. Daniely Freitas',
    '--handle', '@dradaniely.freitas'
], check=True)

subprocess.run([
    'python3', SLIDES_SCRIPT,
    '--config', str(CRE / 'slides.json'),
    '--avatar', str(AVATAR),
    '--out', str(CRE),
    '--name', 'Dra. Daniely Freitas',
    '--handle', '@dradaniely.freitas'
], check=True)


def screenshot_pubmed(url: str, out_path: Path):
    subprocess.run([
        'google-chrome', '--headless=new', '--disable-gpu', '--no-sandbox', '--hide-scrollbars',
        '--window-size=1400,1700', f'--screenshot={out_path}', url
    ], check=True)


def data_uri(path: Path) -> str:
    mime = 'image/png' if path.suffix.lower() == '.png' else 'image/jpeg'
    return f'data:{mime};base64,' + base64.b64encode(path.read_bytes()).decode('ascii')


def render_slide2(out_dir: Path, screenshot_path: Path, tweet_text: str):
    avatar_uri = data_uri(AVATAR)
    shot_uri = data_uri(screenshot_path)
    html = f'''<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=1080, initial-scale=1">
<style>
  * {{ box-sizing: border-box; }}
  html, body {{ margin: 0; width: 1080px; height: 1350px; background: #000; overflow: hidden; font-family: Inter, Arial, sans-serif; }}
  body {{ color: #e8e8e8; }}
  .wrap {{ width: 1080px; height: 1350px; padding: 42px 48px 44px; position: relative; }}
  .header {{ display: flex; align-items: center; gap: 18px; margin-bottom: 26px; }}
  .avatar {{ width: 72px; height: 72px; border-radius: 50%; overflow: hidden; border: 2px solid #1d1d1d; flex: 0 0 auto; }}
  .avatar img {{ width: 100%; height: 100%; object-fit: cover; }}
  .meta {{ line-height: 1.1; }}
  .name {{ font-size: 28px; font-weight: 700; color: #fff; }}
  .handle {{ font-size: 22px; color: #8b8b8b; margin-top: 6px; }}
  .tweet {{ font-size: 38px; line-height: 1.22; color: #d5d5d5; font-weight: 500; letter-spacing: -0.02em; margin-bottom: 26px; }}
  .shot-card {{ width: 100%; border: 1px solid #242424; border-radius: 26px; overflow: hidden; background: #0c0c0c; box-shadow: 0 0 0 1px rgba(255,255,255,0.03) inset; }}
  .shot-card img {{ width: 100%; display: block; }}
  .footer {{ position: absolute; left: 48px; right: 48px; bottom: 34px; display: flex; align-items: center; justify-content: space-between; color: #6f6f6f; font-size: 18px; }}
  .dots {{ display: flex; gap: 8px; align-items: center; }}
  .dot {{ width: 7px; height: 7px; border-radius: 50%; background: #5a5a5a; }}
</style>
</head>
<body>
  <div class="wrap">
    <div class="header">
      <div class="avatar"><img src="{avatar_uri}" alt="avatar"></div>
      <div class="meta">
        <div class="name">Dra. Daniely Freitas</div>
        <div class="handle">@dradaniely.freitas</div>
      </div>
    </div>
    <div class="tweet">{tweet_text}</div>
    <div class="shot-card"><img src="{shot_uri}" alt="PubMed screenshot"></div>
    <div class="footer">
      <div>Vital Slim</div>
      <div class="dots"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>
    </div>
  </div>
</body>
</html>'''
    html_path = out_dir / 'slide_02.html'
    png_path = out_dir / 'slide_02.png'
    html_path.write_text(html, encoding='utf-8')
    subprocess.run([
        'google-chrome', '--headless=new', '--disable-gpu', '--no-sandbox', '--hide-scrollbars',
        '--window-size=1080,1350', f'--screenshot={png_path}', f'file://{html_path}'
    ], check=True)

mag_pubmed = MAG / 'pubmed_41504160.png'
cre_pubmed = CRE / 'pubmed_39070254.png'
screenshot_pubmed('https://pubmed.ncbi.nlm.nih.gov/41504160/', mag_pubmed)
screenshot_pubmed('https://pubmed.ncbi.nlm.nih.gov/39070254/', cre_pubmed)

render_slide2(
    MAG,
    mag_pubmed,
    'Este artigo mostra que a deficiência de magnésio é uma preocupação global subestimada. O próprio paper cita 2,4 bilhões de pessoas, cerca de 31% da população mundial, com ingestão insuficiente.'
)
render_slide2(
    CRE,
    cre_pubmed,
    'Este estudo reuniu 16 estudos clínicos randomizados, com 492 participantes, e encontrou melhora em memória, atenção e velocidade de processamento.'
)

print('OK', ROOT)
