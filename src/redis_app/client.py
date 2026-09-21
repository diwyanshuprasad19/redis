"""Bounded connection pool Redis client for concurrent large-scale access.

Avoids connection storms from naive redis.from_url() under many workers by
sharing one ConnectionPool with a hard max_connections cap.
"""

from __future__ import annotations

import time
from typing import Any

import redis
from redis.connection import ConnectionPool

from redis_app import metrics
from redis_app.settings import RedisSettings


class RedisClient:
    """Thin wrapper around redis.Redis backed by a shared ConnectionPool."""

    def __init__(
        self,
        settings: RedisSettings | None = None,
        *,
        client: redis.Redis | None = None,
    ) -> None:
        self.settings = settings or RedisSettings.from_env()
        self._owns_pool = client is None
        if client is not None:
            self._client = client
            self._pool: ConnectionPool | None = None
            return

        self._pool = ConnectionPool.from_url(
            self.settings.url,
            max_connections=self.settings.max_connections,
            socket_connect_timeout=self.settings.socket_connect_timeout,
            socket_timeout=self.settings.socket_timeout,
            health_check_interval=self.settings.health_check_interval,
            decode_responses=self.settings.decode_responses,
        )
        self._client = redis.Redis(connection_pool=self._pool)

    @property
    def raw(self) -> redis.Redis:
        return self._client

    @property
    def max_connections(self) -> int:
        if self._pool is None:
            return self.settings.max_connections
        return int(getattr(self._pool, "max_connections", self.settings.max_connections))

    def ping(self) -> bool:
        t0 = time.perf_counter()
        try:
            return bool(self._client.ping())
        finally:
            metrics.observe("ping", time.perf_counter() - t0)

    def get(self, key: str) -> Any:
        t0 = time.perf_counter()
        try:
            return self._client.get(key)
        finally:
            metrics.observe("get", time.perf_counter() - t0)

    def setex(self, key: str, ttl_seconds: int, value: str) -> bool:
        t0 = time.perf_counter()
        try:
            return bool(self._client.setex(key, ttl_seconds, value))
        finally:
            metrics.observe("setex", time.perf_counter() - t0)

    def delete(self, *keys: str) -> int:
        if not keys:
            return 0
        t0 = time.perf_counter()
        try:
            return int(self._client.delete(*keys))
        finally:
            metrics.observe("delete", time.perf_counter() - t0)

    def close(self) -> None:
        if self._owns_pool and self._pool is not None:
            self._pool.disconnect()
