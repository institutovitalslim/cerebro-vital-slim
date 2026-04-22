#!/usr/bin/env python3
"""Regenera bg + capa + slide 2 com todas as correções"""
import subprocess, os, base64, requests
from io import BytesIO
from PIL import Image, ImageFilter, ImageEnhance

W, H = 1080, 1350
OUT_DIR = "/root/cerebro-vital-slim/deliverables/creatina-cerebro-jpeg-2026-04-14"
TMP_DIR = f"{OUT_DIR}/tmp"

# GARANTIR avatar original (nao sobrescrever)
import shutil
if os.path.isfile("/root/avatar_hq_original.png"):
    # Sempre restaura do backup
    shutil.copy("/root/avatar_hq_original.png", "/root/avatar_hq.png")
    with open("/root/avatar_hq.png", "rb") as f:
        original_b64 = base64.b64encode(f.read()).decode()
    with open("/root/avatar_hq_b64.txt", "w") as f:
        f.write(original_b64)
    print(f"Avatar original restaurado: {len(original_b64)} chars")

# ============ 1. BG suplementos (jars CREATINE/PROTEIN/PRE-WORKOUT) ============
print("=== 1. Baixando BG aprovado (3 potes + shaker) ===")
bg_saved = False
if os.path.isfile("/root/bg_creatina_approved.png"):
    # Usa o bg salvo anteriormente como "aprovado"
    shutil.copy("/root/bg_creatina_approved.png", "/root/bg_creatina_final.png")
    print("BG aprovado restaurado do cache")
    bg_saved = True

if not bg_saved:
    # Busca original
    url = "https://unsplash.com/napi/search/photos?query=whey+protein+creatine&per_page=30&orientation=landscape"
    r = requests.get(url, timeout=20).json()
    for item in r.get("results", []):
        desc = item.get("alt_description", "").lower()
        if "three containers" in desc and "protein" in desc:
            try:
                img_resp = requests.get(item["urls"]["regular"], timeout=20)
                img = Image.open(BytesIO(img_resp.content)).convert("RGB")
                H_PHOTO = 743
                w, h = img.size
                target_ratio = W / H_PHOTO
                current_ratio = w / h
                if current_ratio < target_ratio:
                    new_h = int(w / target_ratio)
                    top = (h - new_h) // 2
                    img = img.crop((0, top, w, top + new_h))
                else:
                    new_w = int(h * target_ratio)
                    left = (w - new_w) // 2
                    img = img.crop((left, 0, left + new_w, h))
                img = img.resize((W, H_PHOTO), Image.LANCZOS)
                img = img.filter(ImageFilter.GaussianBlur(radius=8))
                img = ImageEnhance.Brightness(img).enhance(0.38)
                img.save("/root/bg_creatina_final.png")
                # Salva como aprovado para proximas rodadas
                shutil.copy("/root/bg_creatina_final.png", "/root/bg_creatina_approved.png")
                print(f"BG salvo e cacheado como approved: {desc[:70]}")
                bg_saved = True
                break
            except Exception as e:
                print(f"  erro: {e}")

if not bg_saved:
    print("AVISO: usando bg escuro fallback")
    img = Image.new("RGB", (W, 743), (20, 15, 10))
    img.save("/root/bg_creatina_final.png")

# ============ 2. Regenerar capa ============
print("\n=== 2. Regenerando capa (fonte cap=150) ===")
os.environ["GOOGLE_API_KEY"] = "AIzaSyAQcy8URejQXMEQS1MYrVDRUgdNGH6CrDo"
result = subprocess.run([
    "python3", "/root/compose_cover.py",
    "--foto", "/root/dra_seria_lateral.png",
    "--tema", "dummy",
    "--skip-bg", "/root/bg_creatina_final.png",
    "--circulo", "/root/circulo_creatina_v2.png",
    "--headline", "UM DOS SUPLEMENTOS|MAIS SUBESTIMADOS|PARA O CÉREBRO",
    "--destaques", "SUPLEMENTOS,SUBESTIMADOS,CÉREBRO",
    "--out", f"{OUT_DIR}/slide_01.jpg",
], capture_output=True, text=True)
print(result.stdout)
if result.returncode != 0:
    print("ERRO:", result.stderr)

# ============ 3. Regenerar slide 2 com avatar corrigido ============
print("\n=== 3. Regenerando slide 2 ===")
PMID = "39070254"
pubmed_png = f"{TMP_DIR}/pubmed_{PMID}.png"

# Garantir que o PubMed foi capturado com sucesso
result = subprocess.run([
    "python3", "/root/.openclaw/workspace/skills/tweet-carrossel/scripts/capture_pubmed.py",
    "--pmid", PMID, "--out", pubmed_png,
], capture_output=True, text=True)
print(result.stdout)

# Crop útil do pubmed
img = Image.open(pubmed_png).convert("RGB")
cropped = img.crop((0, 0, 910, 720))
crop_path = f"{TMP_DIR}/pubmed_crop.png"
cropped.save(crop_path)

# Avatar (já regenerado acima)
with open("/root/avatar_hq_b64.txt") as f:
    avatar_b64 = f.read().strip()
with open(crop_path, "rb") as f:
    paper_b64 = base64.b64encode(f.read()).decode()

lines = [
    "Uma revisão sistemática de 2024 no Frontiers in Nutrition analisou o efeito da creatina no cérebro.",
    "16 ensaios clínicos randomizados, 492 participantes.",
    "Os achados são claros. &rarr;",
]
lines_html = "".join(f"<p>{l}</p>" for l in lines)

