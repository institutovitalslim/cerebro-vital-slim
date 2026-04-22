from pathlib import Path
import subprocess

OUT = Path('/root/cerebro-vital-slim/deliverables/menopausa-nutrientes-carrossel-2026-04-21/slide_01.jpg')
FOTO = Path('/root/.openclaw/media/tool-image-generation/dra_menopausa_contextual---a9781ee1-7e7f-48ae-aa9d-617986a96ea1.jpg')
CIRCULO = Path('/root/.openclaw/media/tool-image-generation/menopausa_nutrientes_circle---046136d8-41df-4cce-a575-93a6035a4429.jpg')
MAKE = '/root/.openclaw/workspace/skills/tweet-carrossel/scripts/make_cover.py'
HEADLINE = 'NUTRIENTES QUE|PODEM AJUDAR|A MULHER NA|MENOPAUSA'
DESTAQUES = 'PODEM,AJUDAR,MENOPAUSA'
subprocess.run(['python3', MAKE,'--foto', str(FOTO),'--circulo', str(CIRCULO),'--headline', HEADLINE,'--destaques', DESTAQUES,'--out', str(OUT)], check=True)
print(OUT)
