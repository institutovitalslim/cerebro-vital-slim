#!/usr/bin/env python3
"""
catalog_photos.py — Cataloga fotos da Dra. usando Gemini Vision.

Para cada foto em /root/.openclaw/workspace/fotos_dra/originais/ gera:
- Descricao visual (pose, expressao, vestimenta, cenario, iluminacao, emocao)
- Tags automaticas (serio, sorrindo, bracos cruzados, blazer escuro, etc.)
- Embedding semantico (Gemini 3072d)
- Adequacao para temas (indicacao de quais temas funcionam melhor)

Output: /root/.openclaw/workspace/fotos_dra/catalog.json
"""
import os, json, base64, urllib.request, time, sys, re
from pathlib import Path

PHOTOS_DIR = Path("/root/.openclaw/workspace/fotos_dra/originais")
CATALOG_PATH = Path("/root/.openclaw/workspace/fotos_dra/catalog.json")
USAGE_PATH = Path("/root/.openclaw/workspace/fotos_dra/usage.json")

GEMINI_KEY = os.environ.get("GOOGLE_API_KEY", "")
VISION_MODEL = "gemini-2.5-flash"
EMBED_MODEL = "gemini-embedding-001"

VISION_PROMPT = """Descreva esta foto de estudio fotografico profissional em PORTUGUES, de forma estruturada para catalogacao. Responda em JSON puro (sem markdown) com as chaves:

{
  "pose": "descricao breve da pose (ex: bracos cruzados frontal, maos no quadril, maos no rosto)",
  "expressao": "expressao facial (ex: seria, sorriso leve, sorriso largo, concentrada, confiante, reflexiva, amigavel)",
  "vestimenta": "descricao da roupa (cor do blazer, blusa, acessorios)",
  "enquadramento": "tipo de enquadramento (close-up, busto, meio-corpo, corpo inteiro)",
  "direcao_olhar": "para onde ela olha (camera, lateral, para baixo)",
  "tom_emocional": "sensacao transmitida (autoridade, acolhimento, preocupacao, inspiracao, seriedade, alegria)",
  "adequacao_temas": ["lista de 3-5 temas adequados para capa de post, ex: emagrecimento, tratamento cronico, consulta, bem-estar, protocolo rigoroso, acolhimento, diagnostico, medicamento, resultado, transformacao"],
  "descricao_curta": "uma frase de 15-25 palavras resumindo a foto"
}

IMPORTANTE: responda APENAS o JSON, sem texto antes ou depois, sem \\`\\`\\`json."""


def encode_image(path: Path) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def describe_photo(path: Path) -> dict:
    """Usa Gemini Vision para descrever a foto."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{VISION_MODEL}:generateContent?key={GEMINI_KEY}"
    img_b64 = encode_image(path)
    body = {
        "contents": [{
            "parts": [
                {"text": VISION_PROMPT},
                {"inline_data": {"mime_type": "image/png", "data": img_b64}},
            ]
        }],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 1024},
    }
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=90) as r:
        resp = json.loads(r.read())
    text = resp["candidates"][0]["content"]["parts"][0]["text"].strip()
    # Remove possiveis cercas markdown
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


def get_embedding(text: str) -> list:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{EMBED_MODEL}:embedContent?key={GEMINI_KEY}"
    body = {"model": f"models/{EMBED_MODEL}", "content": {"parts": [{"text": text[:8000]}]}}
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())["embedding"]["values"]


def main():
    if not GEMINI_KEY:
        print("ERRO: GOOGLE_API_KEY nao definida", file=sys.stderr)
        sys.exit(1)

    catalog = {}
    if CATALOG_PATH.exists():
        catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        print(f"Catalogo existente: {len(catalog)} entradas. Pulando ja catalogadas.")

    photos = sorted([p for p in PHOTOS_DIR.iterdir() if p.suffix.lower() in [".png", ".jpg", ".jpeg"]])
    print(f"Encontradas {len(photos)} fotos em {PHOTOS_DIR}")

    for i, p in enumerate(photos, 1):
        key = p.name
        if key in catalog:
            print(f"  [{i}/{len(photos)}] {key}: ja catalogada")
            continue

        print(f"  [{i}/{len(photos)}] {key}: descrevendo...")
        for attempt in range(4):
            try:
                desc = describe_photo(p)
                break
            except Exception as e:
                msg = str(e)[:100]
                print(f"    erro (tentativa {attempt+1}): {msg}")
                if "429" in msg or "quota" in msg.lower():
                    time.sleep(30 * (attempt + 1))
                else:
                    time.sleep(5)
        else:
            print(f"    FALHOU apos retries, pulando")
            continue

        # Texto para embedding (tudo que descreve a foto)
        emb_text = (
            f"Pose: {desc.get('pose','')}. Expressao: {desc.get('expressao','')}. "
            f"Vestimenta: {desc.get('vestimenta','')}. Enquadramento: {desc.get('enquadramento','')}. "
            f"Olhar: {desc.get('direcao_olhar','')}. Tom: {desc.get('tom_emocional','')}. "
            f"Temas adequados: {', '.join(desc.get('adequacao_temas', []))}. "
            f"{desc.get('descricao_curta','')}"
        )
        try:
            vec = get_embedding(emb_text)
        except Exception as e:
            print(f"    embedding falhou: {e}")
            vec = []

        catalog[key] = {
            "filename": key,
            "path": str(p),
            "description": desc,
            "emb_text": emb_text,
            "embedding": vec,
        }

        # Salva a cada 5 para nao perder progresso
        if i % 5 == 0 or i == len(photos):
            CATALOG_PATH.write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"    ... salvou {len(catalog)}/{len(photos)}")

        time.sleep(1.5)  # rate limit

    CATALOG_PATH.write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")

    # Inicializa usage.json se nao existir
    if not USAGE_PATH.exists():
        USAGE_PATH.write_text(json.dumps({"usage": {}}, indent=2), encoding="utf-8")

    print(f"\nOK! Catalogo completo: {CATALOG_PATH}")
    print(f"Total catalogadas: {len(catalog)}")


if __name__ == "__main__":
    main()
