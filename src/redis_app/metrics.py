"""Prometheus metrics for redis_app pool usage."""

from __future__ import annotations

from prometheus_client import Counter, Histogram

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


def observe(op: str, seconds: float) -> None:
    REDIS_OPS.labels(op=op).inc()
    REDIS_OP_SECONDS.labels(op=op).observe(seconds)
