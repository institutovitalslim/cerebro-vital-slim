from PIL import Image, ImageFilter, ImageEnhance, ImageDraw
from pathlib import Path

cover_path = Path('/root/cerebro-vital-slim/deliverables/menopausa-nutrientes-carrossel-2026-04-21/slide_01.jpg')
logo_path = Path('/root/cerebro-vital-slim/cerebro/assets/identidade-visual/logo-negativo-transparente.png')

img = Image.open(cover_path).convert('RGBA')
# dark patch over foreign clinic branding area
patch = Image.new('RGBA', img.size, (0,0,0,0))
d = ImageDraw.Draw(patch)
d.rounded_rectangle((655, 110, 1045, 435), radius=30, fill=(25, 18, 15, 230))
patch = patch.filter(ImageFilter.GaussianBlur(radius=6))
img = Image.alpha_composite(img, patch)

logo = Image.open(logo_path).convert('RGBA')
# resize preserving aspect
max_w, max_h = 300, 220
ratio = min(max_w / logo.width, max_h / logo.height)
logo = logo.resize((int(logo.width * ratio), int(logo.height * ratio)), Image.LANCZOS)
# slightly brighten logo
r,g,b,a = logo.split()
logo = Image.merge('RGBA', (ImageEnhance.Brightness(r).enhance(1.05), ImageEnhance.Brightness(g).enhance(1.05), ImageEnhance.Brightness(b).enhance(1.05), a))
# place centered in patched area
x = 700
y = 150
img.alpha_composite(logo, (x,y))

img.convert('RGB').save(cover_path, 'JPEG', quality=88, optimize=True, progressive=True)
print(cover_path)
