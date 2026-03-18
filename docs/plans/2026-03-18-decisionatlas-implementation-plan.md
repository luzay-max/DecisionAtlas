# DecisionAtlas MVP Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a self-hosted MVP that imports GitHub and docs, extracts candidate decisions, answers why-questions with citations, and flags first-pass drift alerts.

**Architecture:** The MVP keeps the blueprint’s logical layers (`ingest`, `extractor`, `retrieval`, `drift`) but deploys them as one Python `engine` service to reduce early complexity. A Next.js web app handles UI, a thin Fastify API handles external requests and future auth boundaries, PostgreSQL owns persistent state and vector/full-text search, and Redis handles background job coordination.

**Tech Stack:** `pnpm`, `Next.js`, `TypeScript`, `Fastify`, `uv`, `FastAPI`, `SQLAlchemy`, `Alembic`, `PostgreSQL`, `pgvector`, `Redis`, `Dramatiq`, `Vitest`, `pytest`, `Playwright`, `Docker Compose`, `pandoc`

---

## Planning Conventions

- Package manager: `pnpm`
- Python environment manager: `uv`
- Node test runner: `vitest`
- Python test runner: `pytest`
- Browser test runner: `playwright`
- DB schema owner: `services/engine`
- DTO/schema sharing: `packages/schema`
- Commit rule: one task, one commit
- Release rule: no live model or GitHub API call is required for automated tests

## Owner Inputs Required Before Week 1

These are hard prerequisites. No code should start before they are fixed in writing.

- Final repo name: `DecisionAtlas` unless you explicitly change it
- Demo repository: one public GitHub repo with active issues, PRs, and docs
- Model provider: one OpenAI-compatible provider for chat and embeddings
- Required Decision Card fields:
  - `title`
  - `problem`
  - `chosen_option`
  - `tradeoffs`
  - `confidence`
  - `review_state`
- Drift visibility default: `internal only` for MVP

Record these in:

- `docs/architecture/adr/0001-mvp-stack.md`
- `docs/architecture/adr/0002-decision-as-core-object.md`
- `docs/architecture/adr/0003-citation-first-answering.md`
- `docs/architecture/adr/0004-rule-first-drift.md`
- `docs/project/owner-decisions.md`

## Repository Shape Assumed By This Plan

```text
apps/
  web/
  api/
services/
  engine/
packages/
  schema/
  ui/
docs/
  architecture/adr/
  plans/
  project/
examples/
  demo-workspace/
infra/
  docker/
scripts/
  dev/
  ci/
```

## Week 1: Project Skeleton And Decision Freeze

**Week goal:** Create a stable monorepo foundation, freeze the four MVP ADRs, and make the empty project runnable locally.

**Exit criteria:**

- `pnpm install` works from repo root
- `uv sync` works in `services/engine`
- `docker compose up -d postgres redis` succeeds
- ADRs and owner decisions exist in markdown

### Task W1-1: Bootstrap the root workspace

**Files:**
- Create: `package.json`
- Create: `pnpm-workspace.yaml`
- Create: `turbo.json`
- Create: `.gitignore`
- Create: `.editorconfig`
- Create: `.env.example`
- Create: `README.md`

**Steps:**
1. Create the root `package.json` with workspace scripts: `dev`, `lint`, `test`, `typecheck`, `format`.
2. Create `pnpm-workspace.yaml` for `apps/*` and `packages/*`.
3. Create `turbo.json` with pipelines for `build`, `dev`, `lint`, `test`, `typecheck`.
4. Create `.env.example` with `DATABASE_URL`, `REDIS_URL`, `LLM_API_KEY`, `EMBEDDING_API_KEY`, `GITHUB_TOKEN`, `ENGINE_BASE_URL`, `API_BASE_URL`.
5. Run: `pnpm install`
6. Run: `pnpm exec turbo run lint --continue`
7. Commit: `git commit -m "chore: bootstrap monorepo workspace"`

**Expected result:** Root workspace commands resolve, even if some package-level targets are not created yet.

### Task W1-2: Create the Next.js web shell

**Files:**
- Create: `apps/web/package.json`
- Create: `apps/web/tsconfig.json`
- Create: `apps/web/next.config.ts`
- Create: `apps/web/app/layout.tsx`
- Create: `apps/web/app/page.tsx`
- Create: `apps/web/app/globals.css`
- Create: `apps/web/vitest.config.ts`
- Create: `apps/web/tests/home-page.test.tsx`

**Steps:**
1. Write `apps/web/tests/home-page.test.tsx` to assert the landing page renders the project name and the three MVP concepts: `Import`, `Decisions`, `Why`.
2. Run: `pnpm --filter @decisionatlas/web test`
3. Create the minimal Next.js app shell and make the test pass.
4. Run: `pnpm --filter @decisionatlas/web test`
5. Run: `pnpm --filter @decisionatlas/web typecheck`
6. Commit: `git commit -m "feat: add web app shell"`

