#!/usr/bin/env python3
"""Sync QuarkClinic patients into Clara's patient history/blocklist.

Purpose:
- QuarkClinic is the source of truth for patient status.
- The WhatsApp history sheet `pacientes` must include every patient phone found in QuarkClinic.
- Clara local exclusions must include those phones as patient-like to fail closed for follow-up/admin sends.

Default mode is dry-run. Use --apply to write.
Output is sanitized: no names/phones are printed.
"""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import os
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

SPREADSHEET_ID = "1QXvRhElCx1t7mxMAwGkcvh5V7YyKLjP9zozSGH7LHnM"
ACCOUNT = "institutovitalslim@gmail.com"
PATIENTS_RANGE = "pacientes!A:J"
PATIENTS_HEADER = [
    "phone",
    "sender_name",
    "chat_name",
    "total_messages",
    "inbound_messages",
    "outbound_messages",
    "first_message_at",
    "last_message_at",
    "last_message_text",
    "timestamp_zapi",
]
QC_HELPER = Path("/root/cerebro-vital-slim/skills/omie-cadastro-paciente/scripts/cadastro_paciente_omie.py")
EXCLUSIONS_FILE = Path("/root/.openclaw/workspace/ops/zapi_bridge/clara_exclusions.json")
REPORT_DIR = Path("/root/cerebro-vital-slim/cerebro/operacional/clara-quarkclinic-patient-sync")


