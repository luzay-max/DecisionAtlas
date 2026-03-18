# 2026-03-18 Progress Log

## Summary

Today the project moved from planning into a working MVP foundation with browser-visible flows.

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

## Commits Pushed Today

- `009920f` `feat: bootstrap DecisionAtlas MVP foundation`
- `2eb537e` `feat: add review queue and why-query foundations`
- `219c304` `feat: add workspace timeline and dashboard views`
- `231639f` `feat: add rule-first drift detection`

Remote status:

- `origin/main` is at `231639f`
- GitHub repo: `https://github.com/luzay-max/DecisionAtlas.git`

## Functional State

The current build can:

- import GitHub artifacts into the database
- import markdown, ADR, text, and optional docx content
- chunk and index artifacts
- extract candidate decisions with source refs
- review candidate decisions in the browser
- answer why-questions with citations
- show an accepted decision timeline
- show workspace KPIs and recent alerts
- detect one conservative drift rule family and persist `possible_drift` alerts

## Drift Rule Implemented

The first drift rule family is intentionally narrow and explainable:

- accepted decisions that say Redis is `cache-only` produce a machine-checkable rule
- new artifacts are scanned for text suggesting Redis is being used as a primary or persistent store
- matches create persisted `possible_drift` alerts

This is implemented in:

- `services/engine/app/drift/rule_extractor.py`
- `services/engine/app/drift/evaluator.py`
- `services/engine/app/api/drift.py`
- `apps/web/app/drift/page.tsx`

## Verification Run

Final verification status before stopping:

- `python -m uv run pytest -q` in `services/engine`: `38 passed`
- `pnpm test`: passed
- `pnpm typecheck`: passed

## Known Current State

- Docker is working locally for `postgres` and `redis`
- the project is in a clean committed state except for two intentionally untracked local research files
- those files were not pushed to GitHub

Untracked local-only files:

- `1.txt`
- `github_open_source_project_research_report_zh_final.docx`

## Recommended Next Step

Resume at Week 10:

- add semantic drift candidate recall
- add conservative semantic alert labels such as `possible_supersession` and `needs_review`
- extend the drift page to show semantic context in alert detail

## Stop Point

Development stopped after Week 9 completion and successful push to `origin/main`.
