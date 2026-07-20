#!/usr/bin/env python3
"""Aplica IVS Motion Layer em HTML estático sem sobrescrever por padrão."""
from __future__ import annotations

import argparse
import html
import logging
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
LOGGER = logging.getLogger("ivs-motion-layer")

STYLE_ID = "ivs-motion-css"
SCRIPT_ID = "ivs-motion-js"
CONFIG_ID = "ivs-motion-config"


def read_text(path: Path) -> str:
    if not path.exists():
        LOGGER.error("Arquivo de entrada inexistente: %s", path)
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")


def ensure_local_assets(out_path: Path) -> tuple[str, str]:
    asset_dir = out_path.parent / "ivs-motion-assets"
    asset_dir.mkdir(parents=True, exist_ok=True)
    css_dest = asset_dir / "ivs-motion.css"
    js_dest = asset_dir / "ivs-motion.js"
    shutil.copy2(ASSETS / "ivs-motion.css", css_dest)
    shutil.copy2(ASSETS / "ivs-motion.js", js_dest)
    return "ivs-motion-assets/ivs-motion.css", "ivs-motion-assets/ivs-motion.js"


def build_config(profile: str, enable_vanta: bool, debug: bool) -> str:
    return (
        f'<script id="{CONFIG_ID}">\n'
        'window.IVSMotionConfig = {'
        f'profile: {profile!r}, lenis: true, gsap: true, vanta: {str(enable_vanta).lower()}, '
        f'debug: {str(debug).lower()}'
        '};\n'
        '</script>'
    )


def add_head_assets(doc: str, css_href: str, js_src: str, profile: str, enable_vanta: bool, debug: bool) -> str:
    if STYLE_ID in doc or SCRIPT_ID in doc:
        LOGGER.warning("HTML já parece conter IVS Motion Layer; mantendo uma única camada")
        doc = re.sub(r'\s*<link[^>]+id=["\']ivs-motion-css["\'][^>]*>', '', doc, flags=re.I)
        doc = re.sub(r'\s*<script[^>]+id=["\']ivs-motion-config["\'][\s\S]*?</script>', '', doc, flags=re.I)
        doc = re.sub(r'\s*<script[^>]+id=["\']ivs-motion-js["\'][^>]*></script>', '', doc, flags=re.I)
    tags = (
        f'  <link id="{STYLE_ID}" rel="stylesheet" href="{html.escape(css_href)}">\n'
        f'  {build_config(profile, enable_vanta, debug)}\n'
        f'  <script id="{SCRIPT_ID}" defer src="{html.escape(js_src)}"></script>\n'
    )
    if re.search(r'</head\s*>', doc, flags=re.I):
        return re.sub(r'</head\s*>', tags + '</head>', doc, count=1, flags=re.I)
    return tags + doc


def mark_body(doc: str, profile: str) -> str:
    if re.search(r'<body\b', doc, flags=re.I):
        def repl(match: re.Match[str]) -> str:
            tag = match.group(0)
            if 'ivs-motion-shell' in tag:
                return tag
            if 'class=' in tag:
                return re.sub(r'class=(["\'])(.*?)\1', lambda m: f'class={m.group(1)}{m.group(2)} ivs-motion-shell ivs-motion-profile-{profile}{m.group(1)}', tag, count=1)
            return tag[:-1] + f' class="ivs-motion-shell ivs-motion-profile-{profile}">'
        return re.sub(r'<body\b[^>]*>', repl, doc, count=1, flags=re.I)
    return '<body class="ivs-motion-shell ivs-motion-profile-%s">%s</body>' % (profile, doc)


def auto_mark_sections(doc: str, enable_vanta: bool) -> str:
    doc = re.sub(
        r'<section(?![^>]*data-ivs-motion)([^>]*)>',
        r'<section data-ivs-motion="fade-up" class="ivs-motion-section"\1>',
        doc,
        flags=re.I,
    )
    doc = re.sub(
        r'<div([^>]*class=["\'][^"\']*(?:card|metric|kpi|painel|panel)[^"\']*["\'][^>]*)(?![^>]*data-ivs-motion)>',
        r'<div\1 data-ivs-motion="card">',
        doc,
        flags=re.I,
    )
    if enable_vanta and 'data-ivs-vanta' not in doc:
        doc = re.sub(r'<(header|section)([^>]*class=["\'][^"\']*(?:hero|capa|cover)[^"\']*["\'][^>]*)>', r'<\1\2 data-ivs-vanta>', doc, count=1, flags=re.I)
    return doc


def apply_motion(input_path: Path, out_path: Path, profile: str, enable_vanta: bool, overwrite: bool, debug: bool, auto_mark: bool) -> Path:
    input_path = input_path.resolve()
    out_path = out_path.resolve()
    if out_path.exists() and out_path != input_path and not overwrite:
        raise FileExistsError(f"Saída já existe; use --overwrite: {out_path}")
    if out_path == input_path and not overwrite:
        raise ValueError("Para sobrescrever o arquivo de entrada, use --overwrite explicitamente")
    LOGGER.info("Aplicando IVS Motion Layer [input=%s, out=%s, profile=%s, vanta=%s]", input_path, out_path, profile, enable_vanta)
    doc = read_text(input_path)
    css_href, js_src = ensure_local_assets(out_path)
    doc = mark_body(doc, profile)
    if auto_mark:
        doc = auto_mark_sections(doc, enable_vanta)
    doc = add_head_assets(doc, css_href, js_src, profile, enable_vanta, debug)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(doc, encoding="utf-8")
    LOGGER.info("Motion aplicado com sucesso: %s", out_path)
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Aplica IVS Motion Layer em um HTML existente.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--profile", choices=["presentation", "landing", "minimal"], default="presentation")
    parser.add_argument("--vanta", action="store_true", help="Habilita background Vanta quando houver hero/capa")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--no-auto-mark", action="store_true", help="Não marca sections/cards automaticamente")
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
    apply_motion(args.input, args.out, args.profile, args.vanta, args.overwrite, args.debug, not args.no_auto_mark)
    print(args.out.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
