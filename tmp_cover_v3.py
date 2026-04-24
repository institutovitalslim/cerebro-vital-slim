#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont
import os, sys

# Constants
W,H=1080,1350
SAFE_TOP,SAFE_BOTTOM=135,H-135
GOLD=(159,136,68)
WHITE=(255,255,255)
GRAY=(180,180,180)

# Font paths
MONTSERRAT="/usr/local/share/fonts/Montserrat-Black.ttf"
if not os.path.isfile(MONTSERRAT):
    MONTSERRAT="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

REG_FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# Build headline with one word per line to maximize vertical fill
lines=["UM","REMÉDIO","PARA","EMAGRECER","PODE","SALVAR","SEU","ÚTERO"]
highlight={"REMÉDIO","EMAGRECER","SALVAR","ÚTERO"}

# Load background
bg=Image.open('/root/.openclaw/media/tool-image-generation/glp1_endometrial_bg---17630a90-e5a5-47f4-b657-ea830ce22cf5.jpg').convert('RGB').resize((W,H), Image.LANCZOS)

# Load photo with transparent background
photo=Image.open('/root/.openclaw/workspace/fotos_dra/originais/Imagem PNG 20.png')
try:
    from rembg import remove
    photo=remove(photo)
except Exception:
    photo=photo.convert('RGBA')

# Scale photo to fit upper portion (smaller to give more space to text)
photo_h=int(H*0.32)
ratio=photo_h/photo.height
photo=photo.resize((int(photo.width*ratio), photo_h), Image.LANCZOS)

# Center photo horizontally
x=(W-photo.width)//2
y=15
rgba=bg.convert('RGBA')
rgba.paste(photo,(x,y),photo if photo.mode=='RGBA' else None)

# Gradient fade at bottom of photo area
fade_start=int(y+photo_h*0.6)
fade_end=y+photo_h
for row in range(fade_start, min(fade_end, H)):
    alpha=int(255*(row-fade_start)/(fade_end-fade_start))
    for col in range(W):
        if row < H:
            px=rgba.getpixel((col,row))
            rgba.putpixel((col,row), (
                int(px[0]*(1-alpha/255)),
                int(px[1]*(1-alpha/255)),
                int(px[2]*(1-alpha/255)),
                255
            ))

bg=rgba.convert('RGB')
draw=ImageDraw.Draw(bg)

# Gold line + V symbol
line_y=int(H*0.38)
margin=40
SYMBOL_SIZE=100

# Try to load V symbol
v_path="/root/.openclaw/workspace/skills/tweet-carrossel/assets/simbolo_v.png"
if os.path.isfile(v_path):
    v_img=Image.open(v_path).convert('RGBA').resize((SYMBOL_SIZE, SYMBOL_SIZE), Image.LANCZOS)
    cx=W//2
    gap=SYMBOL_SIZE//2+10
    draw.line([(margin,line_y),(cx-gap,line_y)], fill=(*GOLD,200), width=2)
    draw.line([(cx+gap,line_y),(W-margin,line_y)], fill=(*GOLD,200), width=2)
    bg_rgba=bg.convert('RGBA')
    bg_rgba.paste(v_img,(cx-SYMBOL_SIZE//2,line_y-SYMBOL_SIZE//2),v_img)
    bg=bg_rgba.convert('RGB')
    draw=ImageDraw.Draw(bg)
else:
    draw.line([(margin,line_y),(W-margin,line_y)], fill=GOLD, width=2)

# Calculate max font size
available_h=SAFE_BOTTOM-line_y-80  # space between line and safe bottom (minus footer)
num_lines=len(lines)

best_size=40
for size in range(180, 40, -2):
    test_font=ImageFont.truetype(MONTSERRAT, size)
    line_h=int(size*1.05)
    total_h=num_lines*line_h
    # Check width
    max_w=max(draw.textlength(line, font=test_font) for line in lines)
    if total_h<=available_h and max_w<=W-80:
        best_size=size
        break

font=ImageFont.truetype(MONTSERRAT, best_size)
line_h=int(best_size*1.05)
total_h=num_lines*line_h

# Center vertically in available space
text_start_y=line_y+40

for i,line in enumerate(lines):
    y=text_start_y+i*line_h
    color=GOLD if line in highlight else WHITE
    bbox=draw.textbbox((0,0),line,font=font)
    tw=bbox[2]-bbox[0]
    x=(W-tw)//2
    draw.text((x,y),line,fill=color,font=font)

# Footer
footer_font=ImageFont.truetype(REG_FONT, 18)
bbox=draw.textbbox((0,0),"Dra. Daniely Freitas  |  CRM-BA 27588", font=footer_font)
tw=bbox[2]-bbox[0]
draw.text(((W-tw)//2, SAFE_BOTTOM-30), "Dra. Daniely Freitas  |  CRM-BA 27588", fill=GRAY, font=footer_font)

# Save
out='/root/cerebro-vital-slim/deliverables/glp1-cancer-endometrial/corrigido/slide_01_v3.jpg'
bg.save(out, "JPEG", quality=95, optimize=True)
print(f"✓ {out} — font size: {best_size}px, {num_lines} lines")
