## Why

DecisionAtlas can now generate release evidence, hosted readiness evidence, and real-repo benchmark comparison reports, but those artifacts still live as one-off `.tmp` outputs. This change makes readiness evidence durable across dates and versions so release, hosted preview, and benchmark trends can be compared without relying on chat history or stale temporary files.

## What Changes

- Add a local readiness evidence history workflow that stores selected evidence bundles under a dated/versioned history directory.
- Preserve release evidence JSON/Markdown, hosted readiness JSON/Markdown, and real-repo benchmark comparison JSON/Markdown as linked evidence sets.
- Generate a compact history index that records evidence id, generated date, source paths, commit/version label, statuses, warnings, blockers, and benchmark movement counts.
- Add a trend/summary command that compares recent evidence entries and highlights changes in release status, hosted readiness status, and benchmark regression/blocker counts.
- Keep `.tmp` as the scratch output location; only explicit archive/history commands should copy evidence into durable project history.
- Do not make live hosted checks, live benchmarks, or CI enforcement automatic.

## Capabilities

### New Capabilities

- `readiness-evidence-history`: durable dated/versioned readiness evidence storage, index generation, and trend summary for release evidence, hosted readiness, and benchmark comparison artifacts.

### Modified Capabilities

- `release-evidence-automation`: generated release evidence can be archived into readiness evidence history with status and source metadata.
- `hosted-operator-delivery-readiness`: generated hosted readiness evidence can be archived into readiness evidence history and included in trend summaries.
- `lightweight-real-repo-benchmarks`: real-repo benchmark comparison output can be referenced as durable trend evidence.

## Impact

- New or extended local script under `scripts/ci/` or `scripts/demo/` for archiving evidence and producing trend summaries.
- New durable evidence directory convention, likely under `docs/evidence/readiness/` or `docs/project/evidence/`.
- Tests for evidence archive validation, index generation, trend summary behavior, missing file handling, and non-mutating defaults.
- Documentation updates in release checklist, hosted readiness docs, and real-repository validation docs.
- No database migration, no runtime API changes, no hosted dashboard, and no default CI/live-network enforcement.
