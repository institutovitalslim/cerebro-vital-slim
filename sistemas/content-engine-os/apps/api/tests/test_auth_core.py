import time

import pytest

from app.auth_core import AuthConfigurationError, make_token, read_token
from app.config import settings


def test_missing_secret_cannot_create_or_validate_sessions(monkeypatch) -> None:
    monkeypatch.setattr(settings, "content_os_secret", None)

    with pytest.raises(AuthConfigurationError):
        make_token("user", "tenant", "user@example.com")
    assert read_token("forged.token") is None


@pytest.mark.parametrize("secret", ["", " " * 32, "short-secret"])
def test_weak_or_ambiguous_secret_fails_closed(monkeypatch, secret: str) -> None:
    monkeypatch.setattr(settings, "content_os_secret", secret)
    with pytest.raises(AuthConfigurationError):
        make_token("user", "tenant", "user@example.com")


def test_valid_secret_round_trips_tenant_identity(monkeypatch) -> None:
    monkeypatch.setattr(settings, "content_os_secret", "x" * 32)
    token = make_token("user", "tenant-123", "user@example.com", ttl=60)
    payload = read_token(token)
    assert payload is not None
    assert payload["tid"] == "tenant-123"
    assert payload["exp"] > int(time.time())
