"""auth_core.py — autenticação stdlib (sem dependências novas).

Senha: PBKDF2-HMAC-SHA256 (pbkdf2_sha256$iters$salt$hash).
Sessão: token assinado HMAC-SHA256 (body.b64 . sig.b64), com expiração — stateless,
validado pelo CONTENT_OS_SECRET. Não guarda sessão no banco.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time

from app.config import settings

_ITER = 200_000


class AuthConfigurationError(RuntimeError):
    """Raised when session signing is not configured securely."""


def hash_password(pw: str) -> str:
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt, _ITER)
    return f"pbkdf2_sha256${_ITER}${salt.hex()}${dk.hex()}"


def verify_password(pw: str, stored: str | None) -> bool:
    try:
        algo, iters, salt_hex, hash_hex = (stored or "").split("$")
        if algo != "pbkdf2_sha256":
            return False
        dk = hashlib.pbkdf2_hmac("sha256", pw.encode(), bytes.fromhex(salt_hex), int(iters))
        return hmac.compare_digest(dk.hex(), hash_hex)
    except Exception:
        return False


def _b64e(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).decode().rstrip("=")


def _b64d(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def _secret() -> bytes:
    value = settings.content_os_secret
    if not value or value != value.strip() or len(value) < 32:
        raise AuthConfigurationError(
            "CONTENT_OS_SECRET must contain at least 32 unambiguous characters"
        )
    return value.encode()


def make_token(user_id: str, tenant_id: str, email: str, ttl: int = 7 * 24 * 3600) -> str:
    payload = {"uid": user_id, "tid": tenant_id, "email": email, "exp": int(time.time()) + ttl}
    body = _b64e(json.dumps(payload, separators=(",", ":")).encode())
    sig = _b64e(hmac.new(_secret(), body.encode(), hashlib.sha256).digest())
    return f"{body}.{sig}"


def read_token(token: str | None) -> dict | None:
    try:
        body, sig = (token or "").split(".")
        expect = _b64e(hmac.new(_secret(), body.encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(sig, expect):
            return None
        payload = json.loads(_b64d(body))
        if int(payload.get("exp", 0)) < int(time.time()):
            return None
        return payload
    except Exception:
        return None
