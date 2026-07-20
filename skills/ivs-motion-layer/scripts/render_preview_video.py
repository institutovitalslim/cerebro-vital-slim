#!/usr/bin/env python3
"""Gera preview MP4 premium da IVS Motion Layer.

Objetivo: provar movimento com estética médica premium — sem faixas agressivas,
sem poluição visual e sem parecer template genérico de startup.
"""
from __future__ import annotations

import math
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = Path('/root/cerebro-vital-slim/skills/ivs-motion-layer/examples/demo-apresentacao-ivs-motion-preview.mp4')
W, H = 1440, 900
FPS, DUR = 30, 7
BG = (7, 12, 13)
PANEL = (18, 24, 23)
PANEL_SOFT = (28, 34, 32)
TEXT = (246, 239, 226)
MUTED = (174, 168, 154)
GOLD = (210, 174, 98)
GOLD_LIGHT = (238, 211, 151)
GREEN = (116, 176, 142)
LINE = (82, 72, 52)

FONT_DIR = Path('/usr/share/fonts/truetype/dejavu')
SERIF_BOLD = ImageFont.truetype(str(FONT_DIR / 'DejaVuSerif-Bold.ttf'), 62)
SERIF_MED = ImageFont.truetype(str(FONT_DIR / 'DejaVuSerif.ttf'), 38)
SANS_BOLD = ImageFont.truetype(str(FONT_DIR / 'DejaVuSans-Bold.ttf'), 32)
SANS = ImageFont.truetype(str(FONT_DIR / 'DejaVuSans.ttf'), 24)
SMALL = ImageFont.truetype(str(FONT_DIR / 'DejaVuSans.ttf'), 18)
TINY = ImageFont.truetype(str(FONT_DIR / 'DejaVuSans.ttf'), 15)


def ease(x: float) -> float:
    x = max(0.0, min(1.0, x))
    return 1 - pow(1 - x, 3)


def draw_text(draw: ImageDraw.ImageDraw, xy: tuple[int, int], s: str, font: ImageFont.FreeTypeFont, fill: tuple[int, int, int], anchor=None):
    draw.text(xy, s, font=font, fill=fill + (255,), anchor=anchor)


def rounded(draw: ImageDraw.ImageDraw, xy, r, fill, outline=None, width=1):
    draw.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=width)


def wrap(draw: ImageDraw.ImageDraw, s: str, font, maxw: int) -> list[str]:
    lines, cur = [], ''
    for word in s.split():
        test = (cur + ' ' + word).strip()
        if draw.textbbox((0, 0), test, font=font)[2] <= maxw:
            cur = test
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def gradient_bg(t: float) -> Image.Image:
    base = Image.new('RGBA', (W, H), BG + (255,))
    glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)

    # Soft moving aurora, premium and slow.
    orbs = [
        (230 + math.sin(t * .65) * 54, 170 + math.cos(t * .55) * 28, 340, GOLD, 35),
        (1110 + math.sin(t * .48 + 1.8) * 68, 285 + math.cos(t * .5) * 42, 420, GREEN, 28),
        (850 + math.sin(t * .42 + 3) * 42, 760 + math.cos(t * .39) * 30, 360, GOLD_LIGHT, 18),
    ]
    for cx, cy, size, color, alpha in orbs:
        gd.ellipse((cx - size, cy - size, cx + size, cy + size), fill=color + (alpha,))
    glow = glow.filter(ImageFilter.GaussianBlur(65))
    return Image.alpha_composite(base, glow)


def draw_metric_card(d, x, y, w, h, title, value, suffix, note, progress, t, delay):
    p = ease((t - delay) / .85)
    yy = y + int((1 - p) * 34)
    alpha = int(255 * p)
    shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    rounded(sd, (x + 8, yy + 18, x + w + 8, yy + h + 18), 26, (0, 0, 0, int(58 * p)))
    return_shadow = shadow.filter(ImageFilter.GaussianBlur(20))

    rounded(d, (x, yy, x + w, yy + h), 26, PANEL + (220,), (105, 87, 53, int(110 * p)), 1)
    # subtle border light
    sweep = (math.sin(t * 1.15 + delay * 2) + 1) / 2
    d.line((x + 28, yy + h - 1, x + 28 + int((w - 56) * sweep), yy + h - 1), fill=GOLD + (int(120 * p),), width=2)
    draw_text(d, (x + 28, yy + 26), title.upper(), TINY, MUTED)
    current = value * ease((t - delay - .35) / 1.25)
    if isinstance(value, float) and not value.is_integer():
        val_s = f'{current:.1f}'.replace('.', ',')
    else:
        val_s = f'{int(current)}'
    draw_text(d, (x + 28, yy + 62), val_s + suffix, SANS_BOLD, GOLD_LIGHT)
    draw_text(d, (x + 28, yy + 105), note, SMALL, MUTED)
    # progress
    bar_y = yy + h - 38
    rounded(d, (x + 28, bar_y, x + w - 28, bar_y + 8), 4, (255, 255, 255, int(26 * p)))
    pw = int((w - 56) * progress * ease((t - delay - .55) / 1.15))
    rounded(d, (x + 28, bar_y, x + 28 + pw, bar_y + 8), 4, GOLD + (alpha,))
    return return_shadow


