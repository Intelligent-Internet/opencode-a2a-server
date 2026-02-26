import os
from unittest import mock

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from pydantic import ValidationError

from opencode_a2a_serve.config import Settings


def _make_rsa_keypair() -> tuple[str, str]:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")
    public_key_pem = (
        private_key.public_key()
        .public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        .decode("utf-8")
    )
    return private_key_pem, public_key_pem


def test_settings_missing_required():
    with mock.patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValidationError) as excinfo:
            Settings.from_env()
        assert "A2A_BEARER_TOKEN is required when A2A_AUTH_MODE=bearer" in str(excinfo.value)


def test_settings_valid():
    env = {
        "A2A_BEARER_TOKEN": "test-token",
        "OPENCODE_TIMEOUT": "300",
        "A2A_CANCEL_ABORT_TIMEOUT_SECONDS": "0.75",
        "A2A_ENABLE_SESSION_SHELL": "true",
    }
    with mock.patch.dict(os.environ, env, clear=True):
        settings = Settings.from_env()
        assert settings.a2a_bearer_token == "test-token"
        assert settings.opencode_timeout == 300.0
        assert settings.a2a_cancel_abort_timeout_seconds == 0.75
        assert settings.a2a_enable_session_shell is True


def test_settings_jwt_mode_valid_without_bearer_token():
    _, public_key_pem = _make_rsa_keypair()
    env = {
        "A2A_AUTH_MODE": "jwt",
        "A2A_JWT_SECRET": public_key_pem,
        "A2A_JWT_ALGORITHM": "RS256",
        "A2A_JWT_ISSUER": "issuer",
        "A2A_JWT_AUDIENCE": "audience",
    }
    with mock.patch.dict(os.environ, env, clear=True):
        settings = Settings.from_env()
        assert settings.a2a_auth_mode == "jwt"
        assert settings.a2a_bearer_token is None
        assert settings.a2a_jwt_secret == public_key_pem


def test_settings_jwt_mode_secret_file_not_readable():
    env = {
        "A2A_AUTH_MODE": "jwt",
        "A2A_JWT_SECRET_FILE": "/tmp/non-existent-jwt-secret-file",
        "A2A_JWT_ALGORITHM": "RS256",
        "A2A_JWT_ISSUER": "issuer",
        "A2A_JWT_AUDIENCE": "audience",
    }
    with mock.patch.dict(os.environ, env, clear=True):
        with pytest.raises(ValidationError) as excinfo:
            Settings.from_env()
        assert "A2A_JWT_SECRET_FILE is not readable" in str(excinfo.value)


def test_settings_jwt_mode_rejects_symmetric_algorithm():
    _, public_key_pem = _make_rsa_keypair()
    env = {
        "A2A_AUTH_MODE": "jwt",
        "A2A_JWT_SECRET": public_key_pem,
        "A2A_JWT_ALGORITHM": "HS256",
        "A2A_JWT_ISSUER": "issuer",
        "A2A_JWT_AUDIENCE": "audience",
    }
    with mock.patch.dict(os.environ, env, clear=True):
        with pytest.raises(ValidationError) as excinfo:
            Settings.from_env()
        assert "A2A_JWT_ALGORITHM must be one of" in str(excinfo.value)


def test_settings_jwt_mode_rejects_private_key():
    private_key_pem, _ = _make_rsa_keypair()
    env = {
        "A2A_AUTH_MODE": "jwt",
        "A2A_JWT_SECRET": private_key_pem,
        "A2A_JWT_ALGORITHM": "RS256",
        "A2A_JWT_ISSUER": "issuer",
        "A2A_JWT_AUDIENCE": "audience",
    }
    with mock.patch.dict(os.environ, env, clear=True):
        with pytest.raises(ValidationError) as excinfo:
            Settings.from_env()
        assert "A2A_JWT_SECRET must be a public verification key" in str(excinfo.value)


def test_settings_bearer_mode_ignores_invalid_jwt_fields():
    env = {
        "A2A_AUTH_MODE": "bearer",
        "A2A_BEARER_TOKEN": "test-token",
        "A2A_JWT_SECRET_B64": "@@@",  # pragma: allowlist secret
        "A2A_JWT_SCOPE_MATCH": "invalid",
    }
    with mock.patch.dict(os.environ, env, clear=True):
        settings = Settings.from_env()
        assert settings.a2a_auth_mode == "bearer"
        assert settings.a2a_bearer_token == "test-token"


def test_parse_oauth_scopes():
    env = {
        "A2A_BEARER_TOKEN": "test",
        "A2A_OAUTH_SCOPES": "scope1, scope2,,scope3 ",
    }
    with mock.patch.dict(os.environ, env, clear=True):
        settings = Settings.from_env()
        assert settings.a2a_oauth_scopes == {"scope1": "", "scope2": "", "scope3": ""}
