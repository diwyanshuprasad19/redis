"""Cover redis_app metrics optional path + pool construction / close / delete edges."""

from __future__ import annotations

import importlib
import sys
from types import ModuleType
from unittest.mock import MagicMock, patch

import fakeredis
import pytest

from redis_app.client import RedisClient
from redis_app.settings import RedisSettings


def _install_fake_prometheus() -> ModuleType:
    """Minimal prometheus_client stand-in so the enabled import branch runs."""
    mod = ModuleType("prometheus_client")

    class _Child:
        def inc(self, *a, **k):
            return None

        def observe(self, *a, **k):
            return None

    class _Metric:
        def __init__(self, *a, **k):
            pass

        def labels(self, **k):
            return _Child()

    mod.Counter = _Metric  # type: ignore[attr-defined]
    mod.Histogram = _Metric  # type: ignore[attr-defined]
    sys.modules["prometheus_client"] = mod
    return mod


def test_metrics_enabled_import_and_observe() -> None:
    """Cover Counter/Histogram import success path (optional dependency present)."""
    real = sys.modules.get("prometheus_client")
    try:
        _install_fake_prometheus()
        if "redis_app.metrics" in sys.modules:
            del sys.modules["redis_app.metrics"]
        mod = importlib.import_module("redis_app.metrics")
        assert mod._ENABLED is True
        mod.observe("ping", 0.001)
        mod.observe("get", 0.002)
    finally:
        if "redis_app.metrics" in sys.modules:
            del sys.modules["redis_app.metrics"]
        if real is not None:
            sys.modules["prometheus_client"] = real
        else:
            sys.modules.pop("prometheus_client", None)
        importlib.import_module("redis_app.metrics")


def test_metrics_import_without_prometheus() -> None:
    """prometheus_client ImportError → _ENABLED False and observe no-op."""
    real = sys.modules.get("prometheus_client")
    try:
        if "redis_app.metrics" in sys.modules:
            del sys.modules["redis_app.metrics"]

        import builtins

        real_import = builtins.__import__

        def _import(name, *args, **kwargs):
            if name == "prometheus_client" or name.startswith("prometheus_client."):
                raise ImportError("simulated missing prometheus_client")
            return real_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=_import):
            mod = importlib.import_module("redis_app.metrics")
            assert mod._ENABLED is False
            mod.observe("x", 1.0)
    finally:
        if "redis_app.metrics" in sys.modules:
            del sys.modules["redis_app.metrics"]
        if real is not None:
            sys.modules["prometheus_client"] = real
        else:
            sys.modules.pop("prometheus_client", None)
        importlib.import_module("redis_app.metrics")


def test_observe_disabled_branch(monkeypatch: pytest.MonkeyPatch) -> None:
    import redis_app.metrics as metrics_mod

    monkeypatch.setattr(metrics_mod, "_ENABLED", False)
    monkeypatch.setattr(metrics_mod, "REDIS_OPS", None)
    monkeypatch.setattr(metrics_mod, "REDIS_OP_SECONDS", None)
    metrics_mod.observe("noop", 0.01)


def test_client_builds_pool_and_close() -> None:
    settings = RedisSettings(url="redis://localhost:6379/0", max_connections=3)
    pool = MagicMock()
    pool.max_connections = 3
    fake_redis = fakeredis.FakeRedis(decode_responses=True)

    with (
        patch("redis_app.client.ConnectionPool.from_url", return_value=pool) as from_url,
        patch("redis_app.client.redis.Redis", return_value=fake_redis),
    ):
        client = RedisClient(settings=settings)
        assert from_url.called
        assert client.max_connections == 3
        assert client.ping() is True
        client.close()
        pool.disconnect.assert_called_once()


def test_delete_empty_and_injected_max_connections() -> None:
    raw = fakeredis.FakeRedis(decode_responses=True)
    client = RedisClient(settings=RedisSettings(max_connections=11), client=raw)
    assert client.delete() == 0
    assert client.max_connections == 11
    client.close()
