# 2026-03-23 Update Log

## Summary

Today the project moved out of guided-demo hardening and into a more credible real-repository analysis lane.

The main result is:

- `strengthen-real-repository-outcomes` was implemented and archived
- imported workspaces now expose stronger readiness, why-answer, and drift states
- real import progress is easier to understand during long extraction runs
- local startup guidance is now clearly split between:
  - the stable SQLite demo lane
  - the Docker-backed real-analysis lane

## Delivered Today

### 1. Real repository outcome hardening

Completed and archived the `strengthen-real-repository-outcomes` change.

Delivered scope:

- expanded high-signal repository markdown selection toward:
  - migration
  - rollout
  - operations
  - architecture
  - release
  - deprecation
- improved imported workspace evidence summaries so downstream usefulness is more explainable
- added imported workspace readiness and next-action signals
- tightened why-answer behavior so imported why-search requires accepted grounding
- improved imported drift usability with explicit evaluation states and manual evaluation flow

### 2. Extraction failure handling and progress visibility

Improved long-running real imports in two ways:

- extraction provider `400` responses no longer fail the whole import job
- extraction provider timeouts no longer fail the whole import job

Added extraction progress details to the import UI:

- processed extraction artifacts
- total extraction artifacts
- estimated remaining time
- current artifact title

This makes it easier to distinguish:

- real progress
- slow progress
- true failure

instead of leaving the user stuck at a generic `75%` stage marker.

### 3. Why / indexing / extraction optimization documentation

Created and expanded an optimization guide for future work:

- [indexing-optimization-guide.md](./indexing-optimization-guide.md)

The guide now covers:

- current indexing behavior
- indexing optimization backlog
- decision extraction performance bottlenecks
- why-search implementation and optimization directions

The intent is to keep one running markdown document where future optimization ideas can accumulate instead of scattering them across chats and ad hoc notes.

### 4. OpenSpec closure

Archived:

- `openspec/changes/archive/2026-03-23-strengthen-real-repository-outcomes/`

Synced main specs:

- `live-repository-analysis`
- `repository-document-ingest`
- `real-repository-outcomes`

OpenSpec status after this update:

- no active changes remain

### 5. Local runtime path clarification

Clarified the practical local operating model:

- `scripts/dev/start-demo-stack.ps1`
  - stable guided demo
  - SQLite
  - fake providers
- manual Docker-backed startup
  - real repository analysis
  - PostgreSQL + Redis
  - live provider configuration from `.env`

This resolves the earlier confusion where SQLite demo startup, local Postgres, and Docker Postgres were being mixed together.

## Verification

Verified today:

- `services/engine/.venv/Scripts/python -m pytest tests/extractor/test_pipeline.py tests/test_import_jobs.py -q`
- `pnpm --filter @decisionatlas/web test -- demo-import-button`
- `pnpm --filter @decisionatlas/web typecheck`
- Docker `postgres` and `redis` health
- live local stack health:
  - `http://127.0.0.1:8000/health`
  - `http://127.0.0.1:3001/health`
  - `http://127.0.0.1:3000`

## Current Project State

The project is now best described as:

- guided demo lane complete and stable
- real repository lane materially stronger, but still experimental
- no active OpenSpec change
- ready for either:
  - another real-functionality slice
  - release / push / external validation work

## Recommended Next Step

The most sensible next step is not another broad feature pass.

It should be one of:

1. push the current repository state and validate real imports on a few benchmark repositories
2. start a focused change for extraction throughput and observability
3. start a focused change for why-search retrieval quality on imported workspaces
