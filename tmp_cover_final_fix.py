#!/usr/bin/env python3
from PIL import Image
import os

W,H=1080,1350
bg_path='/root/.openclaw/media/tool-image-generation/glp1_endometrial_bg---17630a90-e5a5-47f4-b657-ea830ce22cf5.jpg'
circle_path='/root/.openclaw/media/tool-image-generation/glp1_endometrial_circle---160061a1-630b-4cee-ad0f-1dd0fd12c4a8.jpg'
photo_path='/root/.openclaw/workspace/fotos_dra/originais/Imagem PNG 20.png'
out_composed='/root/cerebro-vital-slim/deliverables/glp1-cancer-endometrial/corrigido/foto_composta_final.jpg'

bg=Image.open(bg_path).convert('RGB').resize((W,H), Image.LANCZOS)
photo=Image.open(photo_path)

try:
    from rembg import remove
    photo=remove(photo)
except Exception:
    photo=photo.convert('RGBA')

photo_h=int(H*0.50)
ratio=photo_h/photo.height
photo=photo.resize((int(photo.width*ratio), photo_h), Image.LANCZOS)

x=(W-photo.width)//2
y=20
rgba=bg.convert('RGBA')
rgba.paste(photo,(x,y),photo if photo.mode=='RGBA' else None)
rgba.convert('RGB').save(out_composed, quality=95)
print(out_composed)
print(circle_path)
