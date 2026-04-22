#!/usr/bin/env python3
"""
clara_create_image.py — Wrapper orquestrador que Clara DEVE usar para qualquer
criacao de imagem. NUNCA pular.

Fluxo automatico:
1. Se tema envolver "Dra. Daniely": OBRIGATORIO --with-dra (selectiona foto real)
2. photo_selector escolhe foto adequada ao tema + diversificacao
3. build_prompt monta prompt nas 7 dimensoes com biblioteca de poses variadas
4. generate_with_reference (com Dra) ou generate_image (sem pessoa)
5. send_to_telegram para entrega

Uso:
    # Imagem da Dra em consultorio (obrigatorio --with-dra)
    python3 clara_create_image.py --with-dra \
      --tema "Dra. em consultorio medico recebendo paciente" \
      --pose-hint "conversando com paciente" \
      --estilo editorial \
      --aspect-ratio 4:5 \
      --out /root/img_consultorio.png

    # Imagem sem pessoa (produto, cenario)
    python3 clara_create_image.py \
      --tema "frasco de suplemento em fundo minimalista dourado" \
      --estilo minimalista \
      --aspect-ratio 1:1 \
      --out /root/img_produto.png
"""
import argparse, os, subprocess, sys, json, tempfile
from pathlib import Path

SCRIPTS = Path("/root/.openclaw/workspace/skills/prompt-imagens/scripts")
CARR_SCRIPTS = Path("/root/.openclaw/workspace/skills/tweet-carrossel/scripts")
ACERVO = Path("/root/.openclaw/workspace/fotos_dra/originais")


def select_dra_photo(tema: str) -> str:
    """Chama photo_selector para pegar melhor foto da Dra para o tema."""
    r = subprocess.run(
        ["python3", str(CARR_SCRIPTS / "photo_selector.py"),
         "--theme", tema, "--top-k", "5", "--format", "json"],
        capture_output=True, text=True, timeout=120
    )
    try:
        data = json.loads(r.stdout)
    except:
        # Fallback: pega primeira foto do acervo
        return str(ACERVO / "Imagem PNG 11.png")

    best = data.get("best_match")
    if best and best.get("filename"):
        return str(ACERVO / best["filename"])
    return str(ACERVO / "Imagem PNG 11.png")


def build_prompt(sujeito, aparencia, acao, cenario, iluminacao, estilo, camera, with_ref):
    """Monta o prompt via build_prompt.py."""
    args = ["python3", str(SCRIPTS / "build_prompt.py"),
            "--sujeito", sujeito,
            "--aparencia", aparencia,
            "--acao", acao,
            "--cenario", cenario,
            "--iluminacao", iluminacao,
            "--estilo", estilo]
    if camera:
        args += ["--camera", camera]
    if with_ref:
        args += ["--with-reference"]
    r = subprocess.run(args, capture_output=True, text=True, timeout=30)
    return r.stdout.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--with-dra", action="store_true",
                    help="Imagem envolve Dra. Daniely — OBRIGATORIO usa foto real como referencia")
    ap.add_argument("--foto-dra", help="Caminho explicito de foto da Dra (se omitido, photo_selector escolhe)")
    ap.add_argument("--tema", required=True, help="Tema/contexto geral")
    ap.add_argument("--sujeito", help="Descricao do sujeito (default: auto)")
    ap.add_argument("--aparencia", help="Descricao de aparencia (default: auto para Dra)")
    ap.add_argument("--acao", help="Pose/acao (usar biblioteca de 24 poses)")
    ap.add_argument("--cenario", help="Descricao do cenario")
    ap.add_argument("--iluminacao", help="Iluminacao (default: 3200K lateral suave)")
    ap.add_argument("--estilo", default="editorial", help="Estilo fotografico")
    ap.add_argument("--camera", help="Camera/lente (default por estilo)")
    ap.add_argument("--aspect-ratio", default="4:5")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    # Defaults para Dra
    if args.with_dra:
        sujeito = args.sujeito or "Dra. Daniely Freitas, medica especialista em emagrecimento e longevidade, 43 anos"
        aparencia = args.aparencia or (
            "Cabelo loiro ondulado na altura dos ombros, pele clara, semblante sereno "
            "e confiante. Preservar EXCLUSIVAMENTE o rosto da foto de referencia"
        )
        acao = args.acao or "conversando com paciente, gesto acolhedor, expressao empatica"
        cenario = args.cenario or args.tema
        iluminacao = args.iluminacao or (
            "Luz lateral suave de estudio, temperatura quente 3200K, contraste moderado, "
            "leve rim light dourado"
        )
        foto_ref = args.foto_dra or select_dra_photo(args.tema)
        print(f"📸 Foto de referencia selecionada: {foto_ref}")
    else:
        sujeito = args.sujeito or args.tema
        aparencia = args.aparencia or "elementos visuais tangiveis relacionados ao tema"
        acao = args.acao or "composicao estatica profissional"
        cenario = args.cenario or args.tema
        iluminacao = args.iluminacao or "iluminacao profissional de estudio, temperatura neutra 5500K"
        foto_ref = None

    print(f"\n=== Montando prompt (7 dimensoes) ===")
    prompt = build_prompt(sujeito, aparencia, acao, cenario, iluminacao,
                          args.estilo, args.camera, with_ref=args.with_dra)
    print(prompt[:600] + "...")

    # Salva prompt em tempfile
    tmp_prompt = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8")
    tmp_prompt.write(prompt)
    tmp_prompt.close()

    print(f"\n=== Gerando imagem via {'generate_with_reference' if foto_ref else 'generate_image'} ===")
    if foto_ref:
        cmd = ["python3", str(SCRIPTS / "generate_with_reference.py"),
               "--prompt-file", tmp_prompt.name,
               "--reference", foto_ref,
               "--out", args.out,
               "--aspect-ratio", args.aspect_ratio]
    else:
        cmd = ["python3", str(SCRIPTS / "generate_image.py"),
               "--prompt-file", tmp_prompt.name,
               "--out", args.out,
               "--aspect-ratio", args.aspect_ratio]

    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    print(r.stdout)
    if r.returncode != 0:
        print("STDERR:", r.stderr[:500], file=sys.stderr)
        sys.exit(1)

    # Marca foto como usada (se Dra)
    if foto_ref and args.with_dra:
        filename = Path(foto_ref).name
        subprocess.run(["python3", str(CARR_SCRIPTS / "photo_selector.py"),
                        "--mark-used", filename, "--with-theme", args.tema],
                       capture_output=True, text=True)
        print(f"✅ Foto {filename} marcada como usada")

    os.unlink(tmp_prompt.name)
    print(f"\n✅ Imagem criada: {args.out}")


if __name__ == "__main__":
    main()
