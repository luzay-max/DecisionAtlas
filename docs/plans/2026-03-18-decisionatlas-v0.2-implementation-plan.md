# DecisionAtlas v0.2 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Turn the completed MVP into a stable public demo product with real provider support, hardened import flows, deployment guidance, and repeatable demo validation.

**Architecture:** v0.2 keeps the current `web + api + engine + postgres + redis` shape intact and hardens the existing flows instead of adding new platform scope. The work is centered on three production-facing paths: provider-backed extraction/query/drift, import job state and idempotent sync, and demo/deployment experience.

**Tech Stack:** `Next.js`, `TypeScript`, `Fastify`, `FastAPI`, `SQLAlchemy`, `Alembic`, `uv`, `PostgreSQL`, `Redis`, `Playwright`, `pytest`, `Vitest`, `Docker Compose`

---

## Summary

The MVP baseline is already complete through Week 12. v0.2 focuses on public demo readiness, not new product breadth.

This plan is intentionally sequenced to reduce risk:

1. Make provider usage real, configurable, and fail-closed.
2. Make GitHub import observable and safe to rerun.
3. Make the demo workspace and UI feel intentional.
4. Make deployment and release checks reproducible.

## Task 1: Provider Configuration And Runtime Selection

**Files:**
- Modify: `services/engine/app/config.py`
- Modify: `services/engine/app/llm/base.py`
- Modify: `services/engine/app/llm/openai_compatible.py`
- Modify: `services/engine/app/indexing/embedder.py`
- Create: `services/engine/app/llm/provider_factory.py`
- Create: `services/engine/tests/llm/test_provider_factory.py`

**Step 1: Write failing tests**

- Add tests for:
  - fake provider selection when no API key exists
  - real provider selection when env vars are present
  - explicit error on missing model/base-url for real provider
  - embedding failure on empty provider response

**Step 2: Run tests to verify failure**

Run:

```powershell
cd services/engine
python -m uv run pytest tests/llm/test_provider_factory.py -q
```

Expected: missing factory/config behavior.

**Step 3: Implement minimal runtime provider factory**

- Add env settings for provider mode, chat model, embedding model, provider base URL, timeout, and demo repo defaults.
- Extend the provider abstraction so extraction, answering, and semantic drift can share one configured provider path.
- Add explicit exceptions for configuration errors, upstream HTTP failures, timeouts, rate limits, and malformed provider responses.
- Keep fake provider and fake embedder as the CI-safe default when no live credentials are present.

**Step 4: Run focused validation**

Run:

```powershell
cd services/engine
python -m uv run pytest tests/llm/test_fake_provider.py tests/llm/test_provider_factory.py -q
```

Expected: PASS.

**Step 5: Commit**

```powershell
git add services/engine/app/config.py services/engine/app/llm services/engine/app/indexing/embedder.py services/engine/tests/llm/test_provider_factory.py
git commit -m "feat: add configurable provider runtime"
```

## Task 2: Real Provider Wiring In Extraction, Query, And Drift

**Files:**
- Modify: `services/engine/app/extractor/pipeline.py`
- Modify: `services/engine/app/retrieval/answering.py`
- Modify: `services/engine/app/drift/semantic_recall.py`
- Modify: `services/engine/app/api/query.py`
- Modify: `services/engine/app/api/imports.py`
- Create: `services/engine/tests/retrieval/test_live_provider_fallback.py`

**Step 1: Write failing tests**

- Cover:
  - query path uses configured embedder/provider instead of always fake
  - extraction path can run with fake by default and live provider when configured
  - provider exceptions return explicit API errors instead of silent fallthrough

**Step 2: Run failing tests**

```powershell
cd services/engine
python -m uv run pytest tests/retrieval/test_live_provider_fallback.py -q
```

**Step 3: Implement provider-aware orchestration**

- Move provider/embedder selection behind one factory used by query, extraction, and semantic drift.
- Keep citation-first response shape unchanged.
- Preserve fail-closed behavior: provider errors do not become fabricated answers.

**Step 4: Re-run engine tests**

```powershell
cd services/engine
python -m uv run pytest tests/extractor/test_pipeline.py tests/retrieval/test_answering.py tests/drift/test_semantic_recall.py tests/retrieval/test_live_provider_fallback.py -q
```

**Step 5: Commit**

```powershell
git add services/engine/app/extractor/pipeline.py services/engine/app/retrieval/answering.py services/engine/app/drift/semantic_recall.py services/engine/app/api/query.py services/engine/app/api/imports.py services/engine/tests/retrieval/test_live_provider_fallback.py
git commit -m "feat: wire provider runtime into engine flows"
```

## Task 3: Import Mode, Job Status, And Idempotent Reruns

**Files:**
- Modify: `services/engine/app/db/models.py`
- Modify: `services/engine/alembic/versions/0001_initial_schema.py` or add follow-up migration
- Create: `services/engine/app/repositories/import_jobs.py`
- Modify: `services/engine/app/jobs/import_jobs.py`
- Modify: `services/engine/app/ingest/github_importer.py`
- Modify: `services/engine/app/api/imports.py`
- Modify: `apps/api/src/routes/imports.ts`
- Modify: `apps/web/lib/api.ts`
- Modify: `apps/web/components/dashboard/demo-import-button.tsx`
- Create: `services/engine/tests/api/test_import_job_status_api.py`
- Update: `services/engine/tests/ingest/test_github_importer.py`
- Update: `apps/api/tests/imports-route.test.ts`