def frame(t: float) -> Image.Image:
    im = gradient_bg(t)
    d = ImageDraw.Draw(im)

    # Editorial frame lines.
    d.line((76, 78, W - 76, 78), fill=LINE + (135,), width=1)
    d.line((76, H - 78, W - 76, H - 78), fill=LINE + (95,), width=1)
    d.ellipse((W - 194, 54, W - 146, 102), outline=GOLD + (150,), width=1)
    d.ellipse((W - 181, 67, W - 159, 89), fill=GOLD + (110,))

    # Header.
    draw_text(d, (86, 106), 'INSTITUTO VITAL SLIM', SMALL, GOLD)
    draw_text(d, (86, 132), 'motion layer para apresentações premium', TINY, MUTED)

    title = 'Presença visual premium sem perder clareza clínica.'
    title_lines = wrap(d, title, SERIF_BOLD, 830)
    y = 194
    for idx, line in enumerate(title_lines):
        p = ease((t - .18 - idx * .13) / .7)
        x = 86 + int((1 - p) * -34)
        yy = y + idx * 70
        draw_text(d, (x, yy), line, SERIF_BOLD, TEXT)

    subtitle_p = ease((t - .85) / .75)
    subtitle = 'Scroll suave, entrada de seções, métricas animadas e fundos ambientais discretos — com fallback e reduced motion.'
    for n, line in enumerate(wrap(d, subtitle, SANS, 760)):
        draw_text(d, (88, 430 + n * 32 + int((1 - subtitle_p) * 14)), line, SANS, MUTED)

    # Pills/chips.
    chips = [('Lenis', 'scroll'), ('GSAP', 'timelines'), ('Vanta', 'ambient'), ('IVS', 'fallback')]
    cx = 88
    for i, (a, b) in enumerate(chips):
        p = ease((t - 1.05 - i * .08) / .55)
        yy = 518 + math.sin(t * 1.8 + i) * 4
        w = 118
        rounded(d, (cx, yy, cx + w, yy + 40), 20, (255, 255, 255, int(18 * p)), (210, 174, 98, int(70 * p)), 1)
        draw_text(d, (cx + 18, int(yy + 10)), a, SMALL, GOLD_LIGHT)
        draw_text(d, (cx + 68, int(yy + 10)), b, TINY, MUTED)
        cx += w + 12

    # Metric cards with shadows composed behind.
    shadows = []
    shadows.append(draw_metric_card(d, 86, 604, 360, 160, 'Evolução', 21.6, ' kg', 'counter animado com sobriedade', .82, t, 1.45))
    shadows.append(draw_metric_card(d, 500, 604, 360, 160, 'Aderência', 92, '%', 'progresso visual sem exagero', .92, t, 1.62))
    shadows.append(draw_metric_card(d, 914, 604, 360, 160, 'Jornada', 6, ' meses', 'linha narrativa da apresentação', .68, t, 1.79))

    # Right-side soft presentation mockup.
    p = ease((t - .95) / .9)
    px, py = 985 + int((1 - p) * 48), 176
    rounded(d, (px, py, px + 290, py + 245), 28, (246, 239, 226, int(18 * p)), (210, 174, 98, int(85 * p)), 1)
    draw_text(d, (px + 28, py + 30), 'PREVIEW', TINY, GOLD)
    draw_text(d, (px + 28, py + 62), 'Apresentação', SERIF_MED, TEXT)
    for j, width in enumerate([210, 168, 238]):
        rounded(d, (px + 28, py + 124 + j * 34, px + 28 + width, py + 135 + j * 34), 5, (255, 255, 255, int(35 * p)))
    # animated gold cursor/progress dot
    dotx = px + 34 + int(220 * ((math.sin(t * 1.4) + 1) / 2))
    d.ellipse((dotx - 6, py + 210 - 6, dotx + 6, py + 210 + 6), fill=GOLD + (int(230 * p),))

    return im.convert('RGB')


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        for i in range(FPS * DUR):
            t = i / FPS
            frame(t).save(td_path / f'frame_{i:04d}.png')
        subprocess.run([
            'ffmpeg', '-y', '-framerate', str(FPS), '-i', str(td_path / 'frame_%04d.png'),
            '-vf', 'format=yuv420p', '-movflags', '+faststart', str(OUT)
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(OUT)


if __name__ == '__main__':
    main()
