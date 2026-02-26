import time

import httpx
import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from tests.helpers import make_settings


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


def _make_jwt(private_key_pem: str, **overrides) -> str:
    payload = {
        "iss": "test-issuer",
        "aud": "test-audience",
        "exp": int(time.time()) + 300,
        "sub": "user-1",
    }
    payload.update(overrides)
    return jwt.encode(payload, private_key_pem, algorithm="RS256")


@pytest.mark.asyncio
async def test_auth_bearer_mode_accepts_valid_token():
    import opencode_a2a_serve.app as app_module

    app = app_module.create_app(make_settings(a2a_bearer_token="token-1"))
    transport = httpx.ASGITransport(app=app)
    headers = {"Authorization": "Bearer token-1"}

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health", headers=headers)
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_auth_jwt_mode_accepts_valid_token():
    import opencode_a2a_serve.app as app_module

    private_key_pem, public_key_pem = _make_rsa_keypair()
    app = app_module.create_app(
        make_settings(
            a2a_auth_mode="jwt",
            a2a_bearer_token=None,
            a2a_jwt_secret=public_key_pem,
            a2a_jwt_algorithm="RS256",
            a2a_jwt_issuer="test-issuer",
            a2a_jwt_audience="test-audience",
        )
    )
    transport = httpx.ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {_make_jwt(private_key_pem)}"}

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health", headers=headers)
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_auth_jwt_mode_rejects_missing_required_scope():
    import opencode_a2a_serve.app as app_module

    private_key_pem, public_key_pem = _make_rsa_keypair()
    app = app_module.create_app(
        make_settings(
            a2a_auth_mode="jwt",
            a2a_bearer_token=None,
            a2a_jwt_secret=public_key_pem,
            a2a_jwt_algorithm="RS256",
            a2a_jwt_issuer="test-issuer",
            a2a_jwt_audience="test-audience",
            a2a_required_scopes={"opencode"},
            a2a_jwt_scope_match="any",
        )
    )
    transport = httpx.ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {_make_jwt(private_key_pem, scope='other')}"}

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health", headers=headers)
        assert resp.status_code == 403


@pytest.mark.asyncio
async def test_auth_jwt_mode_rejects_token_missing_exp():
    import opencode_a2a_serve.app as app_module

    private_key_pem, public_key_pem = _make_rsa_keypair()
    app = app_module.create_app(
        make_settings(
            a2a_auth_mode="jwt",
            a2a_bearer_token=None,
            a2a_jwt_secret=public_key_pem,
            a2a_jwt_algorithm="RS256",
            a2a_jwt_issuer="test-issuer",
            a2a_jwt_audience="test-audience",
        )
    )
    token = jwt.encode(
        {
            "iss": "test-issuer",
            "aud": "test-audience",
            "sub": "user-1",
        },
        private_key_pem,
        algorithm="RS256",
    )
    transport = httpx.ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health", headers=headers)
        assert resp.status_code == 401
