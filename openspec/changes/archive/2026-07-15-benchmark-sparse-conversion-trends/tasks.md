## 1. Sparse Metric Contract

- [x] 1.1 Extend benchmark snapshot rows with a versioned, backward-compatible `sparse_conversion` metric block and legacy `not_provided` handling
- [x] 1.2 Normalize production import summaries into sparse attempts, yields, rejection reasons, elapsed time, provider mode, and bounded model labels
- [x] 1.3 Add profile and sparse expectation metadata to `examples/live-benchmarks/trend-pool.json` with deterministic offline validation
- [x] 1.4 Add focused normalization tests for normal candidates, sparse recovery, exhausted recovery, provider failure, zero-candidate, and legacy payloads

## 2. Trend Comparison And Rehearsal

- [x] 2.1 Compare current/baseline sparse metrics with numeric deltas, yield changes, rejection-reason additions/removals, and explicit movement states
- [x] 2.2 Extend fixed-pool trend JSON/Markdown with sparse summaries, profile expectations, coverage status, and bounded follow-up guidance
- [x] 2.3 Extend coverage rehearsal and one-command release rehearsal to generate and preserve sparse trend artifacts and statuses
- [x] 2.4 Preserve sparse trend references in release-safe readiness/team handoff inputs without changing required-gate semantics

## 3. Regression Coverage

- [x] 3.1 Add deterministic fixtures covering mixed profile outcomes, missing repositories, operational blockers, and non-provided sparse metrics
- [x] 3.2 Add CLI/rehearsal tests for offline mode, explicit live selection, seed reproducibility, output paths, and secret/path redaction
- [x] 3.3 Run focused benchmark/evidence tests, full engine tests, Node tests, typecheck, benchmark fixture validation, and OpenSpec strict validation

## 4. Real Repository Delivery Evidence

- [x] 4.1 Select a fresh public GitHub repository for each available profile using an explicit seed and record workspace/import/provider metadata
- [x] 4.2 Run the live sparse conversion benchmark against the selected fresh repositories and preserve normal/sparse/rejection/yield/time outcomes
- [x] 4.3 Use the real local stack and Chrome/Browser human flow to inspect at least one selected imported workspace, including dashboard, review, Why, Drift, and evidence navigation
- [x] 4.4 Generate dated JSON/Markdown trend, release evidence, and readiness history artifacts without secrets or raw repository/model content
- [x] 4.5 Update the taskbook, dated update log, and next-development plan with boundaries and evidence; archive the change, commit scoped files, push `mimo`, and verify GitHub Actions
