from __future__ import annotations

from typing import Any

from opencode_a2a_serve.config import Settings


def make_settings(**overrides: Any) -> Settings:
    base: dict[str, Any] = {
        "opencode_base_url": "http://127.0.0.1:4096",
        "a2a_bearer_token": "test-token",
    }
    base.update(overrides)
    return Settings(**base)


class DummyEventQueue:
    def __init__(self) -> None:
        self.events: list[Any] = []

    async def enqueue_event(self, event: Any) -> None:
        self.events.append(event)

    async def close(self) -> None:
        return None
