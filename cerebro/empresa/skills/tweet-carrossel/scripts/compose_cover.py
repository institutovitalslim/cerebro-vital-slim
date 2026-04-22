#!/usr/bin/env python3
"""
compose_cover.py — Pipeline completo para capas de carrossel IVS.

1. Remove fundo da foto da Dra. (rembg) com suavização de bordas
2. Gera fundo contextual via NanoBanana 2 (Gemini)
3. Compõe Dra. (cintura p/ cima) sobre o fundo
4. Chama make_cover.py para montar a capa final

Uso:
    python3 compose_cover.py \
        --foto /root/dra_seria_frontal.png \
        --tema "exames de sangue, tubos de ensaio, coleta laboratorial" \
        --circulo /root/circulo_magnesio_v2.png \
        --headline "SEU MAGNÉSIO ESTÁ|NORMAL|MAS SEU CORPO|DISCORDA." \
        --destaques "MAGNÉSIO,NORMAL,CORPO,DISCORDA." \
        --out /root/capa_magnesio_final.jpg
"""

import argparse
import os
import subprocess
import sys
import requests
import base64
import json
from PIL import Image, ImageFilter
import numpy as np


# ── Config ──
W, H = 1080, 1350
PHOTO_HEIGHT_RATIO = 0.55  # Dra. ocupa top 55%

# NanoBanana 2 (Gemini) config
GEMINI_API_KEY_FILE = "/root/.openclaw/auth-profiles.json"
GEMINI_MODELS = [
    "gemini-2.5-flash-image",
    "nano-banana-pro-preview",
    "gemini-3.1-flash-image-preview",
    "gemini-3-pro-image-preview",
]
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


def get_gemini_key():
    """Get Gemini API key from environment."""
    return os.environ.get("GOOGLE_API_KEY", os.environ.get("GEMINI_API_KEY", ""))


def remove_background(foto_path, output_path):
    """Remove background with rembg and smooth edges."""
    print("  Removendo fundo...")
    from rembg import remove

    img = Image.open(foto_path).convert("RGBA")
    result = remove(img)

    # Suavizar bordas do recorte (anti-halo)
    print("  Suavizando bordas...")
    alpha = result.split()[3]
    # Gaussian blur on alpha channel to soften edges
    alpha_smooth = alpha.filter(ImageFilter.GaussianBlur(radius=1.5))

    # Threshold to keep solid interior but smooth edges
    alpha_np = np.array(alpha_smooth)
    # Erode slightly to remove halo (pixels that were on the edge of bg)
    from PIL import ImageFilter as IF
    alpha_eroded = alpha.filter(IF.MinFilter(3))
    alpha_eroded_smooth = alpha_eroded.filter(IF.GaussianBlur(radius=1.0))

    result.putalpha(alpha_eroded_smooth)
    result.save(output_path, "PNG")
    print(f"  Fundo removido: {output_path}")
    return output_path


def generate_background(tema, output_path):
    """Generate contextual background via Gemini image generation."""
    print(f"  Gerando fundo: {tema}...")

    api_key = get_gemini_key()
    if not api_key:
        print("  AVISO: Sem API key do Gemini, usando fundo preto")
        bg = Image.new("RGB", (W, H), (0, 0, 0))
        bg.save(output_path)
        return output_path

    prompt = (
        f"Professional dark moody photograph of {tema}. "
        f"Cinematic lighting, shallow depth of field, blurred background. "
        f"Dark tones, suitable as background for a medical/health Instagram post. "
        f"No people, no text. Wide angle, portrait orientation."
    )

    headers = {"Content-Type": "application/json"}
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
        }
    }

    for model in GEMINI_MODELS:
        url = GEMINI_URL.format(model=model)
        try:
            print(f"  Tentando modelo: {model}...")
            resp = requests.post(f"{url}?key={api_key}", json=body, headers=headers, timeout=90)
            if resp.status_code != 200:
                print(f"  {model} falhou: {resp.status_code}")
                continue

            data = resp.json()
            for candidate in data.get("candidates", []):
                for part in candidate.get("content", {}).get("parts", []):
                    if "inlineData" in part:
                        img_data = base64.b64decode(part["inlineData"]["data"])
                        with open(output_path, "wb") as f:
                            f.write(img_data)
                        img = Image.open(output_path).convert("RGB")
                        img = img.resize((W, int(H * PHOTO_HEIGHT_RATIO)), Image.LANCZOS)
                        img.save(output_path)
                        print(f"  Fundo gerado com {model}: {output_path}")
                        return output_path

        except Exception as e:
            print(f"  {model} erro: {e}")
            continue

    print("  Gemini falhou - fallback Unsplash...")
    try:
        import requests
        from io import BytesIO
        from PIL import ImageFilter, ImageEnhance
        url = f"https://unsplash.com/napi/search/photos?query={tema.replace( , +)}&per_page=5&orientation=landscape"
        r = requests.get(url, timeout=15).json()
        for item in r.get("results", [])[:5]:
            try:
                img_resp = requests.get(item["urls"]["regular"], timeout=15)
                img = Image.open(BytesIO(img_resp.content)).convert("RGB")
                H_PHOTO = int(H * PHOTO_HEIGHT_RATIO)
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
                img = ImageEnhance.Brightness(img).enhance(0.40)
                img.save(output_path)
                print(f"  Fundo Unsplash: {item.get(chr(97)+chr(108)+chr(116)+chr(95)+chr(100)+chr(101)+chr(115)+chr(99)+chr(114)+chr(105)+chr(112)+chr(116)+chr(105)+chr(111)+chr(110), )[:60]}")
                return output_path
            except Exception as e:
                continue
    except Exception as e:
        print(f"  Unsplash tambem falhou: {e}")

    print("  AVISO FINAL: usando fundo preto (ambos Gemini e Unsplash falharam)")
    bg = Image.new("RGB", (W, int(H * PHOTO_HEIGHT_RATIO)), (20, 20, 20))
    bg.save(output_path)
    return output_path