**Expected result:** The web app renders a simple placeholder homepage and has one passing UI test.

### Task W1-3: Create the Fastify API shell

**Files:**
- Create: `apps/api/package.json`
- Create: `apps/api/tsconfig.json`
- Create: `apps/api/src/server.ts`
- Create: `apps/api/src/routes/health.ts`
- Create: `apps/api/src/plugins/env.ts`
- Create: `apps/api/vitest.config.ts`
- Create: `apps/api/tests/health-route.test.ts`

**Steps:**
1. Write `apps/api/tests/health-route.test.ts` to assert `GET /health` returns `200` and `{ ok: true }`.
2. Run: `pnpm --filter @decisionatlas/api test`
3. Implement the minimal Fastify app and health route.
4. Run: `pnpm --filter @decisionatlas/api test`
5. Run: `pnpm --filter @decisionatlas/api typecheck`
6. Commit: `git commit -m "feat: add api service shell"`

**Expected result:** The API process starts locally and exposes a health endpoint.

### Task W1-4: Create the Python engine shell

**Files:**
- Create: `services/engine/pyproject.toml`
- Create: `services/engine/app/main.py`
- Create: `services/engine/app/config.py`
- Create: `services/engine/app/api/health.py`
- Create: `services/engine/tests/test_health.py`

**Steps:**
1. Write `services/engine/tests/test_health.py` to assert `GET /health` returns `200` and `{"ok": true}`.
2. Run: `uv run --project services/engine pytest services/engine/tests/test_health.py -q`
3. Implement the minimal FastAPI engine and config loading.
4. Run: `uv run --project services/engine pytest services/engine/tests/test_health.py -q`
5. Run: `uv run --project services/engine python -m app.main`
6. Commit: `git commit -m "feat: add engine service shell"`

**Expected result:** The engine starts and exposes a health endpoint.

### Task W1-5: Freeze the MVP decisions as ADRs

**Files:**
- Create: `docs/architecture/adr/0001-mvp-stack.md`
- Create: `docs/architecture/adr/0002-decision-as-core-object.md`
- Create: `docs/architecture/adr/0003-citation-first-answering.md`
- Create: `docs/architecture/adr/0004-rule-first-drift.md`
- Create: `docs/project/owner-decisions.md`

**Steps:**
1. Write the four ADRs using the chosen decisions from the blueprint.
2. Write `docs/project/owner-decisions.md` with the demo repo choice, provider choice, mandatory Decision fields, and drift visibility.
3. Run: `rg "Status|Decision|Consequences" docs/architecture/adr`
4. Commit: `git commit -m "docs: record mvp architectural decisions"`

**Expected result:** Product and technical scope are frozen before feature work begins.

## Week 2: Local Infrastructure And Database Ownership

**Week goal:** Make the project runnable with PostgreSQL, pgvector, Redis, and an owned schema for workspaces, artifacts, decisions, source refs, relations, and drift alerts.

**Exit criteria:**

- `docker compose up -d` starts all local infra
- `alembic upgrade head` works
- schema tests pass

### Task W2-1: Add Docker Compose and local infra

**Files:**
- Create: `docker-compose.yml`
- Create: `infra/docker/postgres/init-extensions.sql`
- Create: `infra/docker/redis/redis.conf`
- Create: `scripts/dev/up.ps1`

**Steps:**
1. Write `docker-compose.yml` for `postgres`, `redis`, `web`, `api`, `engine`.
2. Add `init-extensions.sql` to enable `pgvector`.
3. Add `scripts/dev/up.ps1` to start infra and print service URLs.
4. Run: `docker compose up -d postgres redis`
5. Run: `docker compose ps`
6. Commit: `git commit -m "chore: add local development infrastructure"`

**Expected result:** Postgres and Redis start reliably on a clean machine.

### Task W2-2: Create the database models and migrations

**Files:**
- Create: `services/engine/alembic.ini`
- Create: `services/engine/alembic/env.py`
- Create: `services/engine/alembic/versions/0001_initial_schema.py`
- Create: `services/engine/app/db/base.py`
- Create: `services/engine/app/db/models.py`
- Create: `services/engine/tests/db/test_schema.py`

**Steps:**
1. Write `services/engine/tests/db/test_schema.py` to assert the initial tables exist:
   - `workspaces`
   - `artifacts`
   - `artifact_chunks`
   - `decisions`
   - `source_refs`
   - `relations`
   - `drift_alerts`
