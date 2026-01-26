from __future__ import annotations

import asyncio
import os
import sys

import httpx
from a2a.client.auth.credentials import InMemoryContextCredentialStore
from a2a.client.auth.interceptor import AuthInterceptor
from a2a.client.client_factory import ClientConfig
from a2a.client.errors import A2AClientHTTPError
from a2a.client.middleware import ClientCallContext
from a2a.types import TaskQueryParams, TransportProtocol

from opencode_a2a.a2a_client import connect_with_patched_rest


async def main() -> int:
    base_url = os.environ.get("A2A_URL", "http://127.0.0.1:8000")
    token = os.environ.get("A2A_BEARER_TOKEN")
    if not token:
        print("A2A_BEARER_TOKEN must be set for this test", file=sys.stderr)
        return 2

    store = InMemoryContextCredentialStore()
    session_id = "auth-test"
    await store.set_credentials(session_id, "bearerAuth", token)

    context = ClientCallContext(state={"sessionId": session_id})
    interceptors = [AuthInterceptor(store)]

    config = ClientConfig(
        supported_transports=[TransportProtocol.http_json],
        httpx_client=httpx.AsyncClient(timeout=10.0),
        streaming=False,
    )

    client = await connect_with_patched_rest(
        base_url,
        client_config=config,
        interceptors=interceptors,
    )

    try:
        await client.get_task(TaskQueryParams(id="task-does-not-exist"), context=context)
        print("AuthInterceptor test: unexpected success")
        return 1
    except A2AClientHTTPError as exc:
        if "401" in str(exc):
            print("AuthInterceptor test: failed (401 Unauthorized)")
            return 1
        if "404" in str(exc):
            print("AuthInterceptor test: success (received 404 after auth)")
            return 0
        print(f"AuthInterceptor test: failed ({exc})")
        return 1
    finally:
        await config.httpx_client.aclose()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
