#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "ivs_context_compressor.py"


def run(cmd):
    return subprocess.run(cmd, text=True, capture_output=True, check=False)


def test_cli_compress_and_recover():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        sample = tmp / "clara.log"
        sample.write_text(
            "2026-06-25T07:00:00Z INFO webhook received phone=11900000000 messageId=MSG123456\n"
            "2026-06-25T07:00:02Z ERROR zapi-fail status_code=500 trace_id=TRACE999 token=TEST_SECRET_123456 email=anon@example.invalid\n"
            "2026-06-25T07:00:03Z INFO NO_REPLY lead aguardando resposta\n",
            encoding="utf-8",
        )
        out_dir = tmp / "reports"
        ev_dir = tmp / "evidence"
        proc = run([
            sys.executable,
            str(SCRIPT),
            "--input",
            str(sample),
            "--type",
            "clara-log",
            "--out-dir",
            str(out_dir),
            "--evidence-dir",
            str(ev_dir),
            "--format",
            "json",
        ])
        assert proc.returncode == 0, proc.stderr
        payload = json.loads(proc.stdout)
        assert payload["ok"] is True
        assert payload["summary"]["critical_line_count"] >= 2
        assert payload["summary"]["error_like_count"] >= 1
        assert payload["summary"]["redactions"].get("email") == 1
        assert payload["summary"]["redactions"].get("api_key") == 1
        assert payload["summary"]["redactions"].get("phone_br") >= 1
        assert payload["summary"]["reduction"]["estimated_tokens_original"] > 0
        assert payload["summary"]["reduction"]["estimated_tokens_compressed_context"] > 0
        assert "estimated_token_reduction_pct" in payload["summary"]["reduction"]
        md = Path(payload["outputs"]["markdown"]).read_text(encoding="utf-8")
        assert "anon@example.invalid" not in md
        assert "11900000000" not in md
        digest = payload["sha256"]
        rec = run([
            sys.executable,
            str(SCRIPT),
            "--recover",
            digest,
            "--evidence-dir",
            str(ev_dir),
        ])
        assert rec.returncode == 0, rec.stderr
        rec_payload = json.loads(rec.stdout)
        assert Path(rec_payload["original"]).exists()


def test_redact_mcp_token_in_url():
    spec = importlib.util.spec_from_file_location("ivs_context_compressor", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    redacted, counts = mod.redact("https://github.com/a/b?mcp_token=abc.def.ghi&x=1")
    assert "abc.def.ghi" not in redacted
    assert "[REDACTED_MCP_TOKEN]" in redacted
    assert counts["mcp_token"] == 1

    redacted_ts, counts_ts = mod.redact('{"generated_at": 1782371652, "messageId": "MSG987654321"}')
    assert "1782371652" in redacted_ts
    assert "MSG987654321" in redacted_ts
    assert "phone_br" not in counts_ts


def test_stdin_mode():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        proc = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--stdin",
                "--stdin-name",
                "pipe.log",
                "--type",
                "cron-log",
                "--out-dir",
                str(tmp / "reports"),
                "--evidence-dir",
                str(tmp / "evidence"),
                "--format",
                "json",
            ],
            input="2026-06-25T08:00:00Z ERROR cron failed status_code=500 request_id=REQPIPE123\n",
            text=True,
            capture_output=True,
            check=False,
        )
        assert proc.returncode == 0, proc.stderr
        payload = json.loads(proc.stdout)
        assert payload["ok"] is True
        assert payload["input_path"] == "stdin"
        assert payload["input_name"] == "pipe.log"
        assert payload["summary"]["error_like_count"] == 1
        assert Path(payload["outputs"]["json"]).exists()
        assert Path(payload["evidence"]["original_path"]).exists()


def test_cleanup_retention_dry_run_and_apply():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        out_dir = tmp / "reports"
        ev_dir = tmp / "evidence"
        out_dir.mkdir()
        ev_dir.mkdir()
        old_report = out_dir / "old.md"
        old_evidence = ev_dir / "old.log"
        fresh_report = out_dir / "fresh.md"
        protected = ev_dir / ".gitignore"
        for path in [old_report, old_evidence, fresh_report, protected]:
            path.write_text("x", encoding="utf-8")
        old_ts = time.time() - (3 * 86400)
        os.utime(old_report, (old_ts, old_ts))
        os.utime(old_evidence, (old_ts, old_ts))

        dry = run([
            sys.executable,
            str(SCRIPT),
            "--cleanup",
            "--cleanup-retention-days",
            "1",
            "--out-dir",
            str(out_dir),
            "--evidence-dir",
            str(ev_dir),
        ])
        assert dry.returncode == 0, dry.stderr
        dry_payload = json.loads(dry.stdout)
        assert dry_payload["mode"] == "dry-run"
        assert dry_payload["candidate_count"] == 2
        assert old_report.exists()
        assert old_evidence.exists()

        applied = run([
            sys.executable,
            str(SCRIPT),
            "--cleanup",
            "--apply-cleanup",
            "--cleanup-retention-days",
            "1",
            "--out-dir",
            str(out_dir),
            "--evidence-dir",
            str(ev_dir),
        ])
        assert applied.returncode == 0, applied.stderr
        applied_payload = json.loads(applied.stdout)
        assert applied_payload["mode"] == "apply"
        assert applied_payload["deleted_count"] == 2
        assert not old_report.exists()
        assert not old_evidence.exists()
        assert fresh_report.exists()
        assert protected.exists()


if __name__ == "__main__":
    test_cli_compress_and_recover()
    test_redact_mcp_token_in_url()
    test_stdin_mode()
    test_cleanup_retention_dry_run_and_apply()
    print("ok")