2. Run: `uv run --project services/engine pytest services/engine/tests/db/test_schema.py -q`
3. Implement SQLAlchemy models and Alembic migration `0001_initial_schema.py`.
4. Run: `uv run --project services/engine alembic upgrade head`
5. Run: `uv run --project services/engine pytest services/engine/tests/db/test_schema.py -q`
6. Commit: `git commit -m "feat: add initial database schema"`

**Expected result:** The engine owns a repeatable DB schema and migration chain.

### Task W2-3: Create shared DTOs and API contracts

**Files:**
- Create: `packages/schema/package.json`
- Create: `packages/schema/src/decision.ts`
- Create: `packages/schema/src/artifact.ts`
- Create: `packages/schema/src/query.ts`
- Create: `packages/schema/src/index.ts`
- Create: `packages/schema/tests/schema-contracts.test.ts`

**Steps:**
1. Write `packages/schema/tests/schema-contracts.test.ts` to assert `DecisionDto`, `ArtifactDto`, and `WhyQueryDto` parse valid fixtures and reject invalid ones.
2. Run: `pnpm --filter @decisionatlas/schema test`
3. Implement DTOs with `zod`.
4. Run: `pnpm --filter @decisionatlas/schema test`
5. Run: `pnpm --filter @decisionatlas/schema typecheck`
6. Commit: `git commit -m "feat: add shared dto contracts"`

**Expected result:** Node services share stable request and response shapes.

### Task W2-4: Seed a demo workspace record

**Files:**
- Create: `examples/demo-workspace/workspace.json`
- Create: `services/engine/app/db/seed_demo.py`
- Create: `services/engine/tests/db/test_seed_demo.py`

**Steps:**
1. Write `services/engine/tests/db/test_seed_demo.py` to assert the seed script creates one workspace with a slug and repo URL.
2. Run: `uv run --project services/engine pytest services/engine/tests/db/test_seed_demo.py -q`
3. Implement `seed_demo.py`.
4. Run: `uv run --project services/engine pytest services/engine/tests/db/test_seed_demo.py -q`
5. Commit: `git commit -m "feat: add demo workspace seeding"`

**Expected result:** The project can always seed one known workspace for development and demo flows.

## Week 3: GitHub Ingestion

**Week goal:** Import issues, PRs, commits, and metadata from one public GitHub repository into `artifacts`.

**Exit criteria:**

- Demo repo imports without manual DB edits
- At least one issue, one PR, and one commit become artifacts
- GitHub importer tests pass without live API calls

### Task W3-1: Build the GitHub client abstraction

**Files:**
- Create: `services/engine/app/ingest/github_client.py`
- Create: `services/engine/app/ingest/github_types.py`
- Create: `services/engine/tests/ingest/test_github_client.py`

**Steps:**
1. Write tests for:
   - `fetch_issues`
   - `fetch_pull_requests`
   - `fetch_commits`
   - token-less public repo fallback
2. Run: `uv run --project services/engine pytest services/engine/tests/ingest/test_github_client.py -q`
3. Implement the GitHub HTTP client with pagination and retry logic.
4. Run: `uv run --project services/engine pytest services/engine/tests/ingest/test_github_client.py -q`
5. Commit: `git commit -m "feat: add github client abstraction"`

**Expected result:** GitHub access is encapsulated and fully mockable in tests.

### Task W3-2: Persist imported GitHub artifacts

**Files:**
- Create: `services/engine/app/ingest/github_importer.py`
- Create: `services/engine/app/repositories/artifacts.py`
- Create: `services/engine/tests/ingest/test_github_importer.py`

**Steps:**
1. Write tests asserting imported issues, PRs, and commits are stored as `artifacts` with:
   - `type`
   - `source_id`
   - `repo`
   - `title`
   - `content`
   - `author`
   - `url`
   - `timestamp`
2. Run: `uv run --project services/engine pytest services/engine/tests/ingest/test_github_importer.py -q`
3. Implement importer orchestration and repository persistence.
4. Run: `uv run --project services/engine pytest services/engine/tests/ingest/test_github_importer.py -q`
5. Commit: `git commit -m "feat: persist github artifacts"`

**Expected result:** GitHub content lands in the database with deterministic normalization.

### Task W3-3: Expose import jobs through the engine and API

**Files:**
- Create: `services/engine/app/api/imports.py`
- Create: `services/engine/app/jobs/import_jobs.py`
- Create: `apps/api/src/routes/imports.ts`
- Create: `apps/api/tests/imports-route.test.ts`
- Create: `services/engine/tests/api/test_imports.py`

**Steps:**
1. Write API tests for:
   - `POST /imports/github`
   - payload validation
   - response includes `job_id`
2. Run: `pnpm --filter @decisionatlas/api test`
3. Run: `uv run --project services/engine pytest services/engine/tests/api/test_imports.py -q`
4. Implement the route, job handoff, and engine endpoint.
5. Re-run both test suites.
6. Commit: `git commit -m "feat: add github import endpoints"`

