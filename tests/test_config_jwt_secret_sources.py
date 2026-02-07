import base64

import pytest

from opencode_a2a.config import Settings


def test_settings_from_env_prefers_jwt_secret_b64(monkeypatch: pytest.MonkeyPatch):
    for key in (
        "A2A_JWT_SECRET_B64",
        "A2A_JWT_SECRET_FILE",
        "A2A_JWT_SECRET",
        "A2A_JWT_ALGORITHM",
        "A2A_JWT_ISSUER",
        "A2A_JWT_AUDIENCE",
    ):
        monkeypatch.delenv(key, raising=False)

    raw = "public-key-pem\nline2\n"
    monkeypatch.setenv("A2A_JWT_SECRET_B64", base64.b64encode(raw.encode("utf-8")).decode("ascii"))
    monkeypatch.setenv("A2A_JWT_SECRET", "should-not-be-used")

    # Provide minimal required env for Settings.from_env defaults to work.
    monkeypatch.setenv("A2A_JWT_ISSUER", "issuer")
    monkeypatch.setenv("A2A_JWT_AUDIENCE", "audience")

    settings = Settings.from_env()
    assert settings.a2a_jwt_secret == raw
