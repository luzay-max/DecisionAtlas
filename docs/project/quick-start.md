# Quick Start

[Home](../README.md) | [Deployment](deployment.md) | [FAQ](faq.md) | [Demo Script](demo-script.md) | [中文](quick-start_zh-CN.md)

---

This project is optimized for local development on a single machine.

### Prerequisites

- `pnpm`
- Python `3.11+`
- Docker Desktop
- `pandoc` (optional, for `.docx` import)

### Install

From the repository root:

```powershell
pnpm install
uv sync --project services/engine
Copy-Item .env.example .env
```

### Quick Demo (Fastest Path)

Start an isolated SQLite-backed demo in one command:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\dev\start-demo-stack.ps1
```

This starts a curated demo workspace under `.tmp/` — isolated from your local PostgreSQL container state.

### Full Stack Setup

For a deployment-like environment with PostgreSQL and Redis:

```powershell
# 1. Start infrastructure
docker compose up -d postgres redis

# 2. Prepare the database
cd services/engine
uv run alembic upgrade head
uv run python -m app.db.seed_demo
cd ..\..

# 3. Start services
# Terminal 1: Engine
cd services/engine
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000

# Terminal 2: API
pnpm --filter @decisionatlas/api dev

# Terminal 3: Web
pnpm --filter @decisionatlas/web dev
```

### Live Provider Mode

Edit `.env` to connect to a real LLM provider:

```env
LLM_PROVIDER_MODE=openai_compatible
LLM_API_KEY=your_api_key
LLM_MODEL=gpt-4o
EMBEDDING_MODEL=text-embedding-3-small
# Optional
EMBEDDING_API_KEY=your_api_key
LLM_BASE_URL=https://api.openai.com/v1
```

### Verify

Check health endpoints:

```powershell
Invoke-WebRequest http://localhost:3001/health
Invoke-WebRequest http://localhost:8000/health
```

Open the web app:

- Web UI: `http://localhost:3000`
- Demo Workspace: `http://localhost:3000/workspaces/demo-workspace`
- Review: `http://localhost:3000/review`
- Search: `http://localhost:3000/search`
- Drift: `http://localhost:3000/drift`

### Common Issues

| Issue | Solution |
|-------|----------|
| `uv` not on PATH | Use `python -m uv ...` instead. The pre-release script handles this automatically. |
| Import succeeds but no candidates | Verify `LLM_PROVIDER_MODE`, `LLM_API_KEY`, `LLM_MODEL`, and `EMBEDDING_MODEL` are set. |
| Live analysis fails | Currently only supports **public GitHub repositories**. Private repos and GitHub App flows are out of scope. |
| Docker services unavailable | Retry `docker compose up -d postgres redis` |
| `.docx` import skipped | Confirm `pandoc` is installed and available in terminal. |
