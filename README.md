# DecisionAtlas

DecisionAtlas turns engineering repo context into a searchable decision memory with citations and drift alerts.

Current project stage:

- core MVP complete
- `v0.2` demo hardening complete
- guided demo lane stable
- next priority: strengthen real repository analysis so the product can complete real-world tasks more credibly

Example why-questions:

- Why did we choose Redis as cache only?
- Why is PostgreSQL still the primary database?
- Why does this candidate decision need review?
- Why did this pull request trigger a drift alert?
- Why did we move this workflow into a queue?

What the product already does:

- imports GitHub issues, PRs, commits, markdown, ADRs, text notes, and optional docx content
- supports fake-provider local mode and OpenAI-compatible live provider mode
- supports one-off live analysis runs for public GitHub repositories through imported workspaces
- extracts candidate decisions with source references and stage-aware extraction progress
- lets a reviewer accept, reject, or supersede decisions
- answers why-questions with citation-first responses
- flags rule-first and semantic drift alerts after manual evaluation

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

For a one-command local bring-up:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\dev\start-demo-stack.ps1
```

This script starts an isolated, SQLite-backed demo workspace and does not depend on the Docker PostgreSQL volume state. It is the fastest way to experience the product locally.

For a one-command real stack bring-up:

```powershell
pnpm run dev:real
```

or double-click:

```text
scripts\dev\start-real-stack.bat
```

This real-stack script:

- starts Docker `postgres` and `redis`
- runs engine migrations against PostgreSQL
- seeds `demo-workspace` into PostgreSQL
- starts `engine`, `api`, and `web`
- records managed process state under `.tmp/real-stack.json`

To stop the managed real stack:

```powershell
pnpm run dev:real:stop
```

or double-click:

```text
scripts\dev\stop-real-stack.bat
```

The public `demo-workspace` is intentionally seeded for a stable walkthrough. Imported workspaces use real repository artifacts and may produce different decision, why-answer, and drift coverage depending on the source repo.

For live analysis, the current supported scope is:

- public GitHub repositories only
- one-off imported workspace analysis, not long-lived GitHub App connections
- results may end in useful candidates, explicit `insufficient_evidence`, or `conversion_limited` diagnostics depending on repository signal and extraction quality
- drift evaluation is available for imported workspaces but is currently triggered manually from the product UI

Current operating model:

- `demo-workspace` is the stable product walkthrough
- imported workspaces are the real-capability lane
- fake/live provider switching affects the next real run or extraction path, not the already-rendered demo results on screen
- imported-workspace dashboards now expose extraction funnel progress and post-run conversion diagnostics

Then open:

- Web: `http://localhost:3000`
- API: `http://localhost:3001/health`
- Engine: `http://localhost:8000/health`

The `.env.example` file still points `DATABASE_URL` at the local PostgreSQL container for manual deployment-style runs.

Project docs:

- [Quick Start](./docs/project/quick-start.md)
- [Demo Script](./docs/project/demo-script.md)
- [Deployment](./docs/project/deployment.md)
- [FAQ](./docs/project/faq.md)
- [Release Checklist](./docs/project/release-checklist.md)
- [Real Repository Validation Baseline](./docs/project/real-repository-validation-baseline.md)
- [v0.2 Release Notes](./docs/project/release-notes-v0.2.md)
- [Project Blueprint](./docs/plans/2026-03-18-decisionatlas-project-blueprint.md)
- [Implementation Plan](./docs/plans/2026-03-18-decisionatlas-implementation-plan.md)
- [v0.2 Implementation Plan](./docs/plans/2026-03-18-decisionatlas-v0.2-implementation-plan.md)
- [Post-v0.2 Next Steps](./docs/plans/2026-03-23-post-v0.2-next-steps.md)
- [v0.3 Backlog](./docs/plans/2026-03-18-decisionatlas-v0.3-backlog.md)

Next recommended direction:

1. keep the guided demo stable
2. improve the real imported-workspace path so live analysis produces more useful decisions, answers, and drift signals on public repositories
3. only after that, move on to hosted demo delivery and later v0.3 platform work

Real-functionality priorities:

- improve end-to-end live-provider validation on public repositories
- widen the set of real repository signals that can turn into accepted decisions
- make drift evaluation more operational after real imports
- measure repository outcomes instead of relying on demo-only confidence

Known limitations:

- MVP auth and multi-user permissions are not implemented yet
- semantic drift labels are conservative and intentionally narrow
- the public demo workspace is seeded and should not be confused with a fully imported repository workspace
- GitHub import still uses token mode, not GitHub App auth
- live analysis currently supports public repositories only, not private repo auth flows
- real imported workspaces can still be sparse or conversion-limited depending on repository signal quality and extraction grounding
- indexing chunking is still MVP-style and not yet structure-aware
- why-search can still over-merge adjacent accepted decisions into one answer when multiple nearby hits score well