**Expected result:** The frontend can trigger GitHub import through stable APIs.

## Week 4: Docs, Text Import, Chunking, And Indexing

**Week goal:** Support Markdown, ADR, plain text, and optional `pandoc`-backed document conversion, then produce chunked, indexed artifact content.

**Exit criteria:**

- Markdown and ADR files import from the repo clone or local folder
- Local text notes import through API
- Artifact chunks are stored with embeddings and FTS indexes

### Task W4-1: Implement Markdown and ADR import

**Files:**
- Create: `services/engine/app/ingest/markdown_importer.py`
- Create: `services/engine/app/ingest/file_discovery.py`
- Create: `services/engine/tests/ingest/test_markdown_importer.py`

**Steps:**
1. Write tests for:
   - nested markdown discovery
   - ADR directory import
   - frontmatter stripping
   - URL derivation for repo docs
2. Run: `uv run --project services/engine pytest services/engine/tests/ingest/test_markdown_importer.py -q`
3. Implement import logic and normalization rules.
4. Run: `uv run --project services/engine pytest services/engine/tests/ingest/test_markdown_importer.py -q`
5. Commit: `git commit -m "feat: add markdown and adr import"`

**Expected result:** Repository docs become `doc` artifacts without manual preprocessing.

### Task W4-2: Implement local text and optional `pandoc` import

**Files:**
- Create: `services/engine/app/ingest/text_importer.py`
- Create: `services/engine/app/ingest/pandoc_adapter.py`
- Create: `services/engine/tests/ingest/test_text_importer.py`
- Create: `services/engine/tests/ingest/test_pandoc_adapter.py`

**Steps:**
1. Write tests asserting:
   - plain `.txt` imports as `meeting_note`
   - `.md` local notes import unchanged
   - `pandoc` conversion is skipped gracefully when unavailable
   - `.docx` converts to markdown when `pandoc` exists
2. Run: `uv run --project services/engine pytest services/engine/tests/ingest/test_text_importer.py services/engine/tests/ingest/test_pandoc_adapter.py -q`
3. Implement the text importer and `pandoc` adapter.
4. Re-run the tests.
5. Commit: `git commit -m "feat: add text and pandoc-backed import"`

**Expected result:** The engine can import local notes and later accept `.docx` with the installed `pandoc`.

### Task W4-3: Add chunking, embeddings, and full-text indexing

**Files:**
- Create: `services/engine/app/indexing/chunker.py`
- Create: `services/engine/app/indexing/embedder.py`
- Create: `services/engine/app/indexing/index_artifact.py`
- Create: `services/engine/tests/indexing/test_chunker.py`
- Create: `services/engine/tests/indexing/test_index_artifact.py`

**Steps:**
1. Write tests for:
   - chunk boundaries preserve sentence order
   - empty content is skipped
   - repeated indexing is idempotent
   - embeddings are mocked in tests
2. Run: `uv run --project services/engine pytest services/engine/tests/indexing/test_chunker.py services/engine/tests/indexing/test_index_artifact.py -q`
3. Implement chunking, embedding abstraction, and FTS/vector persistence.
4. Re-run the tests.
5. Commit: `git commit -m "feat: add artifact chunking and indexing"`

**Expected result:** Every imported artifact can be searched by full text and vector similarity.

## Week 5: Candidate Decision Extraction

**Week goal:** Turn indexed artifacts into candidate decisions with structured fields and source references.

**Exit criteria:**

- Extraction runs on the seeded demo workspace
- Candidate decisions are stored with `review_state = candidate`
- All extraction tests use mocked model providers

### Task W5-1: Add provider-agnostic model interfaces

**Files:**
- Create: `services/engine/app/llm/base.py`
- Create: `services/engine/app/llm/openai_compatible.py`
- Create: `services/engine/app/llm/fake_provider.py`
- Create: `services/engine/tests/llm/test_fake_provider.py`

**Steps:**
1. Write tests asserting the fake provider returns deterministic extraction and embedding fixtures.
2. Run: `uv run --project services/engine pytest services/engine/tests/llm/test_fake_provider.py -q`
3. Implement the provider interface and fake provider.
4. Re-run the tests.
5. Commit: `git commit -m "feat: add provider abstraction"`

**Expected result:** Extraction and retrieval logic can be tested offline.

### Task W5-2: Implement extraction prompts and response parsing

**Files:**
- Create: `packages/prompts/decision-extraction.md`
- Create: `services/engine/app/extractor/prompt_loader.py`
- Create: `services/engine/app/extractor/parser.py`
- Create: `services/engine/tests/extractor/test_parser.py`

