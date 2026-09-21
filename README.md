# Redis project — pooled client + pipeline batching for large-scale access

Python + Redis (`localhost:6380` via platform-ops data-stack).

## Local-first (required before PR)

```bash
cd ../platform-ops
make local-gate REPO=redis      # must be GREEN
make anti-slop REPO=redis       # aislop ≥ 80
make auto REPO=redis TITLE="…"  # push + PR only if green
```

## Client (scale)

```bash
pip install -e ".[dev]"
pytest tests/ -q
python scripts/load_pipeline_dry.py --dry-run --keys 10000
# live (after make data-up):
REDIS_URL=redis://localhost:6380/0 python scripts/load_pipeline_dry.py --keys 5000
```

- `RedisClient` — shared `ConnectionPool` with `REDIS_MAX_CONNECTIONS` (default 50)
- `mget_via_pipeline` / `msetex_via_pipeline` — one RTT per batch

## Local data (from platform-ops)

```bash
cd ../platform-ops
make data-up
# Redis: localhost:6380
# Postgres redis_app: localhost:5433  user/pass app/app
```

## Observability

Shared stack in `platform-ops` — see `../platform-ops/OBSERVABILITY.md`.

```bash
cd ../platform-ops
make obs-up
```

## PR automation

```bash
cd ../platform-ops
make auto REPO=redis TITLE="feat: …"
```

PR review (Actions): **git diff / PR files** via reviewdog (`filter-mode=added`) + PR-Agent — not whole-repo AI review.
