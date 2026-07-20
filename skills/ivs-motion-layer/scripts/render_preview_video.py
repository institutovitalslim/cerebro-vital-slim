#!/usr/bin/env python3
"""Gera preview MP4 da IVS Motion Layer para validação em canais que não executam HTML."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math
import subprocess
import tempfile

OUT = Path('/root/cerebro-vital-slim/skills/ivs-motion-layer/examples/demo-apresentacao-ivs-motion-preview.mp4')
W, H = 1280, 720
FPS, DUR = 24, 5
BG = (8, 15, 16)
GOLD = (214, 180, 108)
TEXT = (247, 242, 232)
MUTED = (184, 192, 186)
GREEN = (120, 200, 157)

try:
    FONT_BIG = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 56)
    FONT_MED = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 34)
    FONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 24)
    FONT_SMALL = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 18)
except Exception:
    FONT_BIG = FONT_MED = FONT = FONT_SMALL = ImageFont.load_default()


def rounded(draw, xy, r, fill, outline=None, width=1):
    draw.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=width)


def text(draw, xy, s, font, fill):
    draw.text(xy, s, font=font, fill=fill)


def wrap(s, font, maxw):
    words, lines, cur = s.split(), [], ''
    for w in words:
        test = (cur + ' ' + w).strip()
        if ImageDraw.Draw(Image.new('RGB',(1,1))).textbbox((0,0), test, font=font)[2] <= maxw:
            cur = test
        else:
            lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

with tempfile.TemporaryDirectory() as td:
    frames = []
    for i in range(FPS * DUR):
        t = i / FPS
        im = Image.new('RGB', (W, H), BG)
        overlay = Image.new('RGBA', (W, H), (0,0,0,0))
        od = ImageDraw.Draw(overlay)
        # moving blurred orbs
        for cx, cy, color, phase in [(180,150,GOLD,0), (1040,510,GREEN,1.7)]:
            x = cx + math.sin(t*1.1+phase)*80
            y = cy + math.cos(t*.9+phase)*45
            od.ellipse((x-220,y-220,x+220,y+220), fill=color+(38,))
        overlay = overlay.filter(ImageFilter.GaussianBlur(36))
        im = Image.alpha_composite(im.convert('RGBA'), overlay)
        d = ImageDraw.Draw(im)
        # sheen
        sheen_x = -500 + (t/DUR)*1900
        d.polygon([(sheen_x,0),(sheen_x+180,0),(sheen_x-120,H),(sheen_x-300,H)], fill=(255,255,255,18))
        text(d, (70,72), 'INSTITUTO VITAL SLIM · MOTION LAYER', FONT_SMALL, GOLD+(255,))
        title = 'Apresentações clínicas com presença premium, clareza e movimento controlado.'
        y=118
        for idx,line in enumerate(wrap(title, FONT_BIG, 930)):
            offset = max(0, 1 - (t - idx*.16)/.55)
            text(d, (70, y + int(offset*28)), line, FONT_BIG, TEXT+(255,))
            y += 64
        text(d, (72, y+10), 'Preview em vídeo: chips flutuam, cards brilham, counters e barras animam.', FONT, MUTED+(255,))
        # chips floating
        chips = ['Lenis scroll', 'GSAP counters', 'Vanta ambient', 'CSS fallback']
        x=72; cy=y+64
        for n,ch in enumerate(chips):
            yy = cy + math.sin(t*2+n)*8
            tw = d.textbbox((0,0), ch, font=FONT_SMALL)[2]
            rounded(d, (x, yy, x+tw+30, yy+36), 18, (247,242,232,18), (214,180,108,90), 1)
            text(d, (x+15, yy+8), ch, FONT_SMALL, MUTED+(255,))
            x += tw+46
        # metrics cards enter
        base_y=470
        vals=[21.6,92,6]
        labels=['kg em jornada visual','% de progresso demonstrativo','meses de acompanhamento']
        for n in range(3):
            enter = min(1, max(0, (t-.6-n*.18)/.7))
            yy = base_y + (1-enter)*50
            xx = 70+n*385
            rounded(d, (xx, yy, xx+340, yy+160), 24, (255,255,255,18), (255,255,255,42), 1)
            # moving card sheen
            sx = xx-240 + ((t*180+n*70) % 720)
            d.polygon([(sx,yy),(sx+70,yy),(sx-30,yy+160),(sx-100,yy+160)], fill=(214,180,108,35))
            val = vals[n]*min(1, max(0,(t-1.2-n*.2)/1.4))
            suffix = [' kg','%',' meses'][n]
            shown = f'{val:.1f}{suffix}' if n==0 else f'{int(val)}{suffix}'
            text(d, (xx+24, yy+24), shown, FONT_MED, GOLD+(255,))
            text(d, (xx+24, yy+75), labels[n], FONT_SMALL, MUTED+(255,))
            # progress line
            prog = min(1, max(0,(t-2.1-n*.12)/1.0))
            d.rounded_rectangle((xx+24, yy+120, xx+315, yy+130), radius=5, fill=(247,242,232,28))
            d.rounded_rectangle((xx+24, yy+120, xx+24+291*prog, yy+130), radius=5, fill=GOLD+(255,))
        frame = Path(td)/f'frame_{i:04d}.png'
        im.convert('RGB').save(frame)
        frames.append(frame)
    subprocess.run(['ffmpeg','-y','-framerate',str(FPS),'-i',str(Path(td)/'frame_%04d.png'),'-vf','format=yuv420p','-movflags','+faststart',str(OUT)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print(OUT)
