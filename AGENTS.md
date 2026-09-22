# Agent / AI coding guide

Implementation / bug fix / meaningful refactor work follows the **autonomous
production-engineering workflow** in `.cursor/rules/autonomous-engineering.mdc`
and `.cursor/agents/` (product-analyst → architect → implementer → test-engineer →
edge/security/production reviewers → final-verifier). Prefer saying
`Implement this feature: …` / `Fix this bug: …` and let the orchestrator drive.

Use this file so code stays consistent and **human**, not AI-slop.

## Principles
- Match existing project structure and naming; do not invent parallel frameworks.
- Prefer small, reviewable diffs; one concern per PR.
- Never commit secrets (`.env`, keys, tokens). Use examples only.
- Add or update tests when changing behavior.
- Document operator-facing changes in README or PR body.

## Anti-slop (enforced by `make anti-slop` / `make auto`)
- No narrative comments that restate what the next line does.
- No `# === Helpers ===` banner comments or apologetic TODOs.
- No bare `except:` / empty `except Exception: pass`.
- No placeholder `pass  # implement later` left in merged code.
- Prefer clear names over generic `data`, `result`, `temp`, `helper2`.
- Run `ruff format` / `ruff check --fix` before finishing.
- Tools: **aislop**, **sloplint**, **agent-slop-lint**, **ruff**, optional **Strix**.

## Before finishing a task
1. `make anti-slop REPO=redis`
2. `make local-gate REPO=redis`
3. `make security REPO=redis`
4. Summarize risk (auth, data, deploy) in the PR.

## Stack awareness (redis)
- Redis-backed services + Postgres where present; respect TTL/eviction semantics.
- Prefer pooled clients and pipelines for multi-key work.
- Prod secrets via Secret Manager / WIF — never bake keys into the repo.
- Observability: JSON logs + Prometheus; correlation ids on requests.

## Data locally
- Shared Postgres/Redis: `make data-up` in platform-ops (5433 / 6380).
- Migrations: `make alembic REPO=redis` or in-repo Alembic.
