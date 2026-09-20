# Redis project scaffold — separate repo under github_project/redis

Python + Redis + optional Postgres (via platform-ops data-stack).

## Local data (from platform-ops)

```bash
cd ../platform-ops
make data-up
# Redis: localhost:6380
# Postgres redis_app: localhost:5433  user/pass app/app
make alembic REPO=redis
```

## PR automation

```bash
cd ../platform-ops
make auto REPO=redis TITLE="feat: …"
```

Runs anti-slop → lint/security/graphify → push → PR.