html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ width:1080px; height:1350px; background:#000; color:#c8c8c8;
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  overflow:hidden; }}
body {{ padding:60px 64px; display:flex; flex-direction:column; }}
.header {{ display:flex; align-items:center; gap:28px; margin-bottom:50px; flex-shrink:0; }}
.avatar {{ width:96px; height:96px; border-radius:50%; overflow:hidden; flex-shrink:0; }}
.avatar img {{ width:100%; height:100%; object-fit:cover; display:block; }}
.user-info {{ display:flex; flex-direction:column; justify-content:center; gap:4px; }}
.name-row {{ display:flex; align-items:center; line-height:1.15; }}
.name {{ font-weight:700; font-size:48px; color:#fff; line-height:1.15; }}
.verified {{ display:inline-block; width:38px; height:38px; background:#1d9bf0;
  border-radius:50%; text-align:center; line-height:38px; font-size:20px;
  color:#fff; margin-left:12px; font-weight:700; }}
.handle {{ color:#71767b; font-size:34px; line-height:1.15; }}
.content {{ flex-shrink:0; }}
p {{ font-size:50px; line-height:1.28; color:#c8c8c8; margin-bottom:36px; font-weight:400; }}
.breathing {{ flex:1; display:flex; align-items:center; justify-content:center; }}
.paper-wrap {{ width:100%; border-radius:10px; overflow:hidden; }}
.paper-wrap img {{ width:100%; display:block; }}
</style></head><body>
<div class="header">
  <div class="avatar"><img src="data:image/png;base64,{avatar_b64}"></div>
  <div class="user-info">
    <div class="name-row"><span class="name">Dra. Daniely Freitas</span><span class="verified">&#10003;</span></div>
    <div class="handle">@dradaniely.freitas</div>
  </div>
</div>
<div class="content">{lines_html}</div>
<div class="breathing"><div class="paper-wrap"><img src="data:image/png;base64,{paper_b64}"></div></div>
</body></html>"""

html_path = f"{TMP_DIR}/slide_02.html"
with open(html_path, "w") as f:
    f.write(html)

png_out = f"{TMP_DIR}/slide_02.png"
subprocess.run(["chromium","--headless","--disable-gpu","--no-sandbox",
    f"--screenshot={png_out}","--window-size=1080,1350",f"file://{html_path}"],
    capture_output=True, timeout=60)

jpg_out = f"{OUT_DIR}/slide_02.jpg"
Image.open(png_out).convert("RGB").save(jpg_out, "JPEG", quality=85, optimize=True)
print(f"Slide 2 JPEG: {os.path.getsize(jpg_out)//1024}KB")

# ============ 4. Regenerar slides 3-10 com avatar novo ============
print("\n=== 4. Slides 3-10 também precisam do avatar novo ===")
# Lê config do slides.json para reconstruir slides 3-10
import json
with open(f"{TMP_DIR}/slides.json") as f:
    slides_cfg = json.load(f)

for cfg in slides_cfg:
    num = cfg["num"]
    if num == 2:
        continue  # já regenerado
    paragraphs = cfg.get("paragraphs", [])
    lines_html = "".join(f"<p>{p}</p>" for p in paragraphs)

    # CTA no último slide
    is_last = num == max(c["num"] for c in slides_cfg)

    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ width:1080px; height:1350px; background:#000; color:#c8c8c8;
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  overflow:hidden; }}
body {{ padding:60px 64px; display:flex; flex-direction:column; }}
.centered {{ flex:1; display:flex; flex-direction:column; justify-content:center; }}
.header {{ display:flex; align-items:center; gap:28px; margin-bottom:54px; flex-shrink:0; }}
.avatar {{ width:96px; height:96px; border-radius:50%; overflow:hidden; flex-shrink:0; }}
.avatar img {{ width:100%; height:100%; object-fit:cover; display:block; }}
.user-info {{ display:flex; flex-direction:column; justify-content:center; gap:4px; }}
.name-row {{ display:flex; align-items:center; line-height:1.15; }}
.name {{ font-weight:700; font-size:48px; color:#fff; line-height:1.15; }}
.verified {{ display:inline-block; width:38px; height:38px; background:#1d9bf0;
  border-radius:50%; text-align:center; line-height:38px; font-size:20px;
  color:#fff; margin-left:12px; font-weight:700; }}
.handle {{ color:#71767b; font-size:34px; line-height:1.15; }}
.content {{ flex-shrink:0; }}
p {{ font-size:56px; line-height:1.28; color:#c8c8c8; margin-bottom:40px; font-weight:400; }}
</style></head><body>
<div class="centered">
  <div class="header">
    <div class="avatar"><img src="data:image/png;base64,{avatar_b64}"></div>
    <div class="user-info">
      <div class="name-row"><span class="name">Dra. Daniely Freitas</span><span class="verified">&#10003;</span></div>
      <div class="handle">@dradaniely.freitas</div>
    </div>
  </div>
  <div class="content">{lines_html}</div>
</div>
</body></html>"""

    html_path = f"{TMP_DIR}/slide_{num:02d}.html"
    with open(html_path, "w") as f:
        f.write(html)
    png_out = f"{TMP_DIR}/slide_{num:02d}.png"
    subprocess.run(["chromium","--headless","--disable-gpu","--no-sandbox",
        f"--screenshot={png_out}","--window-size=1080,1350",f"file://{html_path}"],
        capture_output=True, timeout=60)

    # Map num to slide file name (slide_01 is cover, slide_02 is paper, slide_03 uses num=3 etc)
    # The slides.json has num=3,4,... but file names are slide_03.jpg etc
    jpg_out = f"{OUT_DIR}/slide_{num:02d}.jpg"
    Image.open(png_out).convert("RGB").save(jpg_out, "JPEG", quality=85, optimize=True)
    print(f"  Slide {num}: {os.path.getsize(jpg_out)//1024}KB")

print("\n=== DONE ===")
