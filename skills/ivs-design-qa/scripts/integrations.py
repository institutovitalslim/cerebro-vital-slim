#!/usr/bin/env python3
"""Adaptadores redigidos para ferramentas IVS existentes."""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
from pathlib import Path
from typing import Any


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _issue(code: str, severity: str, count: int = 1) -> dict[str, Any]:
    return {"code": code, "severity": severity, "count": count}


def _run_process(command: list[str], *, timeout: int, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    process = subprocess.Popen(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired as error:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            process.communicate(timeout=1)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.communicate()
        raise subprocess.TimeoutExpired(command, timeout, output=error.output, stderr=error.stderr) from error
    return subprocess.CompletedProcess(command, process.returncode, stdout, stderr)


def _resolve_executable(executable: str) -> str | None:
    candidate = Path(executable)
    if candidate.is_absolute() or "/" in executable:
        return str(candidate) if candidate.is_file() else None
    return shutil.which(executable)


def run_ivs_site(input_path: Path, executable: str = "ivs-site", timeout: int = 60) -> dict[str, Any]:
    resolved = _resolve_executable(executable)
    if not resolved:
        return {
            "available": False,
            "ran": False,
            "ok": True,
            "blockers": [],
            "concerns": [_issue("ivs_site_unavailable", "concern")],
        }
    try:
        proc = _run_process(
            [resolved, "--json", "validate", str(Path(input_path).resolve())],
            timeout=timeout,
        )
        data = json.loads(proc.stdout or "{}")
        issues = list(data.get("issues") or [])
        source_text = Path(input_path).read_text(encoding="utf-8", errors="ignore")
        todo_words = re.findall(r"\btodo\b", source_text, flags=re.IGNORECASE)
        portuguese_lowercase_todo_only = bool(todo_words) and all(word == "todo" for word in todo_words)
        known_false_positive = r"blocked_placeholder:\bTODO\b"
        filtered_issues = [
            item for item in issues
            if str(item) == known_false_positive and portuguese_lowercase_todo_only
        ]
        remaining_issues = [item for item in issues if item not in filtered_issues]
        only_known_false_positives = bool(filtered_issues) and not remaining_issues
        ok = (bool(data.get("ok")) and proc.returncode == 0) or only_known_false_positives
        issue_count = len(remaining_issues)
        return {
            "available": True,
            "ran": True,
            "ok": ok,
            "returncode": proc.returncode,
            "issues_count": issue_count,
            "filtered_issues_count": len(filtered_issues),
            "blockers": [] if ok else [_issue("ivs_site_validation_failed", "blocker", max(1, issue_count))],
            "concerns": [],
        }
    except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError):
        return {
            "available": True,
            "ran": True,
            "ok": False,
            "blockers": [_issue("ivs_site_execution_error", "blocker")],
            "concerns": [],
        }


def run_browser_probe(
    input_path: Path,
    out_dir: Path,
    script_path: Path | None = None,
    timeout: int = 120,
) -> dict[str, Any]:
    script = Path(script_path) if script_path else Path(__file__).resolve().parent / "browser_probe.mjs"
    if not script.is_file() or not shutil.which("node"):
        return {
            "available": False,
            "ran": False,
            "ok": False,
            "viewports": [],
            "blockers": [_issue("browser_probe_unavailable", "blocker")],
            "concerns": [],
        }
    try:
        proc = _run_process(
            ["node", str(script), "--input", str(Path(input_path).resolve()), "--out-dir", str(Path(out_dir).resolve())],
            timeout=timeout,
        )
        data = json.loads(proc.stdout or "{}")
        data_ok = data.get("ok")
        raw_blockers = data.get("blockers")
        raw_concerns = data.get("concerns")
        viewports = data.get("viewports")
        blockers = list(raw_blockers) if isinstance(raw_blockers, list) else []
        expected_code = 0 if data_ok is True else 2
        valid_exit = proc.returncode == expected_code
        viewport_names = {item.get("name") for item in viewports if isinstance(item, dict)} if isinstance(viewports, list) else set()
        contract_valid = (
            isinstance(data_ok, bool)
            and isinstance(raw_blockers, list)
            and isinstance(raw_concerns, list)
            and isinstance(viewports, list)
            and viewport_names == {"desktop", "mobile"}
            and ((data_ok is True and not blockers) or (data_ok is False and bool(blockers)))
        )
        if not valid_exit:
            blockers.append(_issue("browser_probe_execution_error", "blocker"))
        if not contract_valid:
            blockers.append(_issue("browser_probe_contract_invalid", "blocker"))
        return {
            "available": True,
            "ran": True,
            "ok": data_ok is True and valid_exit and contract_valid,
            "returncode": proc.returncode,
            "viewports": viewports if isinstance(viewports, list) else [],
            "blockers": blockers,
            "concerns": raw_concerns if isinstance(raw_concerns, list) else [],
        }
    except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError):
        return {
            "available": True,
            "ran": True,
            "ok": False,
            "viewports": [],
            "blockers": [_issue("browser_probe_execution_error", "blocker")],
            "concerns": [],
        }


