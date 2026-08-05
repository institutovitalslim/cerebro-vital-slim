"""Trusted ownership context for standalone and Content Engine OS requests."""

from __future__ import annotations

import hashlib
import hmac
import os
import time
from dataclasses import dataclass
from typing import Literal

from fastapi import Request

STANDALONE_ID = "standalone"
_MAX_CLOCK_SKEW_SECONDS = 300
_MAX_ID_LENGTH = 128


@dataclass(frozen=True, slots=True)
class OwnershipContext:
    tenant_id: str = STANDALONE_ID
    user_id: str = STANDALONE_ID
    mode: Literal["standalone", "integration"] = "standalone"

    @property
    def is_standalone(self) -> bool:
        return self.mode == "standalone"


def _valid_identifier(value: str | None) -> bool:
    return bool(
        value
        and len(value) <= _MAX_ID_LENGTH
        and value.strip() == value
        and all(character.isprintable() and character not in "\r\n" for character in value)
    )


def _signature_message(
    *,
    tenant_id: str,
    user_id: str,
    timestamp: str,
    method: str,
    path: str,
    query: str,
    body: bytes,
) -> bytes:
    body_digest = hashlib.sha256(body).hexdigest()
    return (
        f"{tenant_id}\n{user_id}\n{timestamp}\n{method.upper()}\n{path}\n{query}\n{body_digest}"
    ).encode()


async def resolve_ownership(request: Request) -> OwnershipContext | None:
    """Authenticate the complete internal request or return local ownership.

    The HMAC binds tenant, user, timestamp, method, canonical path, raw query and
    SHA-256 of the exact body. Integrated callers may not use the reserved
    ``standalone`` identifier.
    """

    secret = os.environ.get("HOOK_INTEGRATION_SECRET", "")
    if not secret:
        return OwnershipContext()

    tenant_id = request.headers.get("x-content-os-tenant")
    user_id = request.headers.get("x-content-os-user")
    timestamp = request.headers.get("x-content-os-timestamp")
    signature = request.headers.get("x-content-os-signature")
    if not _valid_identifier(tenant_id) or not _valid_identifier(user_id):
        return None
    assert tenant_id is not None and user_id is not None
    if tenant_id == STANDALONE_ID or user_id == STANDALONE_ID:
        return None
    if timestamp is None or signature is None or not timestamp.isascii() or not timestamp.isdigit():
        return None
    try:
        issued_at = int(timestamp)
    except ValueError:
        return None
    if abs(int(time.time()) - issued_at) > _MAX_CLOCK_SKEW_SECONDS:
        return None

    expected = hmac.new(
        secret.encode(),
        _signature_message(
            tenant_id=tenant_id,
            user_id=user_id,
            timestamp=timestamp,
            method=request.method,
            path=request.url.path,
            query=request.url.query,
            body=await request.body(),
        ),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(expected, signature.lower()):
        return None
    return OwnershipContext(
        tenant_id=tenant_id,
        user_id=user_id,
        mode="integration",
    )


def request_ownership(request: Request) -> OwnershipContext:
    """Return ownership installed by the authentication middleware."""

    context = getattr(request.state, "hook_ownership", None)
    if not isinstance(context, OwnershipContext):
        raise TypeError("request ownership context is unavailable")
    return context


def repository_call(request: Request, method: str, *args: object, **kwargs: object) -> object:
    """Call repositories compatibly locally, requiring ownership-aware integration storage."""

    repository = request.app.state.services.get().repository
    operation = getattr(repository, method)
    context = request_ownership(request)
    if context.is_standalone:
        return operation(*args, **kwargs)
    return operation(
        *args,
        **kwargs,
        tenant_id=context.tenant_id,
        user_id=context.user_id,
    )
