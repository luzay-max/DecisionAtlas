# Quick Start

This project is optimized for local development on a single machine.

## Prerequisites

- `pnpm`
- Python `3.11+`
- Docker Desktop
- `pandoc` if you want `.docx` import

## Install

From the repository root:

```powershell
pnpm install
uv sync --project services/engine
Copy-Item .env.example .env
```

Fast path for the local demo:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\dev\prepare-demo.ps1
```

Full one-command startup:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\dev\start-demo-stack.ps1
```

This path starts an isolated SQLite demo database under `.tmp/` so the curated demo stays reproducible even if your local PostgreSQL container already has old state.

For a live public demo, edit `.env` and set:

- `LLM_PROVIDER_MODE=openai_compatible`
- `LLM_API_KEY`
- `LLM_MODEL`
- `EMBEDDING_MODEL`
- optional: `EMBEDDING_API_KEY`, `LLM_BASE_URL`, `DEMO_REPO`

## Start local infrastructure

```powershell
docker compose up -d postgres redis
```

Expected local ports:

- PostgreSQL: `5432`
- Redis: `6379`

## Prepare the engine database

The copied `.env` file points the engine at local PostgreSQL and Redis. Use this path when you want a deployment-like local environment instead of the isolated one-command demo.

```powershell
cd services/engine
uv run alembic upgrade head
uv run python -m app.db.seed_demo
cd ..\..
```

## Run services

Terminal 1:

```powershell
cd services/engine
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Terminal 2:

```powershell
pnpm --filter @decisionatlas/api dev
```

Terminal 3:

```powershell
pnpm --filter @decisionatlas/web dev
```

## Verify

Check health endpoints:

```powershell
Invoke-WebRequest http://localhost:3001/health
Invoke-WebRequest http://localhost:8000/health
```

Open the web app:

- `http://localhost:3000`
- `http://localhost:3000/workspaces/demo-workspace`
- `http://localhost:3000/review`
- `http://localhost:3000/search`
- `http://localhost:3000/drift`

For a real public repository analysis run, use the live-analysis form on the homepage and submit either `owner/repo` or a full GitHub URL. The resulting imported workspace will be separate from `demo-workspace`.

## Demo-specific validation

Run the benchmark fixture check:

```powershell
python scripts/ci/run_benchmark.py
```

This now validates both the guided demo fixtures and the curated live-analysis benchmark repository set under `examples/live-benchmarks/`.

Run browser smoke coverage:

```powershell
pnpm --filter @decisionatlas/web exec playwright install chromium
pnpm --filter @decisionatlas/web exec playwright test
```

## Common issues

- If `uv` is not on `PATH` but `python -m uv --version` works, use `python -m uv ...` for local commands. CI uses the `uv` CLI directly.
- If import succeeds but no meaningful candidates appear, verify `LLM_PROVIDER_MODE`, `LLM_API_KEY`, `LLM_MODEL`, and `EMBEDDING_MODEL` are set for a live provider-backed demo.
- Live analysis currently supports public GitHub repositories only. Private repositories and GitHub App flows are out of scope for this phase.
- If Docker is running but services are unavailable, retry `docker compose up -d postgres redis`
- If `.docx` import is skipped, confirm `pandoc` is installed and available from the terminal
