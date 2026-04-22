## Why

Imported public repositories now expose honest readiness states such as `review_ready`, `evidence_limited`, and `conversion_limited`, but some runs still stop after screening in enough high-signal evidence without producing reviewable candidate decisions. The next slice should reduce that screened-in-to-candidate bottleneck so more real repositories reach a trustworthy first review step instead of only a well-explained stall.

## What Changes

- Improve imported candidate conversion for screened-in artifacts so more high-signal repository evidence becomes grounded, reviewable candidate decisions.
- Tighten extraction routing and conversion diagnostics around the screened-in-to-candidate path instead of broadening ingest or weakening candidate quality thresholds.
- Preserve imported readiness semantics while shifting selected benchmark repositories from repeated `conversion_limited` outcomes toward `review_ready` when the repository already contains enough high-signal rationale.
- Extend lightweight real-repo benchmarks so candidate-conversion expectations are protected alongside the existing why and drift regression cases.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `decision-extraction-conversion`: strengthen how screened-in imported artifacts become grounded candidate decisions without relaxing candidate trust boundaries.
- `real-repository-outcomes`: refine the conditions under which imported workspaces should move from `conversion_limited` to `review_ready` as candidate conversion improves on real repositories.
- `lightweight-real-repo-benchmarks`: capture candidate-conversion expectations for curated repositories so real-lane improvements are regression-protected.

## Impact

- `services/engine`: extraction pipeline routing, candidate conversion diagnostics, and benchmark-facing import outcome behavior
- `apps/api`: imported-workspace summaries only where conversion changes affect exposed readiness or outcome payloads
- `apps/web`: imported workspace dashboard and search surfaces only where improved conversion changes the product state users see
- fixtures and docs: `examples/live-benchmarks/` and real-repository validation guidance
