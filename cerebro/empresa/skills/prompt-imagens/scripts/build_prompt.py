#!/usr/bin/env python3
"""
build_prompt.py — Helper para Clara estruturar prompts seguindo as 7 dimensoes.

Uso:
    python3 build_prompt.py --json config.json
    # ou
    python3 build_prompt.py \
        --sujeito "..." --aparencia "..." --acao "..." --cenario "..." \
        --iluminacao "..." --estilo "editorial" --camera "..." \
        --with-reference  # adiciona clausula de preservacao de rosto

Estilos disponiveis (dimensao 6):
  editorial, cinematografico, fashion, street, fine-art,
  documental, retro, minimalista

Saida: prompt completo em stdout, pronto para generate_image.py / generate_with_reference.py
"""
import argparse, json, sys
from pathlib import Path


STYLE_DESCRIPTIONS = {
    "editorial": (
        "Estilo editorial moderno, limpo, luz suave, cores elegantes. "
        "Referencias: capa de revista Vogue Wellness, ensaios editorial de saude/lifestyle premium."
    ),
    "cinematografico": (
        "Estilo cinematografico, granulacao leve, cores profundas, iluminacao dramatica, "
        "paleta rica e composicao de filme. Referencias: Roger Deakins, filmes A24, look ARRI Alexa."
    ),
    "fashion": (
        "Estilo high fashion/Vogue, poses marcantes, luz dura direcional, contraste alto, "
        "estetica de revista de moda. Referencias: Vogue Paris, Harper's Bazaar."
    ),
    "street": (
        "Estilo street photography, espontaneo, urbano, luzes de cidade refletindo em superficies "
        "molhadas, pessoas desfocadas ao fundo. Referencias: Vivian Maier, Bruce Gilden."
    ),
    "fine-art": (
        "Estilo fine art, minimalista e poetico, composicao delicada, significado profundo. "
        "Referencias: retratos de Irving Penn, composicoes de Rinko Kawauchi."
    ),
    "documental": (
        "Estilo documental, natural, cru, sem edicao excessiva, feel National Geographic. "
        "Referencias: Steve McCurry, James Nachtwey."
    ),
    "retro": (
        "Estilo retro/analogico, filme 35mm com granulacao, cores desbotadas, estetica 70-80-90. "
        "Referencias: Kodak Portra 400 (tons quentes), FujiFilm Pro 400H (verdes suaves), "
        "CineStill 800T (tungstenio). Imperfeicoes caracteristicas de filme."
    ),
    "minimalista": (
        "Estilo minimalista, uso reduzido de elementos, muito espaco negativo, paleta restrita "
        "(2-3 cores maximo), foco absoluto no sujeito. Referencias: fotografia de produto Apple."
    ),
    "aesthetic": (
        "Estilo aesthetic/soft girl/pastel, luz suave difusa, tons claros rosados e amarelados, "
        "vibe romantica e delicada. Referencias: estetica Pinterest/TikTok wellness, cores pastel."
    ),
    "cyberpunk": (
        "Estilo cyberpunk/neon/futurista, cores neon (rosa, azul, verde), cenarios urbanos "
        "futuristas, contraste alto, reflexos em metais e vidros. Referencias: Blade Runner 2049."
    ),
    "realismo-profundo": (
        "Estilo hyper-realistic, detalhe extremo, texturas nitidas, iluminacao perfeita, "
        "proximo de fotografia profissional de alta resolucao. Ideal para close-ups."
    ),
    "publicitario": (
        "Estilo publicitario/commercial, luz perfeita, nitidez alta, fundos planejados, "
        "estetica limpa. Referencias: ads de cosmeticos, alimentos premium, Apple ads."
    ),
    "lifestyle": (
        "Estilo lifestyle natural, movimento, pessoas sorrindo, cores vivas, clima casual, "
        "feel de influenciador autentico. Referencias: Kinfolk, Cereal magazine."
    ),
    "noir": (
        "Estilo noir/dramatico, contrastes fortes, sombras profundas, luz dura lateral, "
        "atmosfera misteriosa. Referencias: filmes noir classicos, Sebastiao Salgado B&W."
    ),
    "pixar": (
        "Estilo Pixar/cartoon/3D, personagens ilustrados com estetica animada, cores vivas, "
        "iluminacao estilizada, expressoes exageradas. Referencias: Pixar, Dreamworks."
    ),
}

