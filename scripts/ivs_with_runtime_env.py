#!/usr/bin/env python3
"""Run a command with IVS runtime credentials loaded safely.

Loads KEY=VALUE pairs from protected local env files without printing secrets.
This intentionally keeps secret values out of skills, prompts, memory and git.
"""
from __future__ import annotations

import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

ENV_FILES = [
    Path(os.environ.get("IVS_RUNTIME_ENV_FILE", "/root/.hermes/shared/ivs-runtime.env")),
    Path(os.environ.get("IVS_OPENCLAW_ENV_FILE", "/root/.openclaw/.env.runtime")),
]
KEY_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)=(.*)$")


def parse_value(raw: str) -> str:
    raw = raw.strip()
    if not raw:
        return ""
    try:
        parts = shlex.split(raw, posix=True)
        if len(parts) == 1:
            return parts[0]
    except Exception:
        pass
    return raw.strip().strip('"').strip("'")


def load_env() -> dict[str, str]:
    env = dict(os.environ)
    for path in ENV_FILES:
        if not path.exists():
            continue
        for line in path.read_text(errors="ignore").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            m = KEY_RE.match(line)
            if not m:
                continue
            key, raw = m.groups()
            env[key] = parse_value(raw)
    return env


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: ivs-with-runtime-env <command> [args...]", file=sys.stderr)
        return 2
    env = load_env()
    proc = subprocess.run(sys.argv[1:], env=env)
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
