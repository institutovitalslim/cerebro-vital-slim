#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
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


if __name__ == "__main__":
    test_cli_compress_and_recover()
    test_redact_mcp_token_in_url()
    print("ok")
