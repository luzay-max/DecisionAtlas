# 2026-03-18 Progress Log

## Summary

Today the project moved from the finished Week 12 MVP into three delivered slices of `v0.2` public-demo hardening.

Completed scope:

- Week 1: monorepo, web shell, API shell, engine shell, ADRs
- Week 2: local infra, database schema, demo workspace seed
- Week 3: GitHub import pipeline and API
- Week 4: markdown/text/docx import, chunking, indexing
- Week 5: candidate decision extraction pipeline
- Week 6: review queue API and UI
- Week 7: why-query retrieval and citation-first answering
- Week 8: search page, timeline, workspace dashboard
- Week 9: first rule-first drift detection flow
- Week 10: semantic drift enrichment and conservative classifier
- Week 11: benchmark fixtures, structured logging, browser smoke flow
- Week 12: README, quick start, release checklist, GitHub community files, CI workflow
- v0.2 slice 1: configurable live provider runtime, persisted import jobs, incremental GitHub import, demo-focused UI and docs
- v0.2 slice 2: benchmark alignment for the curated demo repo, one-command local bring-up, retrieval ranking cleanup, and updated smoke coverage
- v0.2 slice 3: workspace-aware navigation, direct detail links, and smoother page-to-page demo routing

## Commits Pushed Today

- `009920f` `feat: bootstrap DecisionAtlas MVP foundation`
- `2eb537e` `feat: add review queue and why-query foundations`
- `219c304` `feat: add workspace timeline and dashboard views`
- `231639f` `feat: add rule-first drift detection`
- `40b3260` `feat: add semantic drift enrichment`
- `61ac692` `feat: add benchmark and smoke validation`
- `f559573` `docs: add release packaging and ci`
- `9574c30` `fix: use uv cli in ci workflow`
- `ab42f23` `feat: start v0.2 demo hardening`
- `f59552e` `feat: improve demo experience flow`
- `5ea5fbe` `feat: align demo benchmark and one-click startup`
- `4789676` `feat: improve workspace navigation flow`

Remote status:

- `origin/main` is at `4789676`
- GitHub repo: `https://github.com/luzay-max/DecisionAtlas.git`

## Functional State

The current build can:

- import GitHub artifacts into the database
- import markdown, ADR, text, and optional docx content
- chunk and index artifacts
- extract candidate decisions with source refs
- review candidate decisions in the browser
- answer why-questions with citations
- show accepted decision timeline and workspace KPIs
- detect rule-first drift and add semantic drift enrichment
- run benchmark validation and browser smoke automation
- switch between fake-provider mode and OpenAI-compatible live provider mode
- persist import jobs with `full` and `since_last_sync` modes
- expose import job status through engine, API, and dashboard
- run import -> index -> candidate extraction in one GitHub import job
- prepare a local demo environment with `scripts/dev/prepare-demo.ps1`
- start and stop an isolated local demo stack with:
  - `scripts/dev/start-demo-stack.ps1`
  - `scripts/dev/stop-demo-stack.ps1`
- validate the curated demo workspace against fixture and live benchmarks
- preserve workspace context across dashboard, review, search, timeline, drift, and decision detail pages

## v0.2 Work Completed

### Provider runtime

- Added configurable provider settings:
  - `LLM_PROVIDER_MODE`
  - `LLM_API_KEY`
  - `EMBEDDING_API_KEY`
  - `LLM_BASE_URL`
  - `LLM_MODEL`
  - `EMBEDDING_MODEL`
  - `LLM_TIMEOUT_SECONDS`
- Added runtime provider selection with fake/live fallback
- Added explicit provider errors for configuration, timeout, rate limit, request, and response failures
- Wired the runtime into why-query and semantic drift evaluation

### Import hardening

- Added `import_jobs` persistence and migration
- Added GitHub import `mode` support:
  - `full`
  - `since_last_sync`
- Added `GET /imports/:jobId`
- Dashboard now shows the configured demo repo and latest import state
- Import jobs now continue through indexing and candidate extraction
- Candidate extraction now skips already-linked artifacts to reduce duplicate candidates on reruns

### Demo experience

- Homepage now explains the 3-step public demo path
- Review queue now surfaces high-confidence candidates first
- Search page now includes example questions, better empty states, and failure messaging
- Drift page empty state now tells the user what to do next
- Added local demo preparation script:
  - `scripts/dev/prepare-demo.ps1`
- Demo workspace and curated benchmark fixtures now default to:
  - `https://github.com/encode/httpx`

### Demo hardening follow-up

- Added one-command local operator scripts:
  - `scripts/dev/start-demo-stack.ps1`
  - `scripts/dev/stop-demo-stack.ps1`
- The one-command demo flow now uses an isolated SQLite database under `.tmp/`
  so the curated demo is reproducible even when local Docker/PostgreSQL state is dirty
- Updated smoke seed data to cover:
  - Redis cache-only rationale
  - PostgreSQL as source of truth
  - queueing long-running jobs
  - human review before acceptance
  - one candidate decision and one drift alert
- Updated benchmark/example questions to match the curated demo data
- Tightened retrieval ranking by filtering stopword noise from full-text scoring
- Tightened answer assembly so weak secondary hits do not pollute why-answers
- Updated Playwright smoke expectations to match the new curated demo content

### Routing and navigation polish

- Added a shared workspace navigation bar across:
  - dashboard
  - review
  - search
  - timeline
  - drift
  - decision detail
- Added direct quick links from the dashboard into review, why search, timeline, and drift
- Preserved workspace context in route transitions with `?workspace=<slug>`
- Added direct links from:
  - review candidates to decision detail
  - timeline entries to decision detail
  - drift alerts to matched decision detail
