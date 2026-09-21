"""redis_app — pooled Redis client + pipeline batching for large-scale access."""

from redis_app.batch import mget_via_pipeline, msetex_via_pipeline
from redis_app.client import RedisClient
from redis_app.settings import RedisSettings

__all__ = [
    "RedisClient",
    "RedisSettings",
    "mget_via_pipeline",
    "msetex_via_pipeline",
]
