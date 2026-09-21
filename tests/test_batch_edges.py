"""Extra edge tests for redis_app batch helpers."""

from __future__ import annotations

import fakeredis
import pytest

from redis_app.batch import mget_via_pipeline, msetex_via_pipeline
from redis_app.client import RedisClient
from redis_app.settings import RedisSettings


@pytest.fixture
def client() -> RedisClient:
    raw = fakeredis.FakeRedis(decode_responses=True)
    return RedisClient(settings=RedisSettings(), client=raw)


def test_mget_empty_keys(client: RedisClient) -> None:
    assert mget_via_pipeline(client, []) == {}


def test_msetex_empty_items(client: RedisClient) -> None:
    assert msetex_via_pipeline(client, {}, ttl_seconds=10) == 0


def test_mget_all_missing(client: RedisClient) -> None:
    assert mget_via_pipeline(client, ["nope", "also-nope"]) == {}
