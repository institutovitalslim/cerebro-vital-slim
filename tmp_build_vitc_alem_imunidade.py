from pathlib import Path
import subprocess, json
from PIL import Image

OUT = Path('/root/cerebro-vital-slim/deliverables/vitamina-c-alem-da-imunidade-2026-04-21')
OUT.mkdir(parents=True, exist_ok=True)
TMP = OUT / 'tmp'
TMP.mkdir(exist_ok=True)

MAKE = '/root/.openclaw/workspace/skills/tweet-carrossel/scripts/make_cover.py'
SLIDES_SCRIPT = '/root/.openclaw/workspace/skills/tweet-carrossel/scripts/make_tweet_slides.py'
AVATAR = '/root/.openclaw/media/inbound/avatar_dradaniely_oficial.png'
FOTO = '/root/.openclaw/media/tool-image-generation/dra_vitc_contextual---9e1792cc-cd59-41eb-b07b-27d3c540bd31.jpg'
CIRCULO = '/root/.openclaw/media/tool-image-generation/vitc_circle---ca24d8ae-c456-4ad2-a84d-3bfd3f286c80.jpg'

headline = 'VITAMINA C|ALÉM DA|IMUNIDADE'
destaques = 'VITAMINA,ALÉM,IMUNIDADE'

subprocess.run(['python3', MAKE, '--foto', FOTO, '--circulo', CIRCULO, '--headline', headline, '--destaques', destaques, '--out', str(OUT/'slide_01.jpg')], check=True)

slides = [
  {'num': 2, 'paragraphs': [
    'Muita gente ainda reduz vitamina C a resfriado e defesa imune.',
    'Mas a literatura mostra que o papel dela vai muito além disso.',
    'Fonte: PMID 38187788'
  ]},
  {'num': 3, 'paragraphs': [
    'A vitamina C atua como antioxidante',
    'e também como cofator de enzimas importantes para o funcionamento saudável do organismo.',
    'Fonte: PMID 38187788 | PMID 39062764'
  ]},
  {'num': 4, 'paragraphs': [
    'Ela participa de processos ligados a:',
    'síntese de colágeno, integridade dos tecidos, recuperação tecidual e homeostase metabólica.',
    'Fonte: PMID 38187788'
  ]},
  {'num': 5, 'paragraphs': [
    'Ou seja:',
    'vitamina C não conversa só com imunidade.',
    'Ela também conversa com pele, vasos, tecido conjuntivo e recuperação.',
    'Fonte: PMID 38187788'
  ]},
  {'num': 6, 'paragraphs': [
    'Outro ponto importante:',
    'alguns contextos aumentam o risco de status inadequado de vitamina C, como obesidade, tabagismo, dieta pobre em alimentos in natura e maior estresse oxidativo.',
    'Fonte: PMID 38187788 | PMID 39062764'
  ]},
  {'num': 7, 'paragraphs': [
    'Na prática, isso significa que a necessidade não é igual para todo mundo.',
    'Peso corporal, estilo de vida e contexto clínico mudam esse raciocínio.',
    'Fonte: PMID 38187788 | PMID 39062764'
  ]},
  {'num': 8, 'paragraphs': [
    'Em cenários específicos, a vitamina C também tem sido estudada como apoio terapêutico.',
    'Exemplo: em cirurgia ortopédica, houve redução de analgesia de resgate e melhora precoce de dor em um estudo clínico.',
    'Fonte: PMID 39487511'
  ]},
  {'num': 9, 'paragraphs': [
    'Mas atenção:',
    'isso não significa que vitamina C seja solução universal, nem que toda pessoa precise usar forma injetável.',
    'Base: interpretação clínica dos artigos acima'
  ]},
  {'num': 10, 'paragraphs': [
    'Antes de pensar em usar, a pergunta certa é:',
    'em qual contexto a vitamina C realmente faz sentido para você?',
    'Salve este carrossel e envie para alguém que ainda acha que vitamina C é só imunidade.'
  ]},
]
slides_json = TMP/'slides.json'
slides_json.write_text(json.dumps(slides, ensure_ascii=False, indent=2), encoding='utf-8')
png_dir = TMP/'png'
png_dir.mkdir(exist_ok=True)
subprocess.run(['python3', SLIDES_SCRIPT, '--config', str(slides_json), '--avatar', AVATAR, '--out', str(png_dir), '--name', 'Dra. Daniely Freitas', '--handle', '@dradaniely.freitas'], check=True)
for png in sorted(png_dir.glob('slide_*.png')):
    Image.open(png).convert('RGB').save(OUT/f'{png.stem}.jpg', 'JPEG', quality=85, optimize=True, progressive=True)
print(OUT)
for p in sorted(OUT.glob('slide_*.jpg')):
    print(p.name)