**Steps:**
1. Write tests asserting malformed LLM output is rejected and valid structured output maps to the required fields.
2. Run: `uv run --project services/engine pytest services/engine/tests/extractor/test_parser.py -q`
3. Implement prompt loading and response parsing.
4. Re-run the tests.
5. Commit: `git commit -m "feat: add decision extraction parsing"`

**Expected result:** The extraction boundary is explicit and resilient to model output noise.

### Task W5-3: Build the candidate extraction pipeline

**Files:**
- Create: `services/engine/app/extractor/pipeline.py`
- Create: `services/engine/app/repositories/decisions.py`
- Create: `services/engine/app/repositories/source_refs.py`
- Create: `services/engine/tests/extractor/test_pipeline.py`

**Steps:**
1. Write tests asserting the pipeline:
   - skips low-signal artifacts
   - creates one candidate decision from a valid source
   - creates `source_refs` with quote spans
   - stores `review_state = candidate`
2. Run: `uv run --project services/engine pytest services/engine/tests/extractor/test_pipeline.py -q`
3. Implement the extraction workflow.
4. Re-run the tests.
5. Commit: `git commit -m "feat: add candidate decision extraction pipeline"`

**Expected result:** The engine can populate a review queue from imported artifacts.

## Week 6: Review Queue And Decision Detail

**Week goal:** Let a human confirm, reject, or supersede extracted decisions and inspect the supporting evidence.

**Exit criteria:**

- Review queue works end-to-end
- Decision detail page renders quotes and sources
- Review actions persist correctly

### Task W6-1: Expose review queue APIs

**Files:**
- Create: `services/engine/app/api/decisions.py`
- Create: `apps/api/src/routes/decisions.ts`
- Create: `services/engine/tests/api/test_decisions_api.py`
- Create: `apps/api/tests/decisions-route.test.ts`

**Steps:**
1. Write tests for:
   - `GET /decisions?review_state=candidate`
   - `GET /decisions/:id`
   - `POST /decisions/:id/review`
2. Run: `uv run --project services/engine pytest services/engine/tests/api/test_decisions_api.py -q`
3. Run: `pnpm --filter @decisionatlas/api test`
4. Implement engine and API routes.
5. Re-run both test suites.
6. Commit: `git commit -m "feat: add review queue apis"`

**Expected result:** The UI has stable endpoints for review operations.

### Task W6-2: Build the review queue page

**Files:**
- Create: `apps/web/app/review/page.tsx`
- Create: `apps/web/components/review/review-list.tsx`
- Create: `apps/web/components/review/review-actions.tsx`
- Create: `apps/web/tests/review-page.test.tsx`

**Steps:**
1. Write `review-page.test.tsx` to assert candidates render with `Accept`, `Reject`, and `Supersede` controls.
2. Run: `pnpm --filter @decisionatlas/web test`
3. Implement the review page and controls.
4. Re-run the tests.
5. Commit: `git commit -m "feat: add review queue ui"`

**Expected result:** A reviewer can manage candidate decisions from the web app.

### Task W6-3: Build the decision detail page

**Files:**
- Create: `apps/web/app/decisions/[id]/page.tsx`
- Create: `apps/web/components/decisions/decision-card.tsx`
- Create: `apps/web/components/decisions/source-ref-list.tsx`
- Create: `apps/web/tests/decision-detail.test.tsx`

**Steps:**
1. Write tests asserting the page shows required fields, source quotes, and source URLs.
2. Run: `pnpm --filter @decisionatlas/web test`
3. Implement the detail page and source reference rendering.
4. Re-run the tests.
5. Commit: `git commit -m "feat: add decision detail page"`

**Expected result:** Accepted and candidate decisions are inspectable with evidence.

## Week 7: Hybrid Retrieval And Why Answering

**Week goal:** Support natural-language why queries over accepted decisions and supporting artifacts.

**Exit criteria:**

- Search can answer at least five seed why-questions
- Every answer includes 2-4 citations
- Retrieval tests pass with deterministic fixtures

### Task W7-1: Implement hybrid retrieval

**Files:**
- Create: `services/engine/app/retrieval/full_text.py`
- Create: `services/engine/app/retrieval/vector_search.py`
- Create: `services/engine/app/retrieval/hybrid.py`
- Create: `services/engine/tests/retrieval/test_hybrid.py`

**Steps:**
1. Write tests for:
   - full-text hit ranking
   - vector recall on paraphrased questions
   - merged ranking with deduplication
   - filtering by `workspace_id` and `review_state`
2. Run: `uv run --project services/engine pytest services/engine/tests/retrieval/test_hybrid.py -q`
3. Implement hybrid retrieval.
4. Re-run the tests.
5. Commit: `git commit -m "feat: add hybrid retrieval"`

