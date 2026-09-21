"""Unit tests for pooled Redis client + pipeline batching (fakeredis)."""

from __future__ import annotations

import fakeredis
import pytest

from redis_app.batch import mget_via_pipeline, msetex_via_pipeline
from redis_app.client import RedisClient
from redis_app.settings import RedisSettings


@pytest.fixture
def fake_client() -> RedisClient:
    server = fakeredis.FakeServer()
    raw = fakeredis.FakeRedis(server=server, decode_responses=True)
    settings = RedisSettings(url="redis://fake/0", max_connections=10)
    return RedisClient(settings=settings, client=raw)


def test_ping(fake_client: RedisClient) -> None:
    assert fake_client.ping() is True


def test_setex_get_delete(fake_client: RedisClient) -> None:
    assert fake_client.setex("k1", 60, "v1") is True
    assert fake_client.get("k1") == "v1"
    assert fake_client.delete("k1") == 1
    assert fake_client.get("k1") is None


def test_pipeline_msetex_mget(fake_client: RedisClient) -> None:
    n = msetex_via_pipeline(
        fake_client,
        {f"agg:{i}": f"payload-{i}" for i in range(100)},
        ttl_seconds=30,
    )
    assert n == 100
    got = mget_via_pipeline(fake_client, [f"agg:{i}" for i in range(100)])
    assert len(got) == 100
    assert got["agg:42"] == "payload-42"


def test_pipeline_skips_missing_keys(fake_client: RedisClient) -> None:
    fake_client.setex("only", 10, "yes")
    got = mget_via_pipeline(fake_client, ["only", "missing"])
    assert got == {"only": "yes"}


def test_msetex_rejects_bad_ttl(fake_client: RedisClient) -> None:
    with pytest.raises(ValueError):
        msetex_via_pipeline(fake_client, {"a": "b"}, ttl_seconds=0)


def test_pool_max_connections_from_settings() -> None:
    settings = RedisSettings(url="redis://localhost:6380/0", max_connections=25)
    # Injected client still reports settings.max_connections
    raw = fakeredis.FakeRedis(decode_responses=True)
    client = RedisClient(settings=settings, client=raw)
    assert client.max_connections == 25


def test_settings_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("REDIS_URL", "redis://example:6379/2")
    monkeypatch.setenv("REDIS_MAX_CONNECTIONS", "80")
    s = RedisSettings.from_env()
    assert s.url == "redis://example:6379/2"
    assert s.max_connections == 80