def default_visual_layer_script() -> Path:
    return Path(__file__).resolve().parents[2] / "ivs-visual-layer" / "scripts" / "ivs_visual_layer.py"


def run_visual_layer(
    input_path: Path,
    out_dir: Path,
    mode: str,
    script_path: Path | None = None,
    timeout: int = 60,
) -> dict[str, Any]:
    input_path = Path(input_path).resolve()
    out_dir = Path(out_dir).resolve()
    script = Path(script_path) if script_path else default_visual_layer_script()
    if not script.is_file():
        return {
            "available": False,
            "ran": False,
            "ok": True,
            "original_unchanged": True,
            "blockers": [],
            "concerns": [_issue("visual_layer_unavailable", "concern")],
        }
    before = sha256_file(input_path)
    try:
        proc = _run_process(
            [sys.executable, str(script), "--input", str(input_path), "--out-dir", str(out_dir), "--mode", mode],
            timeout=timeout,
        )
        after = sha256_file(input_path)
        unchanged = before == after
        data = json.loads(proc.stdout or "{}")
        data_ok = data.get("ok")
        output_html_value = data.get("output_html")
        audit_json_value = data.get("audit_json")
        sections_value = data.get("sections_count")
        risks_value = data.get("risks")

        def valid_declared_output(value: Any, suffix: str) -> bool:
            if not isinstance(value, str) or not value:
                return False
            candidate = Path(value)
            try:
                resolved_candidate = candidate.resolve(strict=True)
            except (OSError, RuntimeError):
                return False
            return (
                candidate.suffix.lower() == suffix
                and candidate.is_file()
                and not candidate.is_symlink()
                and resolved_candidate.is_relative_to(out_dir)
            )

        declared_outputs_valid = (
            valid_declared_output(output_html_value, ".html")
            and valid_declared_output(audit_json_value, ".json")
        ) if data_ok is True else True
        contract_valid = (
            isinstance(data_ok, bool)
            and isinstance(sections_value, int)
            and not isinstance(sections_value, bool)
            and sections_value >= 0
            and isinstance(risks_value, list)
            and declared_outputs_valid
        )
        ok = proc.returncode == 0 and data_ok is True and unchanged and contract_valid
        blockers: list[dict[str, Any]] = []
        if not unchanged:
            blockers.append(_issue("original_modified_by_visual_layer", "blocker"))
        if proc.returncode != 0 or data_ok is not True:
            blockers.append(_issue("visual_layer_execution_error", "blocker"))
        if not contract_valid:
            blockers.append(_issue("visual_layer_contract_invalid", "blocker"))
        return {
            "available": True,
            "ran": True,
            "ok": ok,
            "returncode": proc.returncode,
            "output_html": str(output_html_value) if contract_valid and data_ok is True else "",
            "audit_json": str(audit_json_value) if contract_valid and data_ok is True else "",
            "sections_count": sections_value if isinstance(sections_value, int) and not isinstance(sections_value, bool) else 0,
            "risks_count": len(risks_value) if isinstance(risks_value, list) else 0,
            "original_unchanged": unchanged,
            "blockers": blockers,
            "concerns": [],
        }
    except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError):
        unchanged = sha256_file(input_path) == before
        blockers = [_issue("visual_layer_execution_error", "blocker")]
        if not unchanged:
            blockers.append(_issue("original_modified_by_visual_layer", "blocker"))
        return {
            "available": True,
            "ran": True,
            "ok": False,
            "original_unchanged": unchanged,
            "blockers": blockers,
            "concerns": [],
        }
