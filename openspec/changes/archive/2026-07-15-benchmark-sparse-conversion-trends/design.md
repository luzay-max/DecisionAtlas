## Context

The repository already has a source-controlled benchmark pool, live current reports, historical snapshots, comparison movement, and readiness evidence. Import jobs also emit bounded sparse/recovery counters, but those counters are not carried into benchmark snapshots or compared across releases. The change crosses the benchmark scripts, fixed pool metadata, coverage rehearsal, release rehearsal, and CI tests.

The design must work with legacy snapshots, remain offline-testable, and keep real-repository evidence honest. A zero-candidate run is a valid observed outcome, not an implicit failure or a reason to fabricate a candidate. Provider identity is recorded as a bounded mode/model label, never as credentials or raw responses.

## Goals / Non-Goals

**Goals:**

- Normalize sparse conversion metrics from live import summaries into versioned benchmark snapshot rows.
- Compare current and baseline sparse metrics per repository, including numeric deltas, yield ratios, rejection reason changes, and explicit movement states.
- Make repository profiles and expected sparse behavior visible in the fixed pool.
- Generate JSON/Markdown trend evidence that can be consumed by coverage rehearsal, release rehearsal, team handoff, and readiness history.
- Preserve zero-candidate, provider-failure, product-limited, missing, and operator-guided states without hiding them behind aggregate scores.
- Provide deterministic offline fixtures plus a real fresh-repository rehearsal path.

**Non-Goals:**

- No automatic accept/reject/merge/delete of decisions or candidates.
- No new model provider, prompt family, billing, multi-tenancy, Marketplace, or OAuth work.
- No requirement that every repository produce a candidate; repository-specific expectations remain explicit and bounded.
- No network access in default unit tests or offline evidence generation.

## Decisions

### 1. Add a nested, versioned sparse metric block to snapshot rows

Each benchmark row will carry a `sparse_conversion` object with bounded counters and labels: normal attempts/candidates, sparse eligible/attempted/model attempts, recovered candidates, candidate and recovered yields, rejection reasons, elapsed seconds, provider mode, model label, and outcome status. The snapshot schema version increments, while readers accept the previous schema and fill absent sparse data as `not_provided`.

This keeps existing top-level benchmark metrics compatible and makes the sparse contract independently extensible. A flat expansion of many top-level fields was rejected because it would make legacy compatibility and Markdown rendering harder.

### 2. Derive live metrics from existing import summaries

The live benchmark collector will read the existing dashboard/import summary fields and normalize them; it will not create a second import execution path. The collector records the selected repository id, workspace, explicit base URL, and provider mode/model label. It does not persist raw model output or repository content.

This reuses the production counters and ensures the benchmark measures the same sparse lane users experience. A separate benchmark-only sparse runner was rejected because it could drift from production behavior.

### 3. Compare metrics with explicit bounded movement

Comparison output will include current/baseline values and deltas for sparse metrics, plus added/removed rejection reasons. Movement remains per repository and per metric; overall status is warning for regressions, operational blockers, missing coverage, or invalid/unknown outcomes. Improvements do not erase a simultaneous provider failure or zero-candidate limitation.

No single weighted score will decide release readiness. Weighted scoring was rejected because it would hide whether a result was blocked by infrastructure, limited by product quality, or simply produced no candidate.

### 4. Use profile-aware pool expectations, not universal thresholds

Pool rows will declare a profile (`small_sparse`, `medium_decision_rich`, `docs_heavy`, or `stress`) and bounded expectations such as whether sparse recovery is expected, minimum observable attempt coverage, and accepted zero-candidate/rejection states. Validation remains offline and deterministic.

Universal candidate-count thresholds were rejected because repository shape and evidence density differ materially.

### 5. Keep evidence outputs explicit and release-safe

Coverage rehearsal will write current report/snapshot/comparison/trend artifacts under the requested output directory and include sparse summary fields in its top-level JSON/Markdown. Release rehearsal and readiness consumers will reference the trend path explicitly; missing trend evidence remains `not_provided` or `warning`.

Default commands remain non-mutating. A live run requires an explicit `--live` flag and records the target URL and selected pool ids.

## Risks / Trade-offs

- [Risk] Existing historical snapshots lack sparse fields. -> Treat them as `not_provided` and preserve a clear first-measurement boundary instead of inventing baseline values.
- [Risk] Provider/runtime labels may be unavailable in older deployments. -> Record `unknown`/`not_provided` and keep the rest of the metrics usable.
- [Risk] A fresh repository may legitimately produce zero candidates. -> Preserve `zero_candidate` with rejection reasons and profile expectations; do not fail solely for that outcome.
- [Risk] Live benchmark runs are slow and network-dependent. -> Keep CI fixtures offline and make live repository selection explicit, bounded, and reproducible by seed.
- [Risk] Sparse metric names drift from import summaries. -> Add normalization tests against representative normal, recovered, exhausted, provider-failure, and legacy payloads.

## Migration Plan

1. Add the new snapshot/trend schema and backward-compatible readers with offline fixtures.
2. Extend the fixed pool metadata and coverage/release renderers.
3. Run focused tests, full engine/web/API regressions, strict OpenSpec validation, and benchmark fixture validation.
4. Run a live rehearsal against at least one fresh repository from each available profile, recording provider mode and selected ids.
5. If a release must roll back, continue reading old snapshots as `not_provided` and omit sparse comparison; no database migration or destructive rollback is required.

## Open Questions

- The first real pool run will determine whether the initial profile expectations need calibration; calibration must be recorded as evidence, not silently changed in code.
