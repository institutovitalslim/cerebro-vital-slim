#!/usr/bin/env python3
"""
compose_cover_auto.py — Wrapper inteligente que:
1. Roda photo_selector.py para achar a melhor foto da Dra. para o tema
2. Se score < threshold: roda generate_variation.py (NanoBanana 2)
3. Chama compose_cover.py com a foto escolhida/gerada
4. Marca a foto como usada no usage.json

Uso:
    python3 compose_cover_auto.py \
      --tema-foto "retatrutide medicamento injetavel emagrecimento" \
      --tema-fundo "consultorio medico moderno" \
      --headline "RETATRUTIDE|NAO ESTA SO|FAZENDO O PACIENTE|EMAGRECER" \
      --destaques "RETATRUTIDE,EMAGRECER" \
      --circulo /root/circulo_retatrutide.png \
      --out /root/capa_retatrutide.jpg
"""
import argparse, os, json, subprocess, sys, re
from pathlib import Path
from datetime import datetime

SCRIPTS = Path("/root/.openclaw/workspace/skills/tweet-carrossel/scripts")


def slugify(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[-\s]+", "-", text)
    return text.strip("-")[:40]


def run(cmd, timeout=600):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def select_photo(theme: str, min_score: float = 0.55):
    """Chama photo_selector.py e retorna dict."""
    r = run(["python3", str(SCRIPTS / "photo_selector.py"),
             "--theme", theme, "--top-k", "5",
             "--min-score", str(min_score),
             "--format", "json"])
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        # Pode ter vindo com texto antes; tenta extrair
        match = re.search(r"\{[\s\S]*\}", r.stdout)
        if match:
            return json.loads(match.group(0))
    return None


def generate_variation(base_path: str, theme: str, out_path: str) -> bool:
    r = run(["python3", str(SCRIPTS / "generate_variation.py"),
             "--base", base_path,
             "--variation", theme,
             "--out", out_path])
    print(r.stdout)
    if r.returncode != 0:
        print("  variation stderr:", r.stderr[:500], file=sys.stderr)
    return r.returncode == 0


def mark_photo_used(filename: str, theme: str):
    run(["python3", str(SCRIPTS / "photo_selector.py"),
         "--mark-used", filename, "--with-theme", theme])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tema-foto", required=True, help="Tema para buscar foto da Dra (ex: 'retatrutide emagrecimento')")
    ap.add_argument("--tema-fundo", required=True, help="Tema/descricao do fundo (ex: 'consultorio moderno')")
    ap.add_argument("--headline", required=True, help="Headline da capa (linhas separadas por |)")
    ap.add_argument("--destaques", default="", help="Palavras douradas")
    ap.add_argument("--circulo", default=None, help="Imagem do circulo")
    ap.add_argument("--out", required=True, help="JPG de saida")
    ap.add_argument("--skip-bg", default=None, help="Usar este fundo em vez de gerar")
    ap.add_argument("--min-score", type=float, default=0.55)
    ap.add_argument("--force-variation", action="store_true", help="Sempre gerar variacao")
    args = ap.parse_args()

    print(f"=== 1. Selecionando foto da Dra. para: '{args.tema_foto}' ===")
    result = select_photo(args.tema_foto, args.min_score)
    if not result:
        print("ERRO: photo_selector nao retornou resultado", file=sys.stderr)
        sys.exit(1)
    if "error" in result:
        print(f"ERRO: {result['error']}", file=sys.stderr)
        sys.exit(1)

    best = result["best_match"]
    needs_gen = result["needs_generation"] or args.force_variation

    if not best:
        print("ERRO: nenhum match retornado", file=sys.stderr)
        sys.exit(1)

    print(f"  Top-1: {best['filename']} (score={best['semantic_score']}, usada={best['usage_count']}x)")

    photo_path = None
    if needs_gen:
        print(f"\n=== 2. Score baixo - gerando VARIACAO via NanoBanana 2 ===")
        # Base: o top-1 (mais parecido com o tema)
        base = Path("/root/.openclaw/workspace/fotos_dra/originais") / best["filename"]
        var_out = f"/tmp/dra_variation_{slugify(args.tema_foto)}.png"
        success = generate_variation(str(base), args.tema_foto, var_out)
        if success:
            photo_path = var_out
            print(f"  variacao salva: {var_out}")
        else:
            print(f"  variacao falhou - usando foto base original")
            photo_path = str(base)
    else:
        print(f"\n=== 2. Usando foto do acervo (score suficiente) ===")
        photo_path = str(Path("/root/.openclaw/workspace/fotos_dra/originais") / best["filename"])

    print(f"  foto escolhida: {photo_path}")

    print(f"\n=== 3. Compondo capa ===")
    cmd = ["python3", str(SCRIPTS / "compose_cover.py"),
           "--foto", photo_path,
           "--tema", args.tema_fundo,
           "--headline", args.headline,
           "--destaques", args.destaques,
           "--out", args.out]
    if args.circulo:
        cmd.extend(["--circulo", args.circulo])
    if args.skip_bg:
        cmd.extend(["--skip-bg", args.skip_bg])

    r = run(cmd, timeout=600)
    print(r.stdout)
    if r.returncode != 0:
        print("ERRO compose_cover:", r.stderr[:500], file=sys.stderr)
        sys.exit(1)

    # Marca a foto como usada (somente se veio do acervo, nao se foi variacao)
    if not needs_gen:
        print(f"\n=== 4. Marcando foto como usada ===")
        mark_photo_used(best["filename"], args.tema_foto)
        print(f"  {best['filename']} marcada")

    print(f"\n✅ Capa criada: {args.out}")


if __name__ == "__main__":
    main()