**Step 1: Write failing tests**

- Cover:
  - `POST /imports/github` accepts `mode`
  - `GET /imports/{job_id}` returns persisted status
  - importer supports `full` and `since_last_sync`
  - repeat imports do not duplicate artifacts
  - failed imports surface `error_message`

**Step 2: Run failing tests**

```powershell
cd services/engine
python -m uv run pytest tests/api/test_imports.py tests/api/test_import_job_status_api.py tests/ingest/test_github_importer.py -q
pnpm --filter @decisionatlas/api test -- imports-route
```

**Step 3: Implement import hardening**

- Add an `import_jobs` table with status, mode, timing, repo, counts, and error summary.
- Persist job lifecycle as `queued -> running -> succeeded|failed`.
- Add GitHub import modes:
  - `full`
  - `since_last_sync`
- Use the last successful job timestamp to scope incremental fetches.
- Return summary counts from the engine and proxy them through the Node API.

**Step 4: Re-run validation**

```powershell
cd services/engine
python -m uv run pytest tests/api/test_imports.py tests/api/test_import_job_status_api.py tests/ingest/test_github_importer.py -q
cd ..\..
pnpm --filter @decisionatlas/api test
```

**Step 5: Commit**

```powershell
git add services/engine/app/db/models.py services/engine/alembic services/engine/app/repositories/import_jobs.py services/engine/app/jobs/import_jobs.py services/engine/app/ingest/github_importer.py services/engine/app/api/imports.py apps/api/src/routes/imports.ts apps/web/lib/api.ts apps/web/components/dashboard/demo-import-button.tsx services/engine/tests/api/test_import_job_status_api.py services/engine/tests/ingest/test_github_importer.py apps/api/tests/imports-route.test.ts
git commit -m "feat: add import job tracking and incremental sync"
```

## Task 4: Demo Workspace And UI Completion

**Files:**
- Modify: `examples/demo-workspace/workspace.json`
- Modify: `examples/demo-workspace/queries.json`
- Modify: `examples/demo-workspace/expected-answers.json`
- Modify: `apps/web/app/page.tsx`
- Modify: `apps/web/components/dashboard/workspace-dashboard-content.tsx`
- Modify: `apps/web/components/review/review-page-content.tsx`
- Modify: `apps/web/app/search/page.tsx` or related search components
- Create: `apps/web/tests/home-demo-flow.test.tsx`

**Step 1: Write failing tests**

- Cover:
  - homepage presents the demo path
  - review queue prefers high-confidence candidates
  - dashboard surfaces demo repo and latest import state
  - search/detail/drift pages show purposeful empty states

**Step 2: Run failing tests**

```powershell
pnpm --filter @decisionatlas/web test -- home-demo-flow
```

**Step 3: Implement demo-facing UX**

- Replace generic landing copy with a guided three-step demo story.
- Make dashboard import CTA use configured demo repo instead of hardcoded placeholder.
- Sort candidate decisions by confidence, newest first.
- Add empty-state copy that explains what to do next.

**Step 4: Re-run validation**

```powershell
pnpm --filter @decisionatlas/web test
pnpm --filter @decisionatlas/web typecheck
```

**Step 5: Commit**

```powershell
git add examples/demo-workspace apps/web
git commit -m "feat: improve public demo flow"
```

## Task 5: Deployment, Docs, And Release Gate

**Files:**
- Modify: `README.md`
- Modify: `docs/project/quick-start.md`
- Modify: `docs/project/demo-script.md`
- Create: `docs/project/deployment.md`
- Create: `docs/project/release-notes-v0.2.md`
- Create: `docs/plans/2026-03-18-decisionatlas-v0.3-backlog.md`
- Modify: `scripts/ci/pre-release.ps1`
- Modify: `scripts/ci/run_demo_smoke.ps1`

**Step 1: Write failing or missing coverage checks**

- Identify doc/script gaps by running the current pre-release and smoke commands.

**Step 2: Run current gate**

```powershell
pnpm test
pnpm typecheck
cd services/engine
python -m uv run pytest -q
cd ..\..
python scripts/ci/run_benchmark.py
```

**Step 3: Implement release hardening**

- Add one-machine deployment instructions with network topology and environment requirements.
- Update README and demo script to center the hosted demo story.
- Add release notes documenting supported scope, known limits, and deferred v0.3 items.
- Extend local release scripts so one command validates demo readiness.

**Step 4: Run final verification**

```powershell
pnpm test
pnpm typecheck
cd services/engine
python -m uv run pytest -q
cd ..\..
python scripts/ci/run_benchmark.py
pnpm --filter @decisionatlas/web exec playwright test
```

**Step 5: Commit**

```powershell
git add README.md docs/project docs/plans scripts/ci
git commit -m "docs: finalize v0.2 demo release materials"
```

## Definition Of Done

v0.2 is done when all of the following are true:

- No-key local development and CI still run entirely on fake providers.
- Real provider configuration can drive extraction and why-query without code changes.
- GitHub import supports both full and incremental modes and exposes job status.
- The public demo path is visible from the homepage and dashboard.
- Release docs explain local run, hosted deployment, demo flow, and known limits.
- Tests, benchmark, smoke flow, and CI pass together.
