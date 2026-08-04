# -*- coding: utf-8 -*-
"""
derive_design_system.py — Deriva o DESIGN SYSTEM de uma marca a partir de criativos enviados.
Feature do Content Engine OS: o cliente (clínica/médico) sobe peças que gosta; o sistema
extrai tokens (cores, fundo, texto, destaque, proporções, paleta) e gera um design_system.json
que os geradores de criativo consomem — assim cada cliente produz peças on-brand automaticamente.

Uso: python derive_design_system.py <pasta_ou_imagens...> --out design_system.json [--name "Marca"]
"""
import sys, os, json, glob, colorsys, statistics
from collections import Counter
from PIL import Image

EXTS = (".png", ".jpg", ".jpeg", ".webp")

def hexd(c): return "#%02X%02X%02X" % tuple(c[:3])

def collect(paths):
    files = []
    for p in paths:
        if os.path.isdir(p):
            for e in EXTS:
                files += glob.glob(os.path.join(p, "**", "*" + e), recursive=True)
        elif p.lower().endswith(EXTS):
            files.append(p)
    return sorted(set(files))

def aspect_label(w, h):
    r = round(w / h, 3)
    for lbl, val in [("9:16", 0.5625), ("4:5", 0.8), ("1:1", 1.0), ("3:4", 0.75), ("16:9", 1.777)]:
        if abs(r - val) < 0.03:
            return lbl
    return f"{r}"

def analyze_one(path):
    im = Image.open(path).convert("RGB"); w, h = im.size
    s = im.resize((240, int(240 * h / w))) if w else im
    px = list(s.getdata())
    corners = [s.getpixel((x, y)) for x in (3, s.width - 4) for y in (3, s.height - 4)]
    bg = tuple(round(statistics.mean(c[i] for c in corners)) for i in range(3))
    whites = [c for c in px if min(c) > 175]
    ink = tuple(round(statistics.mean(c[i] for c in whites)) for i in range(3)) if whites else (255, 255, 255)
    accents = []
    for c in px:
        hh, ss, vv = colorsys.rgb_to_hsv(*[x / 255 for x in c])
        if ss > 0.32 and vv > 0.40:
            accents.append((c, hh))
    accent = None
    if accents:
        # cor de destaque dominante = hue mais frequente (bucket) -> media
        buckets = Counter(round(hh * 12) for _, hh in accents)
        top_bucket = buckets.most_common(1)[0][0]
        grp = [c for c, hh in accents if round(hh * 12) == top_bucket]
        accent = tuple(round(statistics.mean(c[i] for c in grp)) for i in range(3))
    pal = im.resize((120, 120)).quantize(colors=6).convert("RGB")
    palette = [hexd(c) for c, _ in Counter(pal.getdata()).most_common(6)]
    return {"file": os.path.basename(path), "w": w, "h": h, "aspect": aspect_label(w, h),
            "bg": bg, "ink": ink, "accent": accent, "palette": palette}

def median_color(colors):
    colors = [c for c in colors if c]
    if not colors:
        return None
    return tuple(round(statistics.median(c[i] for c in colors)) for i in range(3))

def derive(paths, name="Marca"):
    files = collect(paths)
    per = [analyze_one(f) for f in files]
    bg = median_color([p["bg"] for p in per])
    ink = median_color([p["ink"] for p in per])
    accent = median_color([p["accent"] for p in per])
    aspects = Counter(p["aspect"] for p in per)
    pal = Counter()
    for p in per:
        pal.update(p["palette"])
    return {
        "brand": name, "amostras": len(files),
        "tokens": {
            "fundo": hexd(bg) if bg else None,
            "texto": hexd(ink) if ink else None,
            "destaque": hexd(accent) if accent else None,
            "paleta": [c for c, _ in pal.most_common(8)],
        },
        "formatos_detectados": dict(aspects),
        "amostras_detalhe": [{**p, "bg": hexd(p["bg"]), "ink": hexd(p["ink"]),
                              "accent": hexd(p["accent"]) if p["accent"] else None} for p in per[:30]],
    }

if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    name = sys.argv[sys.argv.index("--name") + 1] if "--name" in sys.argv else "Marca"
    out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else "design_system.json"
    ds = derive(a, name)
    open(out, "w", encoding="utf-8").write(json.dumps(ds, ensure_ascii=False, indent=2))
    print(json.dumps({k: v for k, v in ds.items() if k != "amostras_detalhe"}, ensure_ascii=False, indent=2))
    print("-> salvo em", out)
