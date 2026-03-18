# 2026-03-18 Progress Log

## Summary

Today the project moved from the finished Week 12 MVP into the first delivered slice of `v0.2` public-demo hardening.

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

Remote status:

- `origin/main` is at `f59552e`
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
- Demo workspace now defaults to:
  - `https://github.com/openai/openai-cookbook`

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

Latest verification status after the v0.2 slice landed:

- `python -m uv run pytest -q` in `services/engine`: `54 passed`
- `pnpm test`: passed
- `pnpm typecheck`: passed
- `python scripts/ci/run_benchmark.py`: passed
- `pnpm --filter @decisionatlas/web exec playwright test`: passed
- `powershell -ExecutionPolicy Bypass -File .\scripts\dev\prepare-demo.ps1`: passed

## Known Current State

- Docker is working locally for `postgres` and `redis`
- the repo is committed and pushed through the first v0.2 demo-hardening slice
- local-only research and tooling folders remain intentionally untracked

Untracked local-only files and folders:

- `.codex/`
- `openspec/`
- `1.txt`
- `github_open_source_project_research_report_zh_final.docx`

## Recommended Next Step

Continue v0.2 with the still-open items:

- calibrate benchmark fixtures and example questions against the real demo repo import
- add stronger import failure summaries for markdown/text/docx paths
- make deployment more turnkey than documentation alone
- prepare one hosted public demo environment

## Stop Point

Development is now inside `v0.2` rather than the original 12-week MVP plan.

The current stop point is:

- provider runtime delivered
- import job persistence delivered
- demo UX improved
- local demo preparation path verified

The next implementation slice should focus on benchmark calibration and hosted demo bring-up.
