from pathlib import Path
import subprocess
OUT = Path('/root/cerebro-vital-slim/deliverables/vitamina-c-alem-da-imunidade-2026-04-21/slide_01.jpg')
subprocess.run([
    'python3', '/root/.openclaw/workspace/skills/tweet-carrossel/scripts/make_cover.py',
    '--foto', '/root/.openclaw/media/tool-image-generation/dra_vitc_contextual---9e1792cc-cd59-41eb-b07b-27d3c540bd31.jpg',
    '--circulo', '/root/.openclaw/media/tool-image-generation/vitc_circle---ca24d8ae-c456-4ad2-a84d-3bfd3f286c80.jpg',
    '--headline', 'VITAMINA C|ALÉM DA|IMUNIDADE',
    '--destaques', 'VITAMINA,C',
    '--out', str(OUT)
], check=True)
print(OUT)
