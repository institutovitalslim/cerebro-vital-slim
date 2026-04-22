#!/usr/bin/env python3
"""
generate_with_reference.py — Gera imagem preservando rosto da referencia.

Uso:
    python3 generate_with_reference.py \
        --prompt-file /tmp/prompt.txt \
        --reference /tmp/foto_original.png \
        --out /root/imagem_nova.png \
        --aspect-ratio 4:5

REGRA CRITICA:
- O rosto/identidade da referencia DEVE ser preservado 100%
- Injeta automaticamente clausula de preservacao no prompt se nao estiver presente
- Usa NanoBanana 2 Pro (nano-banana-pro-preview) prioritariamente
- Aceita multiplas referencias (--reference pode repetir)
"""
import argparse, os, json, base64, urllib.request, sys, time
from pathlib import Path

MODELS = [
    "nano-banana-pro-preview",
    "gemini-3-pro-image-preview",
    "gemini-3.1-flash-image-preview",
    "gemini-2.5-flash-image",
]

PRESERVE_CLAUSE = (
    "\n\nPRESERVACAO DE IDENTIDADE FACIAL (OBRIGATORIO): "
    "Preserve EXCLUSIVAMENTE o ROSTO da pessoa na(s) referencia(s) anexa(s): "
    "estrutura facial, tracos, formato dos olhos e do nariz, boca, maxilar, cor e "
    "corte do cabelo, cor dos olhos. Ela deve ser CLARAMENTE reconhecivel como a "
    "mesma pessoa. "
    "\n\n"
    "MODIFIQUE LIVREMENTE (NAO preserve da referencia): "
    "pose, postura, posicao das maos e dos bracos, angulo do corpo, enquadramento, "
    "vestimenta, acao que ela esta fazendo, expressao facial (sorrindo/seria/concentrada), "
    "cenario, iluminacao, camera, lente, atmosfera. "
    "\n\n"
    "Esses elementos NAO-faciais devem seguir APENAS a descricao textual do prompt "
    "acima — ignore como eles estao na foto de referencia. Se o prompt pedir pose "
    "diferente, angulo diferente ou roupa diferente, voce DEVE alterar, mantendo "
    "apenas o rosto fiel."
)


def call_model(model: str, prompt: str, refs_b64: list, api_key: str):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    parts = [{"text": prompt}]
    for b64 in refs_b64:
        parts.append({"inline_data": {"mime_type": "image/png", "data": b64}})
    body = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "temperature": 0.45,  # mais baixo para ser mais fiel a referencia
        },
    }
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(r.read())


def ensure_preservation(prompt: str) -> str:
    low = prompt.lower()
    if "preserve" in low and ("rosto" in low or "face" in low or "identidade" in low):
        return prompt
    return prompt + PRESERVE_CLAUSE


def load_ref(path: str) -> str:
    return base64.b64encode(Path(path).read_bytes()).decode()


def generate(prompt: str, refs: list, out_path: str, aspect_ratio: str = "4:5") -> bool:
    api_key = os.environ.get("GOOGLE_API_KEY", "")
    if not api_key:
        print("ERRO: GOOGLE_API_KEY nao definida", file=sys.stderr)
        return False

    prompt = ensure_preservation(prompt)
    prompt += f"\n\nTECNICO: proporcao {aspect_ratio}. Nao adicione texto, logos ou marcas de agua."

    refs_b64 = [load_ref(r) for r in refs]
    print(f"Referencias carregadas: {len(refs_b64)}")

    for model in MODELS:
        for attempt in range(3):
            try:
                print(f"Tentando {model} (tentativa {attempt+1})...")
                resp = call_model(model, prompt, refs_b64, api_key)
                for candidate in resp.get("candidates", []):
                    for part in candidate.get("content", {}).get("parts", []):
                        if "inlineData" in part:
                            img = base64.b64decode(part["inlineData"]["data"])
                            Path(out_path).parent.mkdir(parents=True, exist_ok=True)
                            Path(out_path).write_bytes(img)
                            print(f"  ✅ {out_path} ({len(img)//1024}KB) via {model}")
                            return True
                        elif "text" in part:
                            print(f"  text: {part['text'][:150]}")
                print(f"  {model}: sem imagem")
                break
            except urllib.error.HTTPError as e:
                code = e.code
                err_body = e.read().decode()[:200]
                print(f"  {model} HTTP {code}: {err_body}")
                if code == 429:
                    wait = 20 * (attempt + 1)
                    time.sleep(wait)
                    continue
                elif code == 404:
                    break
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
    ap.add_argument("--reference", action="append", required=True,
                    help="Caminho da foto de referencia (pode repetir)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--aspect-ratio", default="4:5",
                    choices=["4:5", "1:1", "9:16", "16:9", "3:4"])
    args = ap.parse_args()

    if args.prompt_file:
        prompt = Path(args.prompt_file).read_text(encoding="utf-8").strip()
    else:
        prompt = args.prompt

    for r in args.reference:
        if not Path(r).exists():
            print(f"ERRO: referencia nao encontrada: {r}", file=sys.stderr)
            sys.exit(1)

    print(f"Prompt ({len(prompt)} chars) + {len(args.reference)} referencia(s)")

    success = generate(prompt, args.reference, args.out, args.aspect_ratio)
    if not success:
        print("\nFALHOU em todos os modelos.", file=sys.stderr)
        sys.exit(2)
    print(f"\nOK: {args.out}")


if __name__ == "__main__":
    main()
