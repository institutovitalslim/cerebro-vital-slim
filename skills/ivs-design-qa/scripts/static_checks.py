#!/usr/bin/env python3
"""Verificações estáticas redigidas para o IVS Design QA."""
from __future__ import annotations

import hashlib
import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

MEDIA_RE = re.compile(r"@media\s*\(", re.IGNORECASE)
PLACEHOLDER_RE = re.compile(
    r"\bFIXME\b|(?i:lorem\s+ipsum|\[(?:placeholder|preencher|inserir)[^\]]*\])"
)
TODO_WORD_RE = re.compile(r"\btodo\b", re.IGNORECASE)
EMAIL_RE = re.compile(r"(?<![\w.+-])[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}(?![\w.-])", re.IGNORECASE)
CPF_RE = re.compile(r"(?<!\d)\d{3}\.?\d{3}\.?\d{3}-?\d{2}(?!\d)")
PHONE_RE = re.compile(r"(?<!\d)(?:\+?55\s*)?(?:\(?\d{2}\)?\s*)?(?:9\s*)?\d{4}[-\s]?\d{4}(?!\d)")
EXTERNAL_LINK_RE = re.compile(r"href=[\"']https?://", re.IGNORECASE)


class _StructureParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.has_doctype = False
        self.has_html = False
        self.has_viewport = False
        self.has_title_text = False
        self.sections = 0
        self._in_title = False

    def handle_decl(self, decl: str) -> None:
        if decl.strip().lower() == "doctype html":
            self.has_doctype = True

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        normalized_tag = tag.lower()
        if normalized_tag == "html":
            self.has_html = True
        elif normalized_tag == "section":
            self.sections += 1
        elif normalized_tag == "title":
            self._in_title = True
        elif normalized_tag == "meta":
            attributes = {name.lower(): (value or "").lower() for name, value in attrs}
            if attributes.get("name") == "viewport":
                self.has_viewport = True

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title and data.strip():
            self.has_title_text = True


def _issue(code: str, severity: str, count: int = 1) -> dict[str, Any]:
    return {"code": code, "severity": severity, "count": count}


def _count_identifiers(src: str) -> dict[str, int]:
    return {
        "email": len(EMAIL_RE.findall(src)),
        "cpf": len(CPF_RE.findall(src)),
        "phone": len(PHONE_RE.findall(src)),
    }


def scan_html(path: Path, artifact_type: str, data_mode: str) -> dict[str, Any]:
    """Analisa HTML sem retornar conteúdo textual ou identificadores encontrados."""
    path = Path(path)
    if artifact_type not in {"site", "patient-presentation", "internal-report"}:
        raise ValueError("artifact_type inválido")
    if data_mode not in {"anonymous", "sensitive-local"}:
        raise ValueError("data_mode inválido")

    blockers: list[dict[str, Any]] = []
    concerns: list[dict[str, Any]] = []
    if not path.is_file():
        return {
            "source": str(path),
            "source_sha256": "",
            "blockers": [_issue("input_missing", "blocker")],
            "concerns": [],
            "metrics": {"bytes": 0, "sections": 0, "direct_identifier_counts": {"email": 0, "cpf": 0, "phone": 0}},
            "governance": {
                "original_unchanged": True,
                "patient_send_ready": False,
                "external_publish": False,
                "sensitive_outputs": data_mode == "sensitive-local",
            },
        }

    raw = path.read_bytes()
    src = raw.decode("utf-8", errors="replace")
    digest = hashlib.sha256(raw).hexdigest()
    structure = _StructureParser()
    structure.feed(src)
    structure.close()
    sections = structure.sections
    identifiers = _count_identifiers(src)

    if not raw:
        blockers.append(_issue("input_empty", "blocker"))
    if not structure.has_doctype:
        blockers.append(_issue("doctype_missing", "blocker"))
    if not structure.has_html:
        blockers.append(_issue("html_root_missing", "blocker"))
    if not structure.has_title_text:
        blockers.append(_issue("title_missing", "blocker"))
    if not structure.has_viewport:
        blockers.append(_issue("viewport_missing", "blocker"))
    if sections < 1:
        blockers.append(_issue("semantic_section_missing", "blocker"))
    placeholder_count = len(PLACEHOLDER_RE.findall(src))
    placeholder_count += sum(match.group(0) != "todo" for match in TODO_WORD_RE.finditer(src))
    if placeholder_count:
        blockers.append(_issue("placeholder_detected", "blocker", placeholder_count))
    if artifact_type == "patient-presentation" and data_mode == "anonymous" and any(identifiers.values()):
        blockers.append(_issue("direct_identifier_detected", "blocker", sum(identifiers.values())))

    if not MEDIA_RE.search(src):
        concerns.append(_issue("media_query_missing", "concern"))
    if sections < 6:
        concerns.append(_issue("few_sections_detected", "concern", sections))
    if artifact_type == "patient-presentation" and EXTERNAL_LINK_RE.search(src):
        concerns.append(_issue("external_link_in_patient_presentation", "concern"))

    return {
        "source": str(path.resolve()),
        "source_sha256": digest,
        "artifact_type": artifact_type,
        "data_mode": data_mode,
        "blockers": blockers,
        "concerns": concerns,
        "metrics": {
            "bytes": len(raw),
            "lines": src.count("\n") + 1,
            "sections": sections,
            "direct_identifier_counts": identifiers,
            "external_links": len(EXTERNAL_LINK_RE.findall(src)),
        },
        "governance": {
            "original_unchanged": True,
            "patient_send_ready": False,
            "external_publish": False,
            "sensitive_outputs": data_mode == "sensitive-local",
        },
    }
