import httpx
import pytest

from opencode_a2a_serve.opencode_client import OpencodeClient
from tests.helpers import make_settings


class _DummyResponse:
    def __init__(self, payload=None) -> None:
        self._payload = {"ok": True} if payload is None else payload

    def raise_for_status(self) -> None:
        return None

    def json(self):
        return self._payload


@pytest.mark.asyncio
async def test_merge_params_does_not_allow_directory_override(monkeypatch):
    client = OpencodeClient(
        make_settings(
            a2a_bearer_token="t-1",
            opencode_directory="/safe",
            opencode_timeout=1.0,
            a2a_log_level="DEBUG",
            a2a_log_payloads=False,
        )
    )

    seen = {}

    async def fake_get(path: str, *, params=None, **_kwargs):
        seen["path"] = path
        seen["params"] = params
        return _DummyResponse()

    monkeypatch.setattr(client._client, "get", fake_get)

    await client.list_sessions(params={"directory": "/evil", "page": 1})
    assert seen["path"] == "/session"
    assert seen["params"]["directory"] == "/safe"
    assert seen["params"]["page"] == "1"

    await client.list_messages("sess-1", params={"directory": "/evil", "size": 10})
    assert seen["path"] == "/session/sess-1/message"
    assert seen["params"]["directory"] == "/safe"
    assert seen["params"]["size"] == "10"

    await client.close()


@pytest.mark.asyncio
async def test_permission_reply_falls_back_to_legacy_endpoint_on_404(monkeypatch):
    client = OpencodeClient(
        make_settings(
            a2a_bearer_token="t-1",
            opencode_directory="/safe",
            opencode_timeout=1.0,
            a2a_log_level="DEBUG",
            a2a_log_payloads=False,
        )
    )

    calls: list[tuple[str, dict | None]] = []

    async def fake_post(path: str, *, params=None, json=None, **_kwargs):
        calls.append((path, json))
        if path.startswith("/permission/"):
            request = httpx.Request("POST", f"http://opencode{path}")
            response = httpx.Response(404, request=request)
            raise httpx.HTTPStatusError("Not Found", request=request, response=response)
        return _DummyResponse(True)

    monkeypatch.setattr(client._client, "post", fake_post)

    ok = await client.permission_reply(
        "perm-1",
        reply="once",
        session_id="sess-1",
    )
    assert ok is True
    assert calls[0][0] == "/permission/perm-1/reply"
    assert calls[0][1] == {"reply": "once"}
    assert calls[1][0] == "/session/sess-1/permissions/perm-1"
    assert calls[1][1] == {"response": "once"}

    await client.close()


@pytest.mark.asyncio
async def test_question_reply_posts_answers(monkeypatch):
    client = OpencodeClient(
        make_settings(
            a2a_bearer_token="t-1",
            opencode_timeout=1.0,
            a2a_log_level="DEBUG",
            a2a_log_payloads=False,
        )
    )

    seen = {}

    async def fake_post(path: str, *, params=None, json=None, **_kwargs):
        seen["path"] = path
        seen["params"] = params
        seen["json"] = json
        return _DummyResponse(True)

    monkeypatch.setattr(client._client, "post", fake_post)

    ok = await client.question_reply("q-1", answers=[["A"], ["B"]])
    assert ok is True
    assert seen["path"] == "/question/q-1/reply"
    assert seen["json"] == {"answers": [["A"], ["B"]]}

    await client.close()