def load_env_file(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.exists():
        return out
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def runtime_env() -> dict[str, str]:
    env = os.environ.copy()
    for p in (Path("/root/.hermes/shared/ivs-runtime.env"), Path("/root/.openclaw/.env.runtime")):
        env.update(load_env_file(p))
    return env


def norm_phone(raw: Any) -> str:
    d = re.sub(r"\D", "", str(raw or ""))
    if len(d) == 10 or len(d) == 11:
        d = "55" + d
    if len(d) == 12 and d.startswith("55"):
        # landline or old mobile; keep as is
        return d
    if len(d) == 13 and d.startswith("55"):
        return d
    return ""


def phone_variants(phone: str) -> set[str]:
    d = norm_phone(phone)
    out = {d} if d else set()
    if d.startswith("55") and len(d) == 13 and d[4] == "9":
        out.add(d[:4] + d[5:])
    if d.startswith("55") and len(d) == 12:
        subscriber = d[4:]
        if subscriber and subscriber[0] in "6789":
            out.add(d[:4] + "9" + subscriber)
    return {x for x in out if x}


def load_qc_helper():
    if not QC_HELPER.exists():
        raise SystemExit(f"QuarkClinic helper not found: {QC_HELPER}")
    spec = importlib.util.spec_from_file_location("qc_helper", str(QC_HELPER))
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    assert spec and spec.loader
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def iter_quark_patients(max_pages: int, workers: int = 16):
    qc = load_qc_helper()
    patients = list(qc.iter_quark_patients(max_pages=max_pages))

    def fetch(patient: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
        pid = patient.get("id")
        phones: list[str] = []
        if pid:
            try:
                status, payload = qc.quark_request("GET", f"/v1/pacientes/{pid}/telefones", timeout=25)
                if status < 400 and isinstance(payload, dict):
                    phones = payload.get("response", []) or []
            except Exception:
                phones = []
        return patient, phones

    with ThreadPoolExecutor(max_workers=max(1, workers)) as ex:
        futures = [ex.submit(fetch, p) for p in patients]
        for fut in as_completed(futures):
            yield fut.result()


def gog_get(range_a1: str) -> list[list[str]]:
    env = runtime_env()
    cmd = ["gog", "sheets", "get", "-a", ACCOUNT, SPREADSHEET_ID, range_a1, "-j"]
    cp = subprocess.run(cmd, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=90)
    if cp.returncode != 0:
        raise RuntimeError("gog_get_failed:" + cp.stderr[:300])
    return json.loads(cp.stdout or "{}").get("values", [])


def gog_append(rows: list[list[str]]) -> dict[str, Any]:
    if not rows:
        return {"ok": True, "appended": 0}
    env = runtime_env()
    total = 0
    responses = []
    for i in range(0, len(rows), 100):
        chunk = rows[i : i + 100]
        cmd = [
            "gog", "sheets", "append", "-a", ACCOUNT, SPREADSHEET_ID, PATIENTS_RANGE,
            "--values-json", json.dumps(chunk, ensure_ascii=False),
            "--input", "USER_ENTERED", "--insert", "INSERT_ROWS", "--no-input", "-j",
        ]
        cp = subprocess.run(cmd, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
        if cp.returncode != 0:
            raise RuntimeError("gog_append_failed:" + cp.stderr[:500])
        total += len(chunk)
        try:
            responses.append(json.loads(cp.stdout or "{}"))
        except Exception:
            responses.append({"raw": cp.stdout[:300]})
    return {"ok": True, "appended": total, "responses": responses[-3:]}


def existing_patient_phone_variants() -> set[str]:
    values = gog_get(PATIENTS_RANGE)
    if not values:
        return set()
    variants: set[str] = set()
    for row in values[1:]:
        for cell in row:
            p = norm_phone(cell)
            if p:
                variants.update(phone_variants(p))
    return variants


def load_exclusions() -> dict[str, Any]:
    if not EXCLUSIONS_FILE.exists():
        return {"phones": {}, "updated_at": None}
    try:
        data = json.loads(EXCLUSIONS_FILE.read_text(encoding="utf-8", errors="ignore"))
        if not isinstance(data, dict):
            return {"phones": {}, "updated_at": None}
        if not isinstance(data.get("phones"), dict):
            data["phones"] = {}
        return data
    except Exception:
        return {"phones": {}, "updated_at": None}


def sync_exclusions(patient_rows: list[dict[str, Any]], apply: bool) -> dict[str, Any]:
    state = load_exclusions()
    phones = state.setdefault("phones", {})
    now = int(time.time())
    added = 0
    preserved = 0
    for item in patient_rows:
        phone = item["phone"]
        for variant in phone_variants(phone):
            existing = phones.get(variant)
            if isinstance(existing, dict):
                source = str(existing.get("source") or "")
                reason = str(existing.get("reason") or "")
                if source == "manual" or source == "tiaro_lead_exception" or reason.startswith("lead_exception"):
                    preserved += 1
                    continue
            if not existing or not isinstance(existing, dict) or existing.get("source") not in {"quarkclinic_patient_sync", "quarkclinic_live_check"}:
                added += 1
            phones[variant] = {
                "name": item.get("name") or "Paciente QuarkClinic",
                "reason": "quarkclinic_patient_rc12",
                "source": "quarkclinic_patient_sync",
                "quark_id": item.get("quark_id"),
                "updated_at": now,
            }
    state["updated_at"] = now
    if apply:
        EXCLUSIONS_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"candidate_exclusion_updates": added, "preserved_exceptions": preserved, "path": str(EXCLUSIONS_FILE)}


def build_sync(max_pages: int, workers: int) -> tuple[list[dict[str, Any]], list[list[str]], dict[str, Any]]:
    existing = existing_patient_phone_variants()
    seen: set[str] = set()
    patient_rows: list[dict[str, Any]] = []
    append_rows: list[list[str]] = []
    stats = {"quark_patients_seen": 0, "patients_with_phone": 0, "duplicates_skipped": 0, "already_in_sheet": 0}
    now_ms = str(int(time.time() * 1000))
    today = dt.datetime.now(dt.timezone.utc).strftime("%Y/%m/%d")
    for patient, phones in iter_quark_patients(max_pages=max_pages, workers=workers):
        stats["quark_patients_seen"] += 1
        qid = patient.get("id")
        name = str(patient.get("nome") or "").strip()
        for raw_phone in phones:
            phone = norm_phone(raw_phone)
            if not phone:
                continue
            stats["patients_with_phone"] += 1
            variants = phone_variants(phone)
            key = sorted(variants)[0]
            if key in seen:
                stats["duplicates_skipped"] += 1
                continue
            seen.add(key)
            patient_rows.append({"phone": phone, "name": name, "quark_id": qid})
            if variants.intersection(existing):
                stats["already_in_sheet"] += 1
                continue
            append_rows.append([
                phone,
                "QuarkClinic",
                name or "Paciente QuarkClinic",
                "0",
                "0",
                "0",
                today,
                today,
                "Paciente QuarkClinic - bloqueio RC12",
                now_ms,
            ])
    return patient_rows, append_rows, stats


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="Write to Google Sheet and local exclusions")
    ap.add_argument("--max-pages", type=int, default=80)
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--quiet-no-change", action="store_true")
    args = ap.parse_args()

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    patient_rows, append_rows, stats = build_sync(args.max_pages, args.workers)
    exclusion_result = sync_exclusions(patient_rows, apply=args.apply)
    append_result = gog_append(append_rows) if args.apply else {"ok": True, "appended": 0, "dry_run": True}
    report = {
        "ok": True,
        "mode": "apply" if args.apply else "dry_run",
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "stats": stats,
        "quark_unique_patient_phones": len(patient_rows),
        "sheet_rows_to_append": len(append_rows),
        "sheet_append": {k: v for k, v in append_result.items() if k != "responses"},
        "exclusions": exclusion_result,
        "policy": "QuarkClinic patient source of truth; pacientes sheet and Clara exclusions updated fail-closed for RC12.",
    }
    out = REPORT_DIR / "latest.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.quiet_no_change and args.apply and not append_rows and not exclusion_result.get("candidate_exclusion_updates"):
        return
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
