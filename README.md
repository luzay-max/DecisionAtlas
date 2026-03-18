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
python -m uv sync --project services/engine
Copy-Item .env.example .env
docker compose up -d postgres redis
cd services/engine
python -m uv run alembic upgrade head
python -m uv run python app/db/seed_demo.py
cd ..\..
pnpm --filter @decisionatlas/api dev
pnpm --filter @decisionatlas/web dev
```

Then open:

- Web: `http://localhost:3000`
- API: `http://localhost:3001/health`
- Engine: `http://localhost:8000/health`

The `.env.example` file already points `DATABASE_URL` at the local PostgreSQL container.

Project docs:

- [Quick Start](./docs/project/quick-start.md)
- [Demo Script](./docs/project/demo-script.md)
- [FAQ](./docs/project/faq.md)
- [Release Checklist](./docs/project/release-checklist.md)
- [Project Blueprint](./docs/plans/2026-03-18-decisionatlas-project-blueprint.md)
- [Implementation Plan](./docs/plans/2026-03-18-decisionatlas-implementation-plan.md)

Screenshots:

- dashboard screenshot: pending
- review queue screenshot: pending
- why-search screenshot: pending
- drift alerts screenshot: pending

Known limitations:

- MVP auth and multi-user permissions are not implemented yet
- semantic drift labels are conservative and intentionally narrow
- demo flows are optimized for one seeded workspace
