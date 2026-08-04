# -*- coding: utf-8 -*-
"""
render_creative.py — Ponte entre o Content Engine OS e o motor de criativos visuais do IVS.
Recebe um "creative spec" normalizado (o que o content-engine produz: roteiro/copy + canal/formato)
e renderiza a PEÇA REAL (PNG/serie) reusando os geradores validados em skills/design-system-ivs.

Uso:
  python3 render_creative.py spec.json --out /caminho/saida
Spec (JSON) exemplo:
  {"channel":"feed","format":"carrossel","slides":[...]}            -> gen_carrossel (4:5)
  {"channel":"feed","format":"estatico","photo":"...","title":"...","sub":"...","cta":"..."} -> foto-led 4:5
  {"channel":"stories","format":"destaque","photo":"...","title":"...","label":"...","sub":"..."} -> foto-led 9:16
Regras canônicas aplicadas: tamanho por canal (feed 4:5 / stories|reels 9:16),
capa com a Dra. (foto-led), validação de overflow do gerador.
"""
import sys, os, json
sys.path.insert(0, "/root/cerebro-vital-slim/skills/design-system-ivs")
import gen_carrossel, gen_foto, gen_estatico  # noqa: E402

SIZE = {"feed": (1080, 1350), "stories": (1080, 1920), "reels": (1080, 1920)}

def render(spec: dict, outdir: str, prefix: str = "peca") -> list:
    os.makedirs(outdir, exist_ok=True)
    channel = spec.get("channel", "feed")
    fmt = spec.get("format", "estatico")
    size = SIZE.get(channel, (1080, 1350))
    if fmt == "carrossel":
        # cada slide herda size 4:5 (feed); foto-led quando "photo" presente no slide
        for s in spec["slides"]:
            s.setdefault("size", size)
        return gen_carrossel.render(spec, outdir, prefix)
    # estatico / destaque / post / story -> foto-led (capa com a Dra. ou imagem de tema)
    s = dict(spec); s["size"] = size
    if spec.get("photo"):
        return gen_foto.render(s, outdir, prefix)
    # sem foto -> estático de marca (texto sobre fundo seda)
    return gen_estatico.render(s, outdir, prefix)

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    spec = json.load(open(args[0], encoding="utf-8")) if args else None
    outdir = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else "out_render"
    if not spec:
        print("uso: render_creative.py spec.json --out DIR"); sys.exit(1)
    paths = render(spec, outdir, spec.get("prefix", "peca"))
    print(json.dumps({"ok": True, "files": paths}, ensure_ascii=False))
