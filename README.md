# DecisionAtlas

DecisionAtlas turns engineering repo context into a searchable decision memory with citations and drift alerts.

Example why-questions:

- Why did we choose Redis as cache only?
- Why is PostgreSQL still the primary database?
- Why does this candidate decision need review?
- Why did this pull request trigger a drift alert?
- Why did we move this workflow into a queue?

What the MVP already does:

- imports GitHub issues, PRs, commits, markdown, ADRs, text notes, and optional docx content
- supports fake-provider local mode and OpenAI-compatible live provider mode
- extracts candidate decisions with source references
- lets a reviewer accept, reject, or supersede decisions
- answers why-questions with citation-first responses
- flags rule-first and semantic drift alerts

Architecture snapshot:

- `apps/web`: Next.js UI for review, search, timeline, dashboard, and drift
- `apps/api`: Fastify edge API and future auth boundary
- `services/engine`: FastAPI engine for ingest, extraction, retrieval, and drift
- `PostgreSQL + pgvector`: durable storage and search index
- `Redis`: background coordination for future async jobs

Quick start:

```powershell
pnpm install
uv sync --project services/engine
Copy-Item .env.example .env
docker compose up -d postgres redis
cd services/engine
uv run alembic upgrade head
uv run python -m app.db.seed_demo
cd ..\..
pnpm --filter @decisionatlas/api dev
pnpm --filter @decisionatlas/web dev
```

If `uv` is not on `PATH` but `python -m uv --version` works, replace `uv ...` with `python -m uv ...` for local shell commands.

For a live provider-backed demo, set these before starting services:

- `LLM_PROVIDER_MODE=openai_compatible`
- `LLM_API_KEY=...`
- `LLM_MODEL=...`
- `EMBEDDING_MODEL=...`
- optionally `EMBEDDING_API_KEY` and `LLM_BASE_URL`

Then open:

- Web: `http://localhost:3000`
- API: `http://localhost:3001/health`
- Engine: `http://localhost:8000/health`

The `.env.example` file already points `DATABASE_URL` at the local PostgreSQL container.

Project docs:

- [Quick Start](./docs/project/quick-start.md)
- [Demo Script](./docs/project/demo-script.md)
- [Deployment](./docs/project/deployment.md)
- [FAQ](./docs/project/faq.md)
- [Release Checklist](./docs/project/release-checklist.md)
- [v0.2 Release Notes](./docs/project/release-notes-v0.2.md)
- [Project Blueprint](./docs/plans/2026-03-18-decisionatlas-project-blueprint.md)
- [Implementation Plan](./docs/plans/2026-03-18-decisionatlas-implementation-plan.md)
- [v0.2 Implementation Plan](./docs/plans/2026-03-18-decisionatlas-v0.2-implementation-plan.md)

Screenshots:

- dashboard screenshot: pending
- review queue screenshot: pending
- why-search screenshot: pending
- drift alerts screenshot: pending

Known limitations:

- MVP auth and multi-user permissions are not implemented yet
- semantic drift labels are conservative and intentionally narrow
- demo flows are optimized for one seeded workspace
- GitHub import still uses token mode, not GitHub App auth