**Expected result:** Search quality does not rely on a single retrieval strategy.

### Task W7-2: Implement citation-first answer assembly

**Files:**
- Create: `services/engine/app/retrieval/answering.py`
- Create: `services/engine/app/retrieval/query_rewrite.py`
- Create: `services/engine/tests/retrieval/test_answering.py`

**Steps:**
1. Write tests asserting:
   - answers fail closed when evidence is insufficient
   - answers include 2-4 citations
   - citations point to source refs, not raw guessed text
2. Run: `uv run --project services/engine pytest services/engine/tests/retrieval/test_answering.py -q`
3. Implement answer assembly and conservative fallback handling.
4. Re-run the tests.
5. Commit: `git commit -m "feat: add citation-first answering"`

**Expected result:** The system can say “insufficient evidence” instead of hallucinating.

### Task W7-3: Expose why-query APIs

**Files:**
- Create: `services/engine/app/api/query.py`
- Create: `apps/api/src/routes/query.ts`
- Create: `services/engine/tests/api/test_query_api.py`
- Create: `apps/api/tests/query-route.test.ts`

**Steps:**
1. Write tests for `POST /query/why`.
2. Run the engine and API test suites.
3. Implement the query routes.
4. Re-run the test suites.
5. Commit: `git commit -m "feat: add why query api"`

**Expected result:** The frontend can issue why-queries through a stable API contract.

## Week 8: Search UI, Timeline, And Workspace Dashboard

**Week goal:** Make the system usable from the browser for demo and evaluation.

**Exit criteria:**

- Search page, result page, timeline, and dashboard all render
- A new user can import the demo workspace and ask at least one seeded question

### Task W8-1: Build the why-search page

**Files:**
- Create: `apps/web/app/search/page.tsx`
- Create: `apps/web/components/search/query-form.tsx`
- Create: `apps/web/components/search/search-results.tsx`
- Create: `apps/web/tests/search-page.test.tsx`

**Steps:**
1. Write tests asserting the search page submits a question and renders the answer with citations.
2. Run: `pnpm --filter @decisionatlas/web test`
3. Implement the page and UI components.
4. Re-run the tests.
5. Commit: `git commit -m "feat: add why search ui"`

**Expected result:** Search is demoable without using API clients.

### Task W8-2: Build the decision timeline

**Files:**
- Create: `apps/web/app/timeline/page.tsx`
- Create: `apps/web/components/timeline/timeline-list.tsx`
- Create: `apps/web/tests/timeline-page.test.tsx`

**Steps:**
1. Write tests asserting accepted decisions are sorted chronologically and grouped by date.
2. Run: `pnpm --filter @decisionatlas/web test`
3. Implement the timeline page.
4. Re-run the tests.
5. Commit: `git commit -m "feat: add decision timeline ui"`

**Expected result:** Reviewers can see decision evolution over time.

### Task W8-3: Build the workspace dashboard

**Files:**
- Create: `apps/web/app/workspaces/[slug]/page.tsx`
- Create: `apps/web/components/dashboard/kpi-strip.tsx`
- Create: `apps/web/components/dashboard/recent-alerts.tsx`
- Create: `apps/web/tests/workspace-dashboard.test.tsx`

**Steps:**
1. Write tests asserting the dashboard shows import status, decision counts, and recent alerts.
2. Run: `pnpm --filter @decisionatlas/web test`
3. Implement the dashboard page.
4. Re-run the tests.
5. Commit: `git commit -m "feat: add workspace dashboard"`

**Expected result:** The demo has a visible home surface, not just isolated pages.

## Week 9: Rule-First Drift Detection

**Week goal:** Add the first real differentiator: rules derived from accepted decisions and enforced against new artifacts.

**Exit criteria:**

- At least one drift rule type runs end-to-end
- Alerts are persisted and viewable
- False positives are surfaced as `possible_drift`

### Task W9-1: Define the drift rule model

**Files:**
- Create: `services/engine/app/drift/rule_types.py`
- Create: `services/engine/app/drift/rule_extractor.py`
- Create: `services/engine/tests/drift/test_rule_extractor.py`

**Steps:**
1. Write tests for extracting a structured rule from an accepted decision with machine-checkable constraints.
2. Run: `uv run --project services/engine pytest services/engine/tests/drift/test_rule_extractor.py -q`
3. Implement rule extraction for one concrete rule family, such as “PR must reference Decision ID” or “Redis is cache-only”.
4. Re-run the tests.
5. Commit: `git commit -m "feat: add drift rule extraction"`

**Expected result:** Accepted decisions can produce explicit rule objects.

### Task W9-2: Implement rule evaluation against new artifacts

