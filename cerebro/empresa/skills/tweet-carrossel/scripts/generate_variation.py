#!/usr/bin/env python3
"""
generate_variation.py — Gera variacao de uma foto da Dra. via NanoBanana 2 (Gemini image).

Uso:
    python3 generate_variation.py \
      --base /path/to/foto_original.png \
      --variation "tema/estilo desejado (ex: medicamento injetavel moderno)" \
      --out /root/dra_variation_retatrutide.png

IMPORTANTE:
- Usa o modelo Gemini 2.5 Flash Image (nano-banana)
- Sempre envia a foto original como referencia para manter identidade facial
- Prompt foca em ALTERAR O CENARIO/ILUMINACAO, nao o rosto
"""
import os, json, base64, urllib.request, argparse, sys, time
from pathlib import Path

IMAGE_MODELS = [
    "gemini-2.5-flash-image",
    "gemini-3.1-flash-image-preview",
    "nano-banana-pro-preview",
    "gemini-3-pro-image-preview",
]


def build_prompt(variation_theme: str) -> str:
    """Constroi prompt que preserva identidade da Dra mas varia cenario."""
    return (
        "Use a foto anexa da Dra. Daniely Freitas como referencia PRINCIPAL de identidade. "
        "IMPORTANTE: preserve 100% o rosto, caracteristicas faciais, cabelo loiro ondulado, "
        "e aparencia geral - ela deve estar claramente reconhecivel como a mesma pessoa. "
        "Mantenha o blazer escuro e postura profissional seria. "
        f"MODIFIQUE apenas o cenario/enquadramento para refletir o tema: {variation_theme}. "
        "Ajuste iluminacao e fundo para combinar com o contexto. "
        "Estilo: foto de estudio profissional cinematografico, nitidez alta, "
        "iluminacao dramatica, proporcao retrato 4:5 ou 3:4. "
        "Nao adicione texto, logos ou elementos graficos na imagem. "
        "Semblante serio, sem sorriso exagerado. Braços cruzados ou pose de autoridade."
    )


def call_image_gen(base_path: Path, theme: str, out_path: Path) -> bool:
    key = os.environ.get("GOOGLE_API_KEY", "")
    if not key:
        print("ERRO: GOOGLE_API_KEY nao definida", file=sys.stderr)
        return False

    with open(base_path, "rb") as f:
        base_b64 = base64.b64encode(f.read()).decode()

    prompt = build_prompt(theme)

    for model in IMAGE_MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
        body = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {"inline_data": {"mime_type": "image/png", "data": base_b64}},
                ]
            }],
            "generationConfig": {"responseModalities": ["TEXT", "IMAGE"], "temperature": 0.5},
        }
        print(f"Tentando modelo: {model}...")
        for attempt in range(3):
            try:
                req = urllib.request.Request(
                    url, data=json.dumps(body).encode(),
                    headers={"Content-Type": "application/json"},
                )
                with urllib.request.urlopen(req, timeout=120) as r:
                    resp = json.loads(r.read())

                for candidate in resp.get("candidates", []):
                    for part in candidate.get("content", {}).get("parts", []):
                        if "inlineData" in part:
                            img_data = base64.b64decode(part["inlineData"]["data"])
                            out_path.write_bytes(img_data)
                            print(f"  ✅ Imagem gerada: {out_path} ({len(img_data)//1024}KB)")
                            return True
                        elif "text" in part:
                            print(f"  text: {part['text'][:150]}")
                print(f"  {model}: nao retornou imagem")
                break
            except urllib.error.HTTPError as e:
                code = e.code
                body_err = e.read().decode()[:200]
                print(f"  {model} HTTP {code}: {body_err}")
                if code == 429:
                    wait = 20 * (attempt + 1)
                    print(f"    rate limit, esperando {wait}s...")
                    time.sleep(wait)
                elif code == 404:
                    break  # modelo nao existe, tenta proximo
                else:
                    break
            except Exception as e:
                print(f"  {model} erro: {e}")
                break

    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True, help="Foto original da Dra. (PNG)")
    ap.add_argument("--variation", required=True, help="Descricao do tema/estilo desejado")
    ap.add_argument("--out", required=True, help="Arquivo de saida (.png)")
    args = ap.parse_args()

    base_path = Path(args.base)
    out_path = Path(args.out)
    if not base_path.exists():
        print(f"ERRO: base nao encontrada: {base_path}", file=sys.stderr)
        sys.exit(1)

    out_path.parent.mkdir(parents=True, exist_ok=True)

    success = call_image_gen(base_path, args.variation, out_path)
    if not success:
        print("\nFALHOU ao gerar variacao. Use a foto base original como fallback.", file=sys.stderr)
        sys.exit(2)

    print(f"\nOK: {out_path}")


if __name__ == "__main__":
    main()
