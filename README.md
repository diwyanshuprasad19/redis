# Redis project scaffold — separate repo under github_project/redis

Python + Redis + optional Postgres (via platform-ops data-stack).

## Local-first (required before PR)

```bash
cd ../platform-ops
make local-gate REPO=redis      # must be GREEN
make anti-slop REPO=redis       # aislop ≥ 80
make auto REPO=redis TITLE="…"  # push + PR only if green
```

## Local data (from platform-ops)

```bash
cd ../platform-ops
make data-up
# Redis: localhost:6380
# Postgres redis_app: localhost:5433  user/pass app/app
make alembic REPO=redis
```

## Observability (local + GCP)

Shared stack lives in `platform-ops` — see `../platform-ops/OBSERVABILITY.md`.

```bash
cd ../platform-ops
make obs-up            # Alloy + Prometheus + Loki + Grafana :3001 + Uptime Kuma :3002
make obs-gcp-check SERVICE=api   # after Cloud Run deploy
```

App signals: Prometheus `/metrics` + JSON logs (`LOG_FORMAT=json`). Cloud Run ships both to Cloud Logging / Monitoring automatically on `make deploy`.

## PR automation

```bash
cd ../platform-ops
make auto REPO=redis TITLE="feat: …"
```

Runs anti-slop → local-gate → lint/security/graphify → push → PR → PR-Agent.