CAMERA_DEFAULTS = {
    "editorial": "Canon R5 Mark II, lente 85mm f1.4, abertura f2.0 para bokeh suave.",
    "cinematografico": "ARRI Alexa Mini LF, lente anamorfica 50mm, abertura T2.8.",
    "fashion": "Hasselblad X2D 100C, lente 80mm f1.9, flash de estudio dedolight.",
    "street": "Fujifilm X100VI, lente fixa 23mm f2, ISO alto para atmosfera.",
    "fine-art": "Leica Q3, lente Summilux 28mm f1.7, foco manual preciso.",
    "documental": "Leica M11, lente Summicron 35mm f2, luz natural disponivel.",
    "retro": "Contax G2 com filme Kodak Portra 400, lente Zeiss Planar 45mm f2.",
    "minimalista": "Canon R5 Mark II, lente macro 100mm f2.8, iluminacao de softbox controlada.",
    "aesthetic": "Canon R6 Mark II, lente 50mm f1.8, luz natural de janela suave.",
    "cyberpunk": "Sony A7R V, lente 35mm f1.4, alta ISO para captar reflexos neon.",
    "realismo-profundo": "Phase One XT com Schneider 80mm f2.8, foco manual preciso.",
    "publicitario": "Canon R5 Mark II, lente 100mm macro, iluminacao de estudio profissional.",
    "lifestyle": "Fujifilm X-T5, lente 35mm f1.4, luz natural.",
    "noir": "Leica M11 Monochrom, lente Summicron 50mm f2, alto contraste B&W.",
    "pixar": "Render 3D (Octane/Blender Cycles), camera virtual 85mm equivalente, ray tracing.",
}

PRESERVE_CLAUSE = (
    "\n\nPRESERVACAO DE IDENTIDADE (OBRIGATORIO): "
    "Preserve 100% o rosto, estrutura facial, tracos, cor e corte de cabelo, "
    "cor dos olhos e aparencia geral da pessoa na(s) imagem(ns) de referencia anexa(s). "
    "Ela deve ser CLARAMENTE reconhecivel como a mesma pessoa. "
    "Modifique apenas cenario, iluminacao, vestimenta (se pedido) e pose conforme descrito acima."
)


def build(sujeito, aparencia, acao, cenario, iluminacao, estilo,
          camera=None, with_reference=False):
    style_desc = STYLE_DESCRIPTIONS.get(estilo.lower(), estilo)
    if not camera:
        camera = CAMERA_DEFAULTS.get(estilo.lower(), "Canon R5 Mark II, lente 50mm f1.4")

    prompt = (
        f"1. SUJEITO: {sujeito}\n\n"
        f"2. APARENCIA: {aparencia}\n\n"
        f"3. ACAO: {acao}\n\n"
        f"4. CENARIO: {cenario}\n\n"
        f"5. ILUMINACAO: {iluminacao}\n\n"
        f"6. ESTILO: {style_desc}\n\n"
        f"7. CAMERA/LENTE: {camera}"
    )
    if with_reference:
        prompt += PRESERVE_CLAUSE
    return prompt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", help="Arquivo JSON com as 7 dimensoes")
    ap.add_argument("--sujeito")
    ap.add_argument("--aparencia")
    ap.add_argument("--acao")
    ap.add_argument("--cenario")
    ap.add_argument("--iluminacao")
    ap.add_argument("--estilo", default="editorial",
                    choices=list(STYLE_DESCRIPTIONS.keys()))
    ap.add_argument("--camera", default=None)
    ap.add_argument("--with-reference", action="store_true",
                    help="Adiciona clausula de preservacao de rosto")
    ap.add_argument("--out", help="Salva em arquivo (default: stdout)")
    args = ap.parse_args()

    if args.json:
        cfg = json.loads(Path(args.json).read_text(encoding="utf-8"))
        prompt = build(
            sujeito=cfg.get("sujeito", ""),
            aparencia=cfg.get("aparencia", ""),
            acao=cfg.get("acao", ""),
            cenario=cfg.get("cenario", ""),
            iluminacao=cfg.get("iluminacao", ""),
            estilo=cfg.get("estilo", "editorial"),
            camera=cfg.get("camera"),
            with_reference=cfg.get("with_reference", args.with_reference),
        )
    else:
        required = ["sujeito", "aparencia", "acao", "cenario", "iluminacao"]
        missing = [r for r in required if not getattr(args, r)]
        if missing:
            print(f"ERRO: faltando --{', --'.join(missing)}", file=sys.stderr)
            sys.exit(1)
        prompt = build(
            args.sujeito, args.aparencia, args.acao, args.cenario,
            args.iluminacao, args.estilo, args.camera, args.with_reference,
        )

    if args.out:
        Path(args.out).write_text(prompt, encoding="utf-8")
        print(f"Prompt salvo em {args.out}")
    else:
        print(prompt)


if __name__ == "__main__":
    main()
