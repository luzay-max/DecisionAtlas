## Why

The master plan still describes Stage 4 as in progress and references an older baseline after `prototype-governance-markdown-ingest` was completed, synced, archived, committed, and pushed. This makes the project roadmap stale and can mislead the next OpenSpec change selection.

## What Changes

- Update the master plan baseline to `main` @ `aec6e1a`.
- Record active OpenSpec changes as `0`.
- Mark Stage 4 Markdown Governance Ingest MVP as complete.
- Mark Stage 5 Governance Diff Checker as the next phase.
- Preserve the existing scope boundaries: Stage 4 created the governance knowledge layer, but AI diff checking and enforcement remain Stage 5+ work.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `release-baseline-validation`: Keep release/roadmap-facing documentation aligned with the current committed stage and next planned phase.

## Impact

- Documentation-only update to `docs/plans/2026-04-29-decisionatlas-next-master-plan.md`.
- No runtime, schema, API, UI, or database behavior changes.
