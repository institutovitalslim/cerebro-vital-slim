#!/usr/bin/env python3
"""Sanitized gog access check for IVS agents.

Does not print secrets. Intended for Maria to validate that a profile/runtime can use gog.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys


def main() -> int:
    result = {
        "ok": False,
        "gog_binary": False,
        "gog_keyring_password_env": bool(os.environ.get("GOG_KEYRING_PASSWORD")),
        "gog_account_env": bool(os.environ.get("GOG_ACCOUNT")),
        "auth_status_ok": False,
        "account_email": None,
        "credentials_exists": None,
        "error": None,
    }
    try:
        subprocess.run(["gog", "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
        result["gog_binary"] = True
    except Exception as exc:
        result["error"] = f"gog_binary_failed: {type(exc).__name__}"
        print(json.dumps(result, ensure_ascii=False))
        return 1

    try:
        proc = subprocess.run(["gog", "auth", "status", "--json"], check=False, text=True, capture_output=True, timeout=30)
        if proc.returncode != 0:
            result["error"] = "auth_status_failed"
            print(json.dumps(result, ensure_ascii=False))
            return 2
        data = json.loads(proc.stdout or "{}")
        acc = data.get("account") or {}
        result["auth_status_ok"] = True
        result["account_email"] = acc.get("email")
        result["credentials_exists"] = bool(acc.get("credentials_exists"))
        result["ok"] = bool(result["gog_keyring_password_env"] and result["credentials_exists"])
    except Exception as exc:
        result["error"] = f"auth_status_exception: {type(exc).__name__}"
        print(json.dumps(result, ensure_ascii=False))
        return 3
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["ok"] else 4


if __name__ == "__main__":
    raise SystemExit(main())
