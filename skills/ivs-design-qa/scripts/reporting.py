#!/usr/bin/env python3
"""Relatórios redigidos do IVS Design QA."""
from __future__ import annotations

import html
import json
import os
from pathlib import Path
from typing import Any


def _badge(status: str) -> tuple[str, str]:
    if status == "PASS":
        return "Aprovado", "ok"
    if status == "PASS_WITH_CONCERNS":
        return "Aprovado com ressalvas", "warn"
    return "Bloqueado", "bad"


def _issue_rows(items: list[dict[str, Any]]) -> str:
    if not items:
        return '<p class="empty">Nenhuma ocorrência.</p>'
    return "".join(
        f'<li><code>{html.escape(str(item.get("code", "unknown")))}</code>'
        f'<span>{html.escape(str(item.get("component", "gate")))}</span>'
        f'<b>{int(item.get("count", 1))}</b></li>'
        for item in items
    )


def render_html(report: dict[str, Any]) -> str:
    label, css_class = _badge(report["status"])
    metrics = report.get("metrics") or {}
    governance = report.get("governance") or {}
    components = report.get("components") or {}
    component_cards = "".join(
        f'<article><h3>{html.escape(name.replace("_", " ").title())}</h3>'
        f'<strong>{"OK" if data.get("ok") else "ATENÇÃO"}</strong>'
        f'<p>Executado: {"sim" if data.get("ran", True) else "não"}</p></article>'
        for name, data in components.items()
    )
    return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>IVS Design QA · {html.escape(report['status'])}</title>
<style>
:root{{--ink:#211d17;--muted:#6f685d;--paper:#f7f3eb;--card:#fffdf8;--gold:#a88942;--line:#ded5c6;--ok:#25734a;--warn:#a35d08;--bad:#a52c2c}}*{{box-sizing:border-box}}body{{margin:0;background:linear-gradient(135deg,#f3ede2,#fffdf8);color:var(--ink);font:16px/1.55 Inter,system-ui,sans-serif}}main{{width:min(1120px,calc(100% - 32px));margin:40px auto 80px}}header{{padding:38px;border:1px solid var(--line);border-radius:28px;background:rgba(255,253,248,.92);box-shadow:0 24px 70px rgba(60,45,20,.09)}}.eyebrow{{letter-spacing:.16em;text-transform:uppercase;color:var(--gold);font-weight:800;font-size:.75rem}}h1{{font:700 clamp(2rem,5vw,4.5rem)/.96 Georgia,serif;margin:.55rem 0 1rem}}.badge{{display:inline-flex;border-radius:999px;padding:9px 14px;color:white;font-weight:800}}.badge.ok{{background:var(--ok)}}.badge.warn{{background:var(--warn)}}.badge.bad{{background:var(--bad)}}.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:18px 0}}article,section{{background:var(--card);border:1px solid var(--line);border-radius:20px;padding:22px}}article h3{{font-size:.78rem;text-transform:uppercase;color:var(--muted);letter-spacing:.08em;margin:0 0 10px}}article strong{{font-size:1.4rem}}section{{margin-top:18px}}section h2{{font:700 1.65rem Georgia,serif;margin-top:0}}ul{{list-style:none;padding:0;margin:0;display:grid;gap:8px}}li{{display:grid;grid-template-columns:1fr auto auto;gap:14px;align-items:center;padding:10px 12px;border-radius:12px;background:#f5f0e7}}code{{color:#714f13;font-weight:700}}.empty{{color:var(--muted)}}footer{{padding:26px 4px;color:var(--muted);font-size:.88rem}}@media(max-width:760px){{main{{width:min(100% - 20px,1120px);margin-top:12px}}header{{padding:26px 22px;border-radius:22px}}.grid{{grid-template-columns:1fr 1fr}}li{{grid-template-columns:1fr auto}}li span{{display:none}}}}@media(max-width:430px){{.grid{{grid-template-columns:1fr}}}}
</style></head><body><main><header><div class="eyebrow">Instituto Vital Slim · Gate interno</div><h1>IVS Design QA</h1><span class="badge {css_class}">{label}</span><p>Artefato: <b>{html.escape(report['artifact_type'])}</b> · modo de dados: <b>{html.escape(report['data_mode'])}</b></p></header>
<div class="grid"><article><h3>Seções</h3><strong>{int(metrics.get('sections', 0))}</strong></article><article><h3>Bloqueios</h3><strong>{len(report.get('blockers') or [])}</strong></article><article><h3>Ressalvas</h3><strong>{len(report.get('concerns') or [])}</strong></article><article><h3>Original</h3><strong>{'Íntegro' if governance.get('original_unchanged') else 'Alterado'}</strong></article></div>
<section><h2>Componentes executados</h2><div class="grid">{component_cards}</div></section><section><h2>Bloqueios</h2><ul>{_issue_rows(report.get('blockers') or [])}</ul></section><section><h2>Ressalvas</h2><ul>{_issue_rows(report.get('concerns') or [])}</ul></section>
<footer>Relatório interno. Não publicar. Não enviar ao paciente. Evidências locais e redigidas; nenhuma promessa de resultado clínico.</footer></main></body></html>"""


def _atomic_write(path: Path, content: str, mode: int) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, mode)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    os.replace(temporary, path)
    os.chmod(path, mode)


def write_reports(report: dict[str, Any], out_dir: Path, sensitive: bool = False) -> dict[str, str]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True, mode=0o700 if sensitive else 0o755)
    if sensitive:
        os.chmod(out_dir, 0o700)
    json_path = out_dir / "ivs-design-qa.report.json"
    html_path = out_dir / "ivs-design-qa.report.html"
    file_mode = 0o600 if sensitive else 0o644
    _atomic_write(json_path, json.dumps(report, ensure_ascii=False, indent=2), file_mode)
    _atomic_write(html_path, render_html(report), file_mode)
    return {"report_json": str(json_path), "report_html": str(html_path)}
