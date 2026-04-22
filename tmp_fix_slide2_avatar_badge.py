from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Config
W, H = 1080, 1350
BG = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (140, 150, 145)
VERIFIED_BG = (29, 155, 240)
MARGIN_L = 64
MARGIN_R = 64
AVATAR_SIZE = 56
NAME_SIZE = 30
HANDLE_SIZE = 26
BODY_SIZE = 34

SKILL_DIR = Path('/root/.openclaw/workspace/skills/tweet-carrossel')
FONT_BOLD = SKILL_DIR / 'assets/DejaVuSans-Bold.ttf'
FONT_REG = SKILL_DIR / 'assets/DejaVuSans.ttf'

def get_font(size, bold=False):
    path = FONT_BOLD if bold else FONT_REG
    if path.exists():
        return ImageFont.truetype(str(path), size)
    sys_bold = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    sys_reg = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    try:
        return ImageFont.truetype(sys_bold if bold else sys_reg, size)
    except:
        return ImageFont.load_default()

def make_circular_avatar(path, size):
    av = Image.open(path).convert('RGBA').resize((size, size), Image.LANCZOS)
    mask = Image.new('L', (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size, size), fill=255)
    out = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    out.paste(av, mask=mask)
    return out

def draw_verified(draw, x, y, size=18):
    draw.ellipse((x, y, x+size, y+size), fill=VERIFIED_BG)
    cx, cy = x + size//2, y + size//2
    draw.line([(cx-4, cy), (cx-1, cy+3)], fill=WHITE, width=2)
    draw.line([(cx-1, cy+3), (cx+4, cy-3)], fill=WHITE, width=2)

def wrap_text(text, font, max_width):
    d = ImageDraw.Draw(Image.new('RGB', (1, 1)))
    words = text.split(' ')
    lines, current = [], ''
    for w in words:
        test = (current + ' ' + w).strip()
        if d.textbbox((0, 0), test, font=font)[2] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines

# Avatar oficial
avatar_path = Path('/root/.openclaw/media/inbound/avatar_dradaniely_oficial.png')
av = make_circular_avatar(avatar_path, AVATAR_SIZE)

name = 'Dra. Daniely Freitas'
handle = '@dradaniely.freitas'
paragraphs = [
    'E se eu te dissesse que um aminoácido simples pode:',
    '',
    '→ Aumentar sua expectativa de vida',
    '→ Apagar a inflamação crônica',
    '→ Curar seu intestino',
    '→ Fazer você dormir como um bebê'
]

font_name = get_font(NAME_SIZE, bold=True)
font_handle = get_font(HANDLE_SIZE)
font_body = get_font(BODY_SIZE)
max_text_w = W - MARGIN_L - MARGIN_R

# Measure
fh_body = ImageDraw.Draw(Image.new('RGB', (1, 1))).textbbox((0, 0), 'A', font=font_body)[3]
fh_name = ImageDraw.Draw(Image.new('RGB', (1, 1))).textbbox((0, 0), 'A', font=font_name)[3]
fh_handle = ImageDraw.Draw(Image.new('RGB', (1, 1))).textbbox((0, 0), 'A', font=font_handle)[3]
lh = int(fh_body * 1.45)
header_h = max(AVATAR_SIZE, fh_name + 8 + fh_handle)

body_h = 0
for i, para in enumerate(paragraphs):
    if i > 0:
        body_h += int(fh_body * 0.5) if para == '' else int(fh_body * 0.8)
    if para == '':
        body_h += int(fh_body * 0.5)
        continue
    body_h += len(wrap_text(para, font_body, max_text_w)) * lh

total_h = header_h + 28 + body_h
y_start = max(40, (H - total_h) // 2)

# Render
img = Image.new('RGB', (W, H), BG)
img_rgba = img.convert('RGBA')
img_rgba.paste(av, (MARGIN_L, y_start), av)
img = img_rgba.convert('RGB')
draw = ImageDraw.Draw(img)

# Name with proper spacing for verified badge
name_x = MARGIN_L + AVATAR_SIZE + 14
name_y = y_start + 2
draw.text((name_x, name_y), name, font=font_name, fill=WHITE)

# Badge positioned with more margin to avoid overlap
nb = draw.textbbox((name_x, name_y), name, font=font_name)
badge_x = nb[2] + 10  # increased from 6 to 10
badge_y = name_y + 6
draw_verified(draw, badge_x, badge_y, 18)

# Handle
draw.text((name_x, name_y + fh_name + 6), handle, font=font_handle, fill=GRAY)

# Body
body_y = y_start + header_h + 28
for i, para in enumerate(paragraphs):
    if para == '':
        body_y += int(fh_body * 0.5)
        continue
    if i > 0:
        body_y += int(fh_body * 0.8)
    lines = wrap_text(para, font_body, max_text_w)
    for line in lines:
        draw.text((MARGIN_L, body_y), line, font=font_body, fill=WHITE)
        body_y += lh

out_path = Path('/root/cerebro-vital-slim/deliverables/slide_02_fixed_avatar_badge.jpg')
img.save(out_path, 'JPEG', quality=90, optimize=True, progressive=True)
print(out_path)
