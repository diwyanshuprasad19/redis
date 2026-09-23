"""Prometheus metrics for redis_app pool usage (optional dependency)."""

from __future__ import annotations

try:
    from prometheus_client import Counter, Histogram
except ImportError:  # pragma: no cover - optional extra
    REDIS_OPS = None  # type: ignore[assignment]
    REDIS_OP_SECONDS = None  # type: ignore[assignment]
    _ENABLED = False
else:
    try:
        REDIS_OPS = Counter(
            "redis_app_ops_total",
            "Redis client operations",
            ["op"],
        )
        REDIS_OP_SECONDS = Histogram(
            "redis_app_op_seconds",
            "Redis client operation latency",
            ["op"],
            buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0),
        )
    except Exception as exc:
        # Re-import in same process (pytest/CI): collectors already registered.
        if type(exc).__name__ not in {"ValueError", "DuplicateTimeseries"} and (
            "duplicat" not in str(exc).lower()
        ):
            raise
        from prometheus_client import REGISTRY

        names = getattr(REGISTRY, "_names_to_collectors", {})
        REDIS_OPS = names.get("redis_app_ops_total")  # type: ignore[assignment]
        REDIS_OP_SECONDS = names.get("redis_app_op_seconds")  # type: ignore[assignment]
        if REDIS_OPS is None or REDIS_OP_SECONDS is None:
            raise
    _ENABLED = True


def observe(op: str, seconds: float) -> None:
    if not _ENABLED or REDIS_OPS is None or REDIS_OP_SECONDS is None:
        return
    REDIS_OPS.labels(op=op).inc()
    REDIS_OP_SECONDS.labels(op=op).observe(seconds)
