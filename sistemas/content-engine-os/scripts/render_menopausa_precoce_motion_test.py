#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import os
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 540, 960
FPS = 24
DURATION = 45
FRAMES = FPS * DURATION

OUT = Path('/root/cerebro-vital-slim/sistemas/content-engine-os/storage/assets/renders/menopausa-precoce-motion-test-20260719')
FRAMES_DIR = OUT / 'frames'
VERIFY = OUT / 'verify'
FINAL = OUT / 'MENOPAUSA_PRECOCE_MOTION_TEST_45S.mp4'
FRAMES_DIR.mkdir(parents=True, exist_ok=True)
VERIFY.mkdir(parents=True, exist_ok=True)

GOLD = (207, 169, 84)
GOLD2 = (244, 215, 138)
BG1 = (10, 18, 30)
BG2 = (17, 31, 49)
TEXT = (247, 241, 227)
MUTED = (190, 199, 210)
RED = (255, 123, 109)
GREEN = (128, 215, 170)

BASE_BG = Image.new('RGB', (W, H), BG1)
_bg_draw = ImageDraw.Draw(BASE_BG)
for y in range(H):
    yy = y / H
    r = int(BG1[0] + (BG2[0]-BG1[0])*yy)
    g = int(BG1[1] + (BG2[1]-BG1[1])*yy)
    b = int(BG1[2] + (BG2[2]-BG1[2])*yy)
    _bg_draw.line((0, y, W, y), fill=(r, g, b))
_bg_draw.ellipse((-120, 90, 300, 510), fill=(18, 48, 74))
_bg_draw.ellipse((260, 460, 680, 920), fill=(40, 34, 52))
BASE_BG = BASE_BG.filter(ImageFilter.GaussianBlur(18))

try:
    FONT_BOLD = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 38)
    FONT_TITLE = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 40)
    FONT_MED = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 23)
    FONT_SMALL = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 21)
    FONT_TINY = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 17)
except Exception:
    FONT_BOLD = FONT_TITLE = FONT_MED = FONT_SMALL = FONT_TINY = ImageFont.load_default()

SCENES = [
    (0, 5, 'HOOK', 'MENOPAUSA\nPRECOCE', 'Não é “frescura” nem sentença.\nÉ um sinal que merece avaliação.'),
    (5, 12, 'SINAL', 'Antes dos\n40 anos', 'Ciclos que falham, ondas de calor,\nsono ruim e mudança de energia.'),
    (12, 20, 'MECANISMO', 'O corpo muda\no ritmo hormonal', 'Ovários, cérebro e metabolismo\nconversam com humor\ne composição corporal.'),
    (20, 29, 'ERRO COMUM', 'Não ignore\nnem se automedique', 'Sintoma parecido pode ter causas diferentes.\nReposição não é decisão de internet.'),
    (29, 38, 'AVALIAÇÃO', 'O caminho seguro\né investigar', 'História clínica, exames, risco individual\ne acompanhamento médico.'),
    (38, 45, 'CTA', 'Entender cedo\nmuda a rota', 'Conteúdo educativo.\nProcure avaliação médica individualizada.'),
]

NARRATION = """Menopausa precoce não é frescura, e também não é sentença.
Quando sinais aparecem antes dos quarenta anos, como ciclos falhando, ondas de calor, sono ruim ou mudança de energia, vale investigar.
O ponto central é que hormônios conversam com cérebro, metabolismo, humor e composição corporal.
O erro comum é ignorar por meses, ou tentar resolver com automedicação.
Sintomas parecidos podem ter causas diferentes.
O caminho seguro é avaliação médica individualizada, com história clínica, exames e acompanhamento.
Conteúdo educativo. Não substitui consulta."""


def lerp(a, b, t):
    return int(a + (b - a) * t)


def ease(x):
    return 0.5 - 0.5 * math.cos(math.pi * max(0, min(1, x)))


def draw_center(draw, text, y, font, fill=TEXT, spacing=8):
    lines = text.split('\n')
    cur = y
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        x = (W - (bbox[2] - bbox[0])) // 2
        draw.text((x, cur), line, font=font, fill=fill)
        cur += bbox[3] - bbox[1] + spacing