**Files:**
- Create: `services/engine/app/drift/rules.py`
- Create: `services/engine/app/drift/evaluator.py`
- Create: `services/engine/tests/drift/test_evaluator.py`

**Steps:**
1. Write tests asserting a violating artifact produces a `possible_drift` alert with evidence.
2. Run: `uv run --project services/engine pytest services/engine/tests/drift/test_evaluator.py -q`
3. Implement the evaluator.
4. Re-run the tests.
5. Commit: `git commit -m "feat: add rule drift evaluator"`

**Expected result:** The engine can detect one real drift pattern.

### Task W9-3: Expose drift alerts in API and UI

**Files:**
- Create: `services/engine/app/api/drift.py`
- Create: `apps/api/src/routes/drift.ts`
- Create: `apps/web/app/drift/page.tsx`
- Create: `apps/web/tests/drift-page.test.tsx`

**Steps:**
1. Write route and UI tests for listing persisted alerts.
2. Run the relevant API, engine, and web tests.
3. Implement the drift routes and page.
4. Re-run the tests.
5. Commit: `git commit -m "feat: add drift alerts page"`

**Expected result:** Drift is visible from the browser and can be demonstrated.

## Week 10: Semantic Drift Enrichment

**Week goal:** Add a semantic layer that recalls similar past decisions when a new artifact may supersede or conflict with them.

**Exit criteria:**

- Semantic drift checks run only after rule checks
- Alerts are labeled `possible_supersession` or `needs_review`
- The semantic layer is conservative and test-backed

### Task W10-1: Add semantic candidate recall

**Files:**
- Create: `services/engine/app/drift/semantic_recall.py`
- Create: `services/engine/tests/drift/test_semantic_recall.py`

**Steps:**
1. Write tests asserting semantically similar artifacts retrieve related accepted decisions.
2. Run: `uv run --project services/engine pytest services/engine/tests/drift/test_semantic_recall.py -q`
3. Implement semantic recall using the existing hybrid retrieval stack.
4. Re-run the tests.
5. Commit: `git commit -m "feat: add semantic drift recall"`

**Expected result:** The engine can find historically related decisions beyond explicit rules.

### Task W10-2: Add semantic drift classification

**Files:**
- Create: `services/engine/app/drift/semantic_classifier.py`
- Create: `services/engine/tests/drift/test_semantic_classifier.py`

**Steps:**
1. Write tests asserting the classifier only emits:
   - `possible_supersession`
   - `needs_review`
   - no alert
2. Run: `uv run --project services/engine pytest services/engine/tests/drift/test_semantic_classifier.py -q`
3. Implement the conservative classifier.
4. Re-run the tests.
5. Commit: `git commit -m "feat: add semantic drift classifier"`

**Expected result:** Semantic drift adds coverage without pretending to be certain.

### Task W10-3: Show semantic context in alert detail

**Files:**
- Modify: `apps/web/app/drift/page.tsx`
- Create: `apps/web/components/drift/alert-detail.tsx`
- Create: `apps/web/tests/drift-detail.test.tsx`

**Steps:**
1. Write UI tests asserting the alert detail page shows the triggering artifact, matched decision, and confidence label.
2. Run: `pnpm --filter @decisionatlas/web test`
3. Implement the detail component.
4. Re-run the tests.
5. Commit: `git commit -m "feat: show semantic drift context"`

**Expected result:** Alert consumers can inspect why the engine flagged a semantic mismatch.

## Week 11: Demo Hardening, Benchmarks, And Observability

**Week goal:** Make the project trustworthy to try, evaluate, and debug.

**Exit criteria:**

- Demo workspace seeds reliably
- Benchmark fixtures exist
- Basic logs and metrics exist
- Playwright smoke flow passes

### Task W11-1: Create benchmark fixtures and evaluation script

**Files:**
- Create: `examples/demo-workspace/queries.json`
- Create: `examples/demo-workspace/expected-answers.json`
- Create: `scripts/ci/run_benchmark.py`
- Create: `services/engine/tests/evals/test_benchmark_fixtures.py`

**Steps:**
1. Write tests asserting the benchmark fixtures have matching IDs, queries, and expected citation counts.
2. Run: `uv run --project services/engine pytest services/engine/tests/evals/test_benchmark_fixtures.py -q`
3. Implement the benchmark runner.
4. Re-run the tests.
5. Commit: `git commit -m "feat: add benchmark fixtures and runner"`

**Expected result:** Search quality can be regression-tested before release.

### Task W11-2: Add structured logging and job observability

**Files:**
- Create: `services/engine/app/observability/logging.py`
- Create: `apps/api/src/plugins/logging.ts`
- Create: `services/engine/tests/observability/test_logging.py`
- Create: `apps/api/tests/logging.test.ts`

