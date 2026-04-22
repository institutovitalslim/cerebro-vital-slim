from PIL import Image, ImageFilter, ImageEnhance, ImageDraw
from pathlib import Path

cover_path = Path('/root/cerebro-vital-slim/deliverables/menopausa-nutrientes-carrossel-2026-04-21/slide_01.jpg')
logo_path = Path('/root/cerebro-vital-slim/cerebro/assets/identidade-visual/logo-negativo-transparente.png')

img = Image.open(cover_path).convert('RGBA')
# stronger full replacement over foreign branding area
patch = Image.new('RGBA', img.size, (0,0,0,0))
d = ImageDraw.Draw(patch)
d.rounded_rectangle((640, 95, 1055, 470), radius=34, fill=(34, 24, 20, 245))
patch = patch.filter(ImageFilter.GaussianBlur(radius=4))
img = Image.alpha_composite(img, patch)

logo = Image.open(logo_path).convert('RGBA')
# resize larger so the foreign brand is fully replaced
max_w, max_h = 335, 335
ratio = min(max_w / logo.width, max_h / logo.height)
logo = logo.resize((int(logo.width * ratio), int(logo.height * ratio)), Image.LANCZOS)
# slight brighten
r,g,b,a = logo.split()
logo = Image.merge('RGBA', (
    ImageEnhance.Brightness(r).enhance(1.08),
    ImageEnhance.Brightness(g).enhance(1.08),
    ImageEnhance.Brightness(b).enhance(1.08),
    a,
))
# centered in replacement area
x = 680
y = 120
img.alpha_composite(logo, (x, y))

img.convert('RGB').save(cover_path, 'JPEG', quality=90, optimize=True, progressive=True)
print(cover_path)
