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

The copied `.env` file points the engine at local PostgreSQL and Redis.

```powershell
cd services/engine
uv run alembic upgrade head
uv run python app/db/seed_demo.py
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

## Demo-specific validation

Run the benchmark fixture check:

```powershell
python scripts/ci/run_benchmark.py
```

Run browser smoke coverage:

```powershell
pnpm --filter @decisionatlas/web exec playwright install chromium
pnpm --filter @decisionatlas/web exec playwright test
```

## Common issues

- If `uv` is not on `PATH` but `python -m uv --version` works, use `python -m uv ...` for local commands. CI uses the `uv` CLI directly.
- If import succeeds but no meaningful candidates appear, verify `LLM_PROVIDER_MODE`, `LLM_API_KEY`, `LLM_MODEL`, and `EMBEDDING_MODEL` are set for a live provider-backed demo.
- If Docker is running but services are unavailable, retry `docker compose up -d postgres redis`
- If `.docx` import is skipped, confirm `pandoc` is installed and available from the terminal