- Added homepage jump links so the demo path is reachable in one click from the landing page

### Docs and release direction

- Added:
  - `docs/project/deployment.md`
  - `docs/project/release-notes-v0.2.md`
  - `docs/plans/2026-03-18-decisionatlas-v0.2-implementation-plan.md`
  - `docs/plans/2026-03-18-decisionatlas-v0.3-backlog.md`
- Updated `README.md`, `quick-start.md`, and `demo-script.md` to reflect the v0.2 demo path

## CI Follow-Up

After the Week 12 push, GitHub Actions failed in `Sync engine environment` on Windows with:

- `python.exe: No module named uv`

Root cause:

- `astral-sh/setup-uv` installs the `uv` CLI on `PATH`
- the workflow incorrectly called `python -m uv ...`, which requires a Python package install that is not present on the runner

Fix applied locally:

- CI now uses `uv sync --project services/engine`
- engine tests now use `uv run pytest -q`
- release and smoke scripts were updated to use `uv run ...`
- setup docs now match the actual CLI usage instead of recommending `python -m uv ...`

## Verification Run

Latest verification status after the current v0.2 work:

- `python -m uv run pytest -q` in `services/engine`: `56 passed`
- `pnpm test`: passed
- `pnpm typecheck`: passed
- `python scripts/ci/run_benchmark.py`: passed
- `python scripts/ci/run_benchmark.py --live --base-url http://127.0.0.1:3001 --workspace-slug demo-workspace`: passed
- `pnpm --filter @decisionatlas/web exec playwright test`: passed
- `powershell -ExecutionPolicy Bypass -File .\scripts\dev\prepare-demo.ps1`: passed
- `powershell -ExecutionPolicy Bypass -File .\scripts\dev\start-demo-stack.ps1`: passed
- `pnpm --filter @decisionatlas/web test`: passed after the routing/navigation updates
- `pnpm --filter @decisionatlas/web typecheck`: passed after the routing/navigation updates

## Known Current State

- Docker is working locally for `postgres` and `redis`
- the repo is committed and pushed through the benchmark-alignment and one-click bring-up slice
- local-only research and tooling folders remain intentionally untracked

Untracked local-only files and folders:

- `.codex/`
- `openspec/`
- `1.txt`
- `github_open_source_project_research_report_zh_final.docx`

## Recommended Next Step

Continue v0.2 with the still-open items:

- add stronger import failure summaries for markdown/text/docx paths
- prepare one hosted public demo environment
- finish live-provider validation with a non-fake model path once local credentials are configured safely

## Stop Point

Development is now inside `v0.2` rather than the original 12-week MVP plan.

The current stop point is:

- provider runtime delivered
- import job persistence delivered
- demo UX improved
- local demo preparation path verified
- curated benchmark/live benchmark aligned to `encode/httpx`
- one-command local bring-up verified
- workspace-aware route jumps verified in the web test suite

The next implementation slice should focus on benchmark calibration and hosted demo bring-up.

## 2026-03-20 Addendum

Today added a lightweight bilingual UI layer to the web app:

- Introduced a shared client-side language provider with persisted `en` / `zh` selection
- Added a visible language toggle in the home page and workspace navigation
- Localized the main demo path:
  - homepage
  - workspace dashboard
  - review queue
  - why search
  - timeline
  - drift alerts
  - decision detail
- Localized the primary action buttons and helper text used in the demo flow
- Made timeline dates follow the active UI language
- Added a regression test that verifies the homepage switches to Chinese and updates `html lang`

Verification for this addendum:

- `pnpm --filter @decisionatlas/web test`: passed
- `pnpm --filter @decisionatlas/web typecheck`: passed
- `pnpm --filter @decisionatlas/web exec playwright test`: passed

Current status after this addendum:

- the demo path now supports an English/Chinese UI toggle without changing API payloads
- the switch is persistent in the browser via localStorage
- the default demo flow still opens in English, so existing demo scripts remain valid

## 2026-03-20 Provenance Addendum

Today also completed the `clarify-demo-vs-live-data` implementation slice on branch `feat/clarify-demo-vs-live-data`.

Delivered:

- added workspace-level provenance classification in the engine:
  - `demo`
  - `imported`
  - `mixed`
- extended these backend responses with provenance summary fields:
  - dashboard summary
  - why query
  - timeline
  - drift alerts
  - decision detail
- added a shared provenance banner to trust-sensitive web surfaces:
  - dashboard
  - why search results
  - timeline
  - drift
  - decision detail
- updated homepage and demo script copy so seeded walkthrough behavior is explicitly distinguished from imported repository behavior
- updated engine, API proxy, and web tests to validate the new provenance behavior

Verification for this addendum:

- `python -m uv run pytest tests/test_provenance.py tests/api/test_timeline_dashboard_api.py tests/api/test_query_api.py tests/api/test_drift_api.py tests/api/test_decisions_api.py -q`: passed
- `pnpm --filter @decisionatlas/api test`: passed
- `pnpm --filter @decisionatlas/web test`: passed
- `pnpm --filter @decisionatlas/web typecheck`: passed

Current status after this addendum:

- demo-facing pages now explain whether the user is seeing seeded walkthrough data or imported repository data
- the timeline, why search, drift page, and decision detail no longer imply that seeded demo content is live repository output
- the project is ready to keep building on this branch or merge the provenance slice once reviewed

Compatibility follow-up:

- added defensive web compatibility handling for legacy API shapes during local development and hot reload cycles
- why search no longer crashes if `answer_context` is temporarily absent
- timeline no longer crashes if it still receives a legacy array response
- drift no longer crashes if it still receives a legacy array response
