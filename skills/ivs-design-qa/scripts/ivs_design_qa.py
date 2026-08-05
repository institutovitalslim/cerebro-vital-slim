#!/usr/bin/env python3
"""CLI orquestradora do IVS Design QA."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

from integrations import run_browser_probe, run_ivs_site, run_visual_layer, sha256_file
from reporting import write_reports
from static_checks import scan_html


def _tag(items: list[dict[str, Any]], component: str) -> list[dict[str, Any]]:
    return [{**item, "component": component} for item in items]


def _component_summary(data: dict[str, Any]) -> dict[str, Any]:
    summary: dict[str, Any] = {"ok": bool(data.get("ok")), "ran": bool(data.get("ran", True))}
    if "available" in data:
        summary["available"] = bool(data.get("available"))
    if "returncode" in data:
        summary["returncode"] = int(data["returncode"])
    return summary


def run_gate(
    input_path: Path,
    out_dir: Path,
    artifact_type: str,
    data_mode: str,
    ivs_site_executable: str = "ivs-site",
) -> tuple[dict[str, Any], dict[str, str]]:
    input_path = Path(input_path).resolve()
    out_dir = Path(out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    static = scan_html(input_path, artifact_type, data_mode)
    before = static.get("source_sha256") or (sha256_file(input_path) if input_path.is_file() else "")
    browser = run_browser_probe(input_path, out_dir / "browser") if input_path.is_file() else {
        "ok": False, "ran": False, "available": False, "blockers": [{"code": "browser_probe_not_run", "severity": "blocker"}], "concerns": [], "viewports": []
    }
    visual = run_visual_layer(input_path, out_dir / "visual-layer", artifact_type) if input_path.is_file() else {
        "ok": False, "ran": False, "available": False, "blockers": [{"code": "visual_layer_not_run", "severity": "blocker"}], "concerns": []
    }
    if artifact_type == "site" and input_path.is_file():
        site = run_ivs_site(input_path, executable=ivs_site_executable)
    else:
        site = {"ok": True, "ran": False, "available": True, "blockers": [], "concerns": []}

    blockers = []
    concerns = []
    for name, data in (("static", static), ("browser", browser), ("visual_layer", visual), ("ivs_site", site)):
        blockers.extend(_tag(data.get("blockers") or [], name))
        concerns.extend(_tag(data.get("concerns") or [], name))
    if visual.get("risks_count"):
        concerns.append({"code": "visual_layer_risks_detected", "severity": "concern", "count": int(visual["risks_count"]), "component": "visual_layer"})

    after = sha256_file(input_path) if input_path.is_file() else ""
    original_unchanged = bool(before) and before == after
    if input_path.is_file() and not original_unchanged:
        blockers.append({"code": "original_hash_changed", "severity": "blocker", "count": 1, "component": "governance"})

    status = "BLOCKED" if blockers else ("PASS_WITH_CONCERNS" if concerns else "PASS")
    source_value = "[sensitive-local-input]" if data_mode == "sensitive-local" else str(input_path)
    report = {
        "schema": "ivs-design-qa-v1",
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "status": status,
        "artifact_type": artifact_type,
        "data_mode": data_mode,
        "source": source_value,
        "source_sha256": before,
        "blockers": blockers,
        "concerns": concerns,
        "metrics": static.get("metrics") or {},
        "components": {
            "static": _component_summary({**static, "ok": not static.get("blockers"), "ran": True}),
            "browser": _component_summary(browser),
            "visual_layer": _component_summary(visual),
            "ivs_site": _component_summary(site),
        },
        "evidence": {
            "desktop_screenshot": str(out_dir / "browser" / "desktop.png"),
            "mobile_screenshot": str(out_dir / "browser" / "mobile.png"),
            "visual_layer_html": visual.get("output_html", ""),
            "visual_layer_audit": visual.get("audit_json", ""),
        },
        "governance": {
            "original_unchanged": original_unchanged,
            "patient_send_ready": False,
            "external_publish": False,
            "sensitive_outputs": data_mode == "sensitive-local",
        },
    }
    paths = write_reports(report, out_dir)
    return report, paths


def main() -> int:
    parser = argparse.ArgumentParser(description="Gate governado de QA visual do Instituto Vital Slim")
    parser.add_argument("--input", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--artifact-type", choices=["site", "patient-presentation", "internal-report"], required=True)
    parser.add_argument("--data-mode", choices=["anonymous", "sensitive-local"], default="anonymous")
    parser.add_argument("--ivs-site-executable", default="ivs-site")
    args = parser.parse_args()
    try:
        report, paths = run_gate(Path(args.input), Path(args.out_dir), args.artifact_type, args.data_mode, args.ivs_site_executable)
    except Exception as error:
        print(json.dumps({"status": "ERROR", "error_code": type(error).__name__}, ensure_ascii=False))
        return 1
    print(json.dumps({"status": report["status"], **paths}, ensure_ascii=False))
    return 2 if report["status"] == "BLOCKED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
