#!/usr/bin/env python3
"""
generate_image.py — Gera imagem via NanoBanana 2 Pro (Gemini 3 Pro Image).

Uso:
    python3 generate_image.py --prompt-file /tmp/prompt.txt \
                              --out /root/imagem.png \
                              --aspect-ratio 4:5

Modelos em ordem de preferencia:
1. nano-banana-pro-preview (NanoBanana 2 Pro = Gemini 3 Pro Image Preview)
2. gemini-3-pro-image-preview
3. gemini-3.1-flash-image-preview (fallback)
4. gemini-2.5-flash-image (ultimo recurso)
"""
import argparse, os, json, base64, urllib.request, sys, time
from pathlib import Path

MODELS = [
    "nano-banana-pro-preview",
    "gemini-3-pro-image-preview",
    "gemini-3.1-flash-image-preview",
    "gemini-2.5-flash-image",
]

ASPECT_HINTS = {
    "4:5":  "proporcao retrato 4:5, 1080x1350 pixels",
    "1:1":  "proporcao quadrada 1:1, 1080x1080 pixels",
    "9:16": "proporcao vertical story 9:16, 1080x1920 pixels",
    "16:9": "proporcao paisagem 16:9, 1920x1080 pixels",
    "3:4":  "proporcao retrato 3:4, 1080x1440 pixels",
}


def call_model(model: str, prompt: str, api_key: str):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "temperature": 0.6,
        },
    }
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(r.read())


def generate(prompt: str, out_path: str, aspect_ratio: str = "4:5") -> bool:
    api_key = os.environ.get("GOOGLE_API_KEY", "")
    if not api_key:
        print("ERRO: GOOGLE_API_KEY nao definida", file=sys.stderr)
        return False

    # Enriquece prompt com dica de proporcao
    hint = ASPECT_HINTS.get(aspect_ratio, f"proporcao {aspect_ratio}")
    full_prompt = f"{prompt}\n\nTECNICO: {hint}. Nao adicione texto, logos ou marcas de agua."

    for model in MODELS:
        for attempt in range(3):
            try:
                print(f"Tentando {model} (tentativa {attempt+1})...")
                resp = call_model(model, full_prompt, api_key)
                for candidate in resp.get("candidates", []):
                    for part in candidate.get("content", {}).get("parts", []):
                        if "inlineData" in part:
                            img_bytes = base64.b64decode(part["inlineData"]["data"])
                            Path(out_path).parent.mkdir(parents=True, exist_ok=True)
                            Path(out_path).write_bytes(img_bytes)
                            print(f"  ✅ Imagem gerada: {out_path} ({len(img_bytes)//1024}KB)")
                            print(f"  Modelo usado: {model}")
                            return True
                        elif "text" in part:
                            print(f"  text: {part['text'][:150]}")
                print(f"  {model}: sem imagem na resposta")
                break
            except urllib.error.HTTPError as e:
                code = e.code
                err_body = e.read().decode()[:200]
                print(f"  {model} HTTP {code}: {err_body}")
                if code == 429:
                    wait = 20 * (attempt + 1)
                    print(f"    rate limit, esperando {wait}s...")
                    time.sleep(wait)
                    continue
                elif code == 404:
                    break  # modelo nao existe
                else:
                    break
            except Exception as e:
                print(f"  {model} erro: {e}")
                break

    return False


def main():
    ap = argparse.ArgumentParser()
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--prompt", help="Prompt direto")
    src.add_argument("--prompt-file", help="Arquivo com prompt")
    ap.add_argument("--out", required=True, help="PNG de saida")
    ap.add_argument("--aspect-ratio", default="4:5",
                    choices=["4:5", "1:1", "9:16", "16:9", "3:4"])
    args = ap.parse_args()

    if args.prompt_file:
        prompt = Path(args.prompt_file).read_text(encoding="utf-8").strip()
    else:
        prompt = args.prompt

    if not prompt:
        print("ERRO: prompt vazio", file=sys.stderr)
        sys.exit(1)

    print(f"Prompt ({len(prompt)} chars):")
    print("-" * 60)
    print(prompt[:800] + ("..." if len(prompt) > 800 else ""))
    print("-" * 60)

    success = generate(prompt, args.out, args.aspect_ratio)
    if not success:
        print("\nFALHOU em todos os modelos.", file=sys.stderr)
        sys.exit(2)
    print(f"\nOK: {args.out}")


if __name__ == "__main__":
    main()