def compose_on_background(dra_nobg_path, bg_path, output_path):
    """Compose Dra. (waist-up) on contextual background."""
    print("  Compondo Dra. sobre fundo...")

    dra = Image.open(dra_nobg_path).convert("RGBA")
    bg = Image.open(bg_path).convert("RGB")

    photo_h = int(H * PHOTO_HEIGHT_RATIO)

    # Resize background to fill photo area
    bg = bg.resize((W, photo_h), Image.LANCZOS)

    # Crop Dra. to waist-up (top ~70% of original, keeping head+torso)
    dra_w, dra_h = dra.size
    crop_bottom = int(dra_h * 0.85)  # Keep top 85%
    dra_cropped = dra.crop((0, 0, dra_w, crop_bottom))

    # Scale to fit photo area height
    scale = photo_h / dra_cropped.height
    new_w = int(dra_cropped.width * scale)
    new_h = photo_h
    dra_resized = dra_cropped.resize((new_w, new_h), Image.LANCZOS)

    # Center horizontally on background
    x_offset = (W - new_w) // 2
    y_offset = 0  # Aligned to top

    # Compose
    canvas = bg.convert("RGBA")
    canvas.paste(dra_resized, (x_offset, y_offset), dra_resized)

    # Save as RGB (for make_cover.py input)
    canvas.convert("RGB").save(output_path, "PNG")
    print(f"  Composição salva: {output_path}")
    return output_path


def run_make_cover(composed_path, circulo_path, headline, destaques, output_path):
    """Run make_cover.py to generate final cover."""
    print("  Gerando capa final...")
    cmd = [
        "python3", "/root/make_cover.py",
        "--foto", composed_path,
        "--headline", headline,
        "--destaques", destaques,
        "--out", output_path,
    ]
    if circulo_path:
        cmd.extend(["--circulo", circulo_path])

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERRO make_cover: {result.stderr}")
    else:
        print(result.stdout.strip())
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Pipeline completo de capas IVS")
    parser.add_argument("--foto", required=True, help="Foto original da Dra. (com fundo)")
    parser.add_argument("--tema", required=True, help="Descrição do fundo contextual (ex: 'exames de sangue')")
    parser.add_argument("--circulo", default=None, help="Imagem para círculo inset")
    parser.add_argument("--headline", required=True, help="Headline separada por | (pipe)")
    parser.add_argument("--destaques", default="", help="Palavras em dourado, separadas por vírgula")
    parser.add_argument("--out", default="/root/capa_final.jpg", help="Arquivo de saída")
    parser.add_argument("--skip-rembg", action="store_true", help="Pular rembg (usar foto já recortada)")
    parser.add_argument("--skip-bg", default=None, help="Usar este fundo em vez de gerar novo")
    args = parser.parse_args()

    basename = os.path.splitext(os.path.basename(args.out))[0]

    # Step 1: Remove background
    if args.skip_rembg:
        nobg_path = args.foto
    else:
        nobg_path = f"/root/{basename}_nobg.png"
        remove_background(args.foto, nobg_path)

    # Step 2: Generate/use background
    if args.skip_bg:
        bg_path = args.skip_bg
    else:
        bg_path = f"/root/{basename}_bg.png"
        generate_background(args.tema, bg_path)

    # Step 3: Compose
    composed_path = f"/root/{basename}_composed.png"
    compose_on_background(nobg_path, bg_path, composed_path)

    # Step 4: Make cover
    run_make_cover(composed_path, args.circulo, args.headline, args.destaques, args.out)

    # Cleanup temp files
    for tmp in [nobg_path, bg_path, composed_path]:
        if tmp != args.foto and os.path.isfile(tmp):
            os.remove(tmp)
            print(f"  Temp removido: {tmp}")

    print(f"\nCapa final: {args.out}")
    if os.path.isfile(args.out):
        size_kb = os.path.getsize(args.out) / 1024
        print(f"Tamanho: {size_kb:.0f}KB")


if __name__ == "__main__":
    main()