def rounded_rect(draw, xy, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def scene_at(t):
    for idx, (start, end, label, title, sub) in enumerate(SCENES):
        if start <= t < end:
            return idx, start, end, label, title, sub
    return len(SCENES)-1, *SCENES[-1]


def make_frame(i):
    t = i / FPS
    idx, start, end, label, title, sub = scene_at(t)
    local = (t - start) / max(0.1, end - start)
    img = BASE_BG.copy()

    overlay = Image.new('RGBA', (W, H), (0,0,0,0))
    od = ImageDraw.Draw(overlay)
    # orbiting abstract endocrine/metabolic circles
    for k in range(9):
        ang = t * 0.55 + k * math.tau / 9
        rad = 118 + 22 * math.sin(t * 0.7 + k)
        cx = W//2 + int(math.cos(ang) * rad)
        cy = 320 + int(math.sin(ang) * rad * 0.72)
        size = 13 + (k % 3) * 4
        col = GOLD if k % 2 == 0 else (90, 150, 180)
        alpha = 70 + int(45 * math.sin(t + k))
        od.ellipse((cx-size, cy-size, cx+size, cy+size), fill=(*col, alpha), outline=(*GOLD2, 90))
        od.line((W//2, 320, cx, cy), fill=(*GOLD, 25), width=1)

    # central organic symbol
    pulse = 1 + 0.05 * math.sin(t * 2.0)
    r = int(76 * pulse)
    od.ellipse((W//2-r, 320-r, W//2+r, 320+r), fill=(207,169,84,28), outline=(*GOLD,130), width=3)
    od.arc((W//2-48, 320-65, W//2+48, 320+65), 90, 270, fill=(*GOLD2,170), width=4)
    od.arc((W//2-48, 320-65, W//2+48, 320+65), -90, 90, fill=(*GREEN,150), width=4)

    # scene card
    card_y = int(122 + 18 * (1 - ease(min(local*1.4, 1))))
    rounded_rect(od, (38, card_y, W-38, 742), 28, (8, 16, 29, 188), outline=(207,169,84,90), width=2)
    rounded_rect(od, (62, card_y+28, 62+150, card_y+63), 16, (207,169,84,42), outline=(207,169,84,120), width=1)
    od.text((78, card_y+34), label, font=FONT_TINY, fill=GOLD2)
    od.text((62, 755), 'INSTITUTO VITAL SLIM', font=FONT_TINY, fill=(207,169,84,160))

    # timeline
    base_y = 858
    od.line((72, base_y, W-72, base_y), fill=(255,255,255,55), width=4)
    prog = min(1, t / DURATION)
    od.line((72, base_y, 72 + int((W-144)*prog), base_y), fill=(*GOLD2,210), width=5)
    for s, _, _, _, _ in SCENES:
        x = 72 + int((W-144) * s / DURATION)
        od.ellipse((x-4, base_y-4, x+4, base_y+4), fill=(*GOLD,180))

    img = Image.alpha_composite(img.convert('RGBA'), overlay)
    d = ImageDraw.Draw(img)

    # animated title alpha simulated via small vertical movement
    title_y = card_y + 92 + int(10 * (1 - ease(min(local*1.6,1))))
    draw_center(d, title, title_y, FONT_TITLE, fill=TEXT, spacing=4)
    draw_center(d, sub, title_y + 150, FONT_MED, fill=MUTED, spacing=8)

    # bottom disclaimer
    d.text((42, 895), 'Conteúdo educativo • não substitui consulta médica', font=FONT_TINY, fill=(220, 226, 235, 150))

    # scene-specific elements
    if idx == 1:
        for m in range(4):
            x = 115 + m*78
            y = 603 + int(8*math.sin(t*2+m))
            rounded_rect(d, (x, y, x+46, y+46), 12, (207,169,84,45), outline=(207,169,84,120))
    if idx == 2:
        for m in range(5):
            x1 = 118 + m*76
            y1 = 610 + int(34*math.sin(t*1.8 + m))
            d.line((x1, 658, x1+34, y1), fill=(128,215,170,135), width=5)
            d.ellipse((x1+28, y1-6, x1+40, y1+6), fill=GREEN)
    if idx == 3:
        d.line((166, 610, 374, 690), fill=RED, width=9)
        d.line((374, 610, 166, 690), fill=RED, width=9)
    if idx == 4:
        for m, txt in enumerate(['História', 'Exames', 'Risco', 'Plano']):
            x = 72 + (m%2)*210
            y = 594 + (m//2)*64
            rounded_rect(d, (x, y, x+180, y+44), 14, (128,215,170,36), outline=(128,215,170,110))
            d.text((x+18, y+10), txt, font=FONT_SMALL, fill=TEXT)

    return img.convert('RGB')


for i in range(FRAMES):
    make_frame(i).save(FRAMES_DIR / f'frame_{i:04d}.jpg', quality=88)

# Ambient bed (no voice) + render 45s. Use silence-safe AAC to avoid autoplay issues.
audio = OUT / 'ambient.m4a'
subprocess.run([
    'ffmpeg','-y',
    '-f','lavfi','-i',f'sine=frequency=174:duration={DURATION}',
    '-f','lavfi','-i',f'sine=frequency=432:duration={DURATION}',
    '-filter_complex','[0:a]volume=0.035[a0];[1:a]volume=0.018[a1];[a0][a1]amix=inputs=2,afade=t=in:st=0:d=2,afade=t=out:st=42:d=3',
    '-c:a','aac','-b:a','128k',str(audio)
], check=True)

subprocess.run([
    'ffmpeg','-y',
    '-framerate',str(FPS),'-i',str(FRAMES_DIR / 'frame_%04d.jpg'),
    '-i',str(audio),
    '-vf','scale=1080:1920:flags=lanczos,format=yuv420p',
    '-c:v','libx264','-preset','medium','-crf','20',
    '-c:a','aac','-b:a','128k','-shortest',str(FINAL)
], check=True)

# verification artifacts
ffprobe_json = VERIFY / 'ffprobe_final.json'
with ffprobe_json.open('w') as f:
    subprocess.run(['ffprobe','-v','error','-show_entries','format=duration,size','-show_entries','stream=index,codec_type,codec_name,width,height,r_frame_rate','-of','json',str(FINAL)], stdout=f, check=True)

contact = VERIFY / 'contact_sheet.jpg'
subprocess.run(['ffmpeg','-y','-i',str(FINAL),'-vf','fps=1/5,scale=216:384,tile=3x3',str(contact)], check=True)

manifest = {
    'topic': 'Menopausa Precoce',
    'duration_target_seconds': DURATION,
    'format': '1080x1920, H.264/AAC, 24fps',
    'final': str(FINAL),
    'ffprobe': str(ffprobe_json),
    'contact_sheet': str(contact),
    'narration_script_reference': NARRATION,
    'compliance': [
        'Conteúdo educativo; não substitui consulta médica.',
        'Sem promessa de resultado, diagnóstico público, prescrição ou paciente real.',
        'CTA seguro para avaliação médica individualizada.'
    ]
}
(OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(manifest, ensure_ascii=False))