**Steps:**
1. Write tests asserting logs include `workspace_id`, `job_id`, and `artifact_id` where applicable.
2. Run the engine and API logging tests.
3. Implement structured logging.
4. Re-run the tests.
5. Commit: `git commit -m "feat: add structured logging"`

**Expected result:** Import, extraction, and drift jobs are debuggable without manual print statements.

### Task W11-3: Add end-to-end browser smoke coverage

**Files:**
- Create: `apps/web/playwright.config.ts`
- Create: `apps/web/tests-e2e/demo-smoke.spec.ts`
- Create: `scripts/ci/run_demo_smoke.ps1`

**Steps:**
1. Write a Playwright spec that:
   - opens the dashboard
   - triggers a demo import
   - opens the review queue
   - runs one why-query
   - opens the drift page
2. Run: `pnpm --filter @decisionatlas/web exec playwright test`
3. Implement the minimum wiring needed to make the smoke flow pass.
4. Re-run the smoke suite.
5. Commit: `git commit -m "test: add demo browser smoke coverage"`

**Expected result:** The demo path is guarded by automation.

## Week 12: Release Packaging And Launch Materials

**Week goal:** Ship a usable open-source release with clear setup, security posture, and demo narrative.

**Exit criteria:**

- Quick start works from a clean machine
- README explains value in under one screen
- Release checklist is complete

### Task W12-1: Write the release-grade README and quick start

**Files:**
- Modify: `README.md`
- Create: `docs/project/quick-start.md`
- Create: `docs/project/demo-script.md`
- Create: `docs/project/faq.md`

**Steps:**
1. Write the README sections in this order:
   - one-sentence value prop
   - five example why-questions
   - architecture snapshot
   - quick start
   - screenshots or placeholders
2. Write `quick-start.md` with exact setup commands.
3. Write `demo-script.md` for a 60-90 second walkthrough.
4. Run: `rg "DecisionAtlas|Quick Start|Why" README.md docs/project`
5. Commit: `git commit -m "docs: add release-ready project documentation"`

**Expected result:** A stranger can understand and run the project without a guided call.

### Task W12-2: Add open-source trust files

**Files:**
- Create: `LICENSE`
- Create: `SECURITY.md`
- Create: `CODEOWNERS`
- Create: `.github/ISSUE_TEMPLATE/bug_report.md`
- Create: `.github/ISSUE_TEMPLATE/feature_request.md`
- Create: `.github/pull_request_template.md`

**Steps:**
1. Add the trust and contribution files.
2. Run: `rg "Security|bug|feature" .github SECURITY.md`
3. Commit: `git commit -m "chore: add open source community files"`

**Expected result:** The repo looks maintained and contribution-ready.

### Task W12-3: Add release checklist and tag process

**Files:**
- Create: `docs/project/release-checklist.md`
- Create: `scripts/ci/pre-release.ps1`
- Create: `.github/workflows/ci.yml`

**Steps:**
1. Write `release-checklist.md` covering setup, tests, demo, docs, and known limitations.
2. Add a CI workflow that runs:
   - Node tests
   - Python tests
   - Playwright smoke
3. Add `pre-release.ps1` to run all local checks in one command.
4. Run: `pnpm test`
5. Run: `uv run --project services/engine pytest -q`
6. Commit: `git commit -m "chore: add release process and ci"`

**Expected result:** The project has a repeatable release gate before public launch.

## Weekly Owner Checkpoints

At the end of each week, the owner only needs to answer these:

- Week 1: confirm repo name, demo repo, provider
- Week 2: confirm required Decision fields and DB naming
- Week 3: confirm imported GitHub object scope
- Week 4: confirm whether `.docx` import is in MVP or optional
- Week 5: confirm extraction output format
- Week 6: confirm review workflow labels
- Week 7: confirm answer style and evidence threshold
- Week 8: confirm dashboard and page order
- Week 9: confirm first rule family for drift
- Week 10: confirm semantic alert labels
- Week 11: confirm benchmark questions
- Week 12: confirm launch copy and release timing

## Commands Expected To Work By The End

```powershell
pnpm install
pnpm test
pnpm --filter @decisionatlas/web dev
pnpm --filter @decisionatlas/api dev
uv sync --project services/engine
uv run --project services/engine alembic upgrade head
uv run --project services/engine pytest -q
docker compose up -d
```

## Definition Of Done For MVP

The MVP is done only when all of the following are true:

- One public repository imports cleanly
- Docs and notes import cleanly
- Candidate decisions are created and reviewable
- At least five why-questions return answers with citations
- At least one drift rule produces useful alerts
- A new user can run the demo in under five minutes
- CI passes without live provider credentials

Plan complete and saved to `docs/plans/2026-03-18-decisionatlas-implementation-plan.md`. Two execution options:

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

Which approach?
