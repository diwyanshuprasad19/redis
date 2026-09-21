"""Redis connection settings for large-scale local/prod use."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class RedisSettings:
    """Pool-oriented Redis settings (env-overridable)."""

    url: str = "redis://localhost:6380/0"
    max_connections: int = 50
    socket_connect_timeout: float = 1.0
    socket_timeout: float = 1.0
    health_check_interval: int = 30
    decode_responses: bool = True

    @classmethod
    def from_env(cls) -> RedisSettings:
        return cls(
            url=os.getenv("REDIS_URL", cls.url),
            max_connections=int(os.getenv("REDIS_MAX_CONNECTIONS", str(cls.max_connections))),
            socket_connect_timeout=float(
                os.getenv("REDIS_SOCKET_CONNECT_TIMEOUT", str(cls.socket_connect_timeout))
            ),
            socket_timeout=float(os.getenv("REDIS_SOCKET_TIMEOUT", str(cls.socket_timeout))),
            health_check_interval=int(
                os.getenv("REDIS_HEALTH_CHECK_INTERVAL", str(cls.health_check_interval))
            ),
            decode_responses=os.getenv("REDIS_DECODE_RESPONSES", "true").lower()
            in {"1", "true", "yes"},
        )
