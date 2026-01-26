from __future__ import annotations

from typing import Any

import httpx
from a2a.client.client_factory import ClientConfig, ClientFactory, TransportProducer
from a2a.client.middleware import ClientCallContext, ClientCallInterceptor
from a2a.client.transports.rest import RestTransport
from a2a.types import AgentCard, TransportProtocol


class PatchedRestTransport(RestTransport):
    """REST transport that applies client interceptors (auth headers, etc.)."""

    async def _apply_interceptors(
        self,
        request_payload: dict[str, Any],
        http_kwargs: dict[str, Any] | None,
        context: ClientCallContext | None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        final_http_kwargs = http_kwargs or {}
        final_request_payload = request_payload
        for interceptor in self.interceptors:
            (
                final_request_payload,
                final_http_kwargs,
            ) = await interceptor.intercept(
                "rest",
                final_request_payload,
                final_http_kwargs,
                self.agent_card,
                context,
            )
        return final_request_payload, final_http_kwargs


def patched_rest_transport(
    card: AgentCard,
    url: str,
    config: ClientConfig,
    interceptors: list[ClientCallInterceptor],
) -> RestTransport:
    return PatchedRestTransport(
        config.httpx_client or httpx.AsyncClient(),
        card,
        url,
        interceptors,
        config.extensions or None,
    )


def patch_rest_transports(
    extra_transports: dict[str, TransportProducer] | None = None,
) -> dict[str, TransportProducer]:
    overrides = {TransportProtocol.http_json: patched_rest_transport}
    if extra_transports:
        overrides.update(extra_transports)
    return overrides


def connect_with_patched_rest(
    agent: str | AgentCard,
    client_config: ClientConfig | None = None,
    consumers: list[Any] | None = None,
    interceptors: list[ClientCallInterceptor] | None = None,
    relative_card_path: str | None = None,
    resolver_http_kwargs: dict[str, Any] | None = None,
    extra_transports: dict[str, TransportProducer] | None = None,
    extensions: list[str] | None = None,
):
    return ClientFactory.connect(
        agent,
        client_config=client_config,
        consumers=consumers,
        interceptors=interceptors,
        relative_card_path=relative_card_path,
        resolver_http_kwargs=resolver_http_kwargs,
        extra_transports=patch_rest_transports(extra_transports),
        extensions=extensions,
    )
