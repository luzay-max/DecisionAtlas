# 2026-03-18 Progress Log

## Summary

Today the project moved from planning to a full Week 12 MVP build with local verification, browser smoke coverage, and release packaging.

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

## Commits Pushed Today

- `009920f` `feat: bootstrap DecisionAtlas MVP foundation`
- `2eb537e` `feat: add review queue and why-query foundations`
- `219c304` `feat: add workspace timeline and dashboard views`
- `231639f` `feat: add rule-first drift detection`
- `40b3260` `feat: add semantic drift enrichment`
- `61ac692` `feat: add benchmark and smoke validation`
- `f559573` `docs: add release packaging and ci`

Remote status:

- `origin/main` is at `f559573`
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

Latest verification status before the CI fix push:

- `python -m uv run pytest -q` in `services/engine`: `46 passed`
- `pnpm test`: passed
- `pnpm typecheck`: passed
- `python scripts/ci/run_benchmark.py`: passed
- `pnpm --filter @decisionatlas/web exec playwright test`: passed

## Known Current State

- Docker is working locally for `postgres` and `redis`
- the repo is committed and pushed through Week 12
- local-only research and tooling folders remain intentionally untracked

Untracked local-only files and folders:

- `.codex/`
- `openspec/`
- `1.txt`
- `github_open_source_project_research_report_zh_final.docx`

## Recommended Next Step

After the CI fix is pushed and green:

- start `v0.2` with real model provider credentials
- add GitHub App auth for production-style imports
- add deployment config for a hosted demo

## Stop Point

Development reached the end of the 12-week MVP plan. The next phase starts after CI is green again.
