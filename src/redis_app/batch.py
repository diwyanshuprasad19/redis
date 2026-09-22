"""Pipeline batch helpers — one RTT for many keys (large-scale cache reads/writes)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from redis_app.client import RedisClient


def mget_via_pipeline(client: RedisClient, keys: list[str]) -> dict[str, Any]:
    """Fetch many keys in one pipeline round-trip. Missing keys are omitted."""
    if not keys:
        return {}
    pipe = client.raw.pipeline(transaction=False)
    for key in keys:
        pipe.get(key)
    values = pipe.execute()
    out: dict[str, Any] = {}
    for key, value in zip(keys, values, strict=True):
        if value is not None:
            out[key] = value
    return out


def msetex_via_pipeline(
    client: RedisClient,
    items: Mapping[str, str],
    *,
    ttl_seconds: int,
) -> int:
    """SETEX many keys in one pipeline. Returns number of keys written."""
    if not items:
        return 0
    if ttl_seconds <= 0:
        raise ValueError("ttl_seconds must be > 0")
    pipe = client.raw.pipeline(transaction=True)
    for key, value in items.items():
        pipe.setex(key, ttl_seconds, value)
    results = pipe.execute()
    return sum(1 for ok in results if ok)
