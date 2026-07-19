#!/usr/bin/env python3
"""IVS Visual Layer — piloto local/read-only inspirado funcionalmente no Onlook.

Não copia código externo. Instrumenta uma cópia de HTML IVS para revisão visual,
com navegação por layers/seções, contorno seguro, checklist e auditoria JSON.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import time
from collections import Counter
from pathlib import Path
from typing import Any

SECTION_RE = re.compile(r'<section\b([^>]*)>', re.IGNORECASE)
ID_RE = re.compile(r'\bid=["\']([^"\']+)["\']', re.IGNORECASE)
CLASS_RE = re.compile(r'\bclass=["\']([^"\']*)["\']', re.IGNORECASE)
TITLE_RE = re.compile(r'<title>(.*?)</title>', re.IGNORECASE | re.DOTALL)
STYLE_CLOSE_RE = re.compile(r'</style\s*>', re.IGNORECASE)
BODY_OPEN_RE = re.compile(r'<body\b([^>]*)>', re.IGNORECASE)
BODY_CLOSE_RE = re.compile(r'</body\s*>', re.IGNORECASE)


def slugify(value: str, fallback: str) -> str:
    value = re.sub(r'[^a-zA-Z0-9_-]+', '-', value.strip().lower()).strip('-')
    return value or fallback


def detect_sections(src: str) -> list[dict[str, Any]]:
    sections: list[dict[str, Any]] = []
    for idx, match in enumerate(SECTION_RE.finditer(src), start=1):
        attrs = match.group(1) or ''
        id_match = ID_RE.search(attrs)
        class_match = CLASS_RE.search(attrs)
        sid = id_match.group(1) if id_match else f'ivs-layer-{idx:02d}'
        cls = class_match.group(1) if class_match else ''
        # find first heading soon after section start
        chunk = src[match.end(): match.end() + 2500]
        h = re.search(r'<h[1-4][^>]*>(.*?)</h[1-4]>', chunk, re.I | re.S)
        label = re.sub(r'<[^>]+>', ' ', h.group(1)) if h else sid
        label = re.sub(r'\s+', ' ', html.unescape(label)).strip()[:90]
        sections.append({'index': idx, 'id': sid, 'class': cls, 'label': label or sid})
    return sections


def class_stats(src: str) -> list[tuple[str, int]]:
    c: Counter[str] = Counter()
    for cl in CLASS_RE.findall(src):
        for item in cl.split():
            if item:
                c[item] += 1
    return c.most_common(40)


def inject_section_metadata(src: str, sections: list[dict[str, Any]]) -> str:
    counter = {'i': 0}

    def repl(match: re.Match[str]) -> str:
        counter['i'] += 1
        idx = counter['i']
        attrs = match.group(1) or ''
        section = sections[idx - 1]
        new_attrs = attrs
        if not ID_RE.search(new_attrs):
            new_attrs += f' id="{section["id"]}"'
        if 'data-ivs-layer=' not in new_attrs:
            safe_label = html.escape(section['label'], quote=True)
            new_attrs += f' data-ivs-layer="{idx:02d}" data-ivs-label="{safe_label}"'
        return '<section' + new_attrs + '>'

    return SECTION_RE.sub(repl, src)


def build_overlay(sections: list[dict[str, Any]], audit_id: str) -> str:
    nav = []
    for s in sections:
        nav.append(
            f'<a class="ivslayer-link" href="#{html.escape(s["id"], quote=True)}">'
            f'<span>{s["index"]:02d}</span>{html.escape(s["label"] or s["id"])}</a>'
        )
    return f'''
<div id="ivs-visual-layer-panel" aria-label="Painel interno IVS Visual Layer">
  <div class="ivslayer-head">
    <strong>IVS Visual Layer</strong>
    <button type="button" onclick="document.documentElement.classList.toggle('ivs-layer-off')">liga/desliga</button>
  </div>
  <div class="ivslayer-meta">QA interno · audit {audit_id} · {len(sections)} seções</div>
  <div class="ivslayer-links">{''.join(nav)}</div>
  <div class="ivslayer-check">
    <b>Checklist</b>
    <label><input type="checkbox"> hierarquia clara</label>
    <label><input type="checkbox"> mobile sem quebra</label>
    <label><input type="checkbox"> sem placeholder</label>
    <label><input type="checkbox"> CTA localizado</label>
    <label><input type="checkbox"> conteúdo clínico sem promessa indevida</label>
  </div>
</div>
<script>
(() => {{
  const panel = document.getElementById('ivs-visual-layer-panel');
  document.querySelectorAll('section[data-ivs-layer]').forEach(sec => {{
    sec.addEventListener('mouseenter', () => {{
      const label = sec.getAttribute('data-ivs-label') || sec.id;
      panel?.style.setProperty('--current-layer', '"' + label.replace(/"/g, '') + '"');
    }});
  }});
}})();
</script>
'''


def build_css() -> str:
    return r'''
/* === IVS VISUAL LAYER · QA interno, não-paciente === */
@media screen {
  html:not(.ivs-layer-off) section[data-ivs-layer]{ position:relative; outline:1px dashed rgba(159,136,68,.32); outline-offset:-8px; }
  html:not(.ivs-layer-off) section[data-ivs-layer]::before{
    content:"Layer " attr(data-ivs-layer) " · " attr(data-ivs-label);
    position:absolute; top:10px; left:10px; z-index:30;
    font:600 10px/1.2 Inter, system-ui, sans-serif; letter-spacing:.12em; text-transform:uppercase;
    color:#6B5A2B; background:rgba(255,250,242,.92); border:1px solid rgba(107,90,43,.2);
    border-radius:999px; padding:6px 9px; pointer-events:none; max-width:min(70vw,720px); white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
  }
  #ivs-visual-layer-panel{ position:fixed; right:18px; top:86px; width:310px; max-height:calc(100vh - 110px); overflow:auto; z-index:9999;
    background:rgba(31,26,18,.92); color:#FFF8E8; border:1px solid rgba(212,188,121,.45); border-radius:20px; box-shadow:0 20px 70px rgba(0,0,0,.28); backdrop-filter: blur(12px);
    font-family:Inter, system-ui, sans-serif; padding:14px; }
  .ivslayer-head{display:flex; align-items:center; justify-content:space-between; gap:10px; margin-bottom:8px}.ivslayer-head strong{font-size:14px; letter-spacing:.08em; text-transform:uppercase}.ivslayer-head button{border:1px solid rgba(212,188,121,.45);background:#FFF8E8;color:#1F1A12;border-radius:999px;padding:5px 9px;font-size:11px;cursor:pointer}.ivslayer-meta{font-size:11px;color:#D4BC79;margin-bottom:10px}.ivslayer-links{display:grid; gap:6px}.ivslayer-link{display:flex;gap:8px;align-items:flex-start;color:#FFF8E8;text-decoration:none;border:1px solid rgba(255,255,255,.08);border-radius:12px;padding:8px;font-size:12px;line-height:1.25}.ivslayer-link:hover{background:rgba(212,188,121,.14)}.ivslayer-link span{color:#D4BC79;font-weight:700}.ivslayer-check{margin-top:12px;border-top:1px solid rgba(255,255,255,.12);padding-top:10px;display:grid;gap:7px;font-size:12px}.ivslayer-check b{color:#D4BC79}.ivslayer-check label{display:flex;gap:7px;align-items:center}
}
@media print { #ivs-visual-layer-panel{display:none!important} section[data-ivs-layer]{outline:none!important} section[data-ivs-layer]::before{display:none!important} }
@media (max-width: 920px){ #ivs-visual-layer-panel{ position:fixed; left:12px; right:12px; top:auto; bottom:12px; width:auto; max-height:35vh; } }
'''


def build_audit(src: str, out_html: Path, sections: list[dict[str, Any]], mode: str) -> dict[str, Any]:
    title = ''
    if m := TITLE_RE.search(src):
        title = re.sub(r'\s+', ' ', html.unescape(m.group(1))).strip()
    lower = src.lower()
    risks = []
    if 'lorem ipsum' in lower or re.search(r'\[(?:placeholder|preencher|inserir)[^\]]*\]', lower) or re.search(r'\bTODO\b|\bFIXME\b', src):
        risks.append('placeholder_or_todo_detected')
    if len(sections) < 6:
        risks.append('few_sections_detected')
    if 'whatsapp' in lower and 'href=' in lower:
        risks.append('contains_whatsapp_link_check_before_patient_send')
    if not re.search(r'@media\s*\(', src, re.I):
        risks.append('no_media_queries_detected')
    return {
        'ok': True,
        'mode': mode,
        'source_sha256_16': hashlib.sha256(src.encode('utf-8', 'ignore')).hexdigest()[:16],
        'generated_at_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'output_html': str(out_html),
        'title': title,
        'size_bytes': len(src.encode('utf-8', 'ignore')),
        'line_count': src.count('\n') + 1,
        'sections_count': len(sections),
        'sections': sections,
        'top_classes': class_stats(src),
        'risks': risks,
        'governance': {
            'original_unchanged': True,
            'patient_send_ready': False,
            'purpose': 'internal_visual_qa_smoke',
            'external_publish': False,
        }
    }


def run(input_path: Path, out_dir: Path, mode: str) -> dict[str, Any]:
    src = input_path.read_text(encoding='utf-8', errors='ignore')
    sections = detect_sections(src)
    audit_id = hashlib.sha256((str(input_path) + str(time.time())).encode()).hexdigest()[:8]
    transformed = inject_section_metadata(src, sections)
    css = build_css()
    if STYLE_CLOSE_RE.search(transformed):
        transformed = STYLE_CLOSE_RE.sub(css + '\n</style>', transformed, count=1)
    else:
        transformed = transformed.replace('</head>', f'<style>{css}</style></head>')
    overlay = build_overlay(sections, audit_id)
    if BODY_CLOSE_RE.search(transformed):
        transformed = BODY_CLOSE_RE.sub(overlay + '\n</body>', transformed, count=1)
    else:
        transformed += overlay
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = input_path.stem
    out_html = out_dir / f'{stem}-visual-layer.html'
    out_json = out_dir / f'{stem}-visual-layer.audit.json'
    out_html.write_text(transformed, encoding='utf-8')
    audit = build_audit(src, out_html, sections, mode)
    audit['audit_json'] = str(out_json)
    out_json.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding='utf-8')
    return audit


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    ap.add_argument('--out-dir', required=True)
    ap.add_argument('--mode', default='generic-html')
    args = ap.parse_args()
    audit = run(Path(args.input), Path(args.out_dir), args.mode)
    print(json.dumps({
        'ok': audit['ok'],
        'output_html': audit['output_html'],
        'audit_json': audit['audit_json'],
        'sections_count': audit['sections_count'],
        'risks': audit['risks'],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
