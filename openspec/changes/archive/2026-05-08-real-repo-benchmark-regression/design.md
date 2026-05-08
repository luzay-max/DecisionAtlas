## Context

The repository already has a real-repo benchmark foundation:

- `examples/live-benchmarks/repositories.json`, `why-cases.json`, and `drift-cases.json` define curated public-repository expectations.
- `scripts/ci/run_benchmark.py --live-real-repos` can evaluate existing imported workspaces and write JSON plus Markdown value reports.
- `services/engine/tests/evals/test_benchmark_fixtures.py` validates fixture shape and several report evaluator paths.
- `docs/project/real-repository-validation-baseline.md` explains that live reports are operator-guided and outside the default release gate.

The remaining gap is historical comparison. A live report can say what happened today, but it does not yet answer whether the repository improved, regressed, stayed stable, or was blocked by setup. That makes release evidence manual and easy to lose.

## Goals / Non-Goals

**Goals:**

- Define a small, durable benchmark history snapshot format derived from live real-repo reports.
- Add deterministic validation for committed or operator-selected history snapshots.
- Add current-vs-baseline comparison output for repository rows and overall summary.
- Keep comparison based on bounded fields, not exact generated prose or repository-specific candidate titles.
- Distinguish product regressions from missing workspaces, API failures, provider failures, and other operational blockers.
- Make the output useful for later release evidence automation without implementing that automation in this change.

**Non-Goals:**

- Do not put live real-repo benchmark execution into default CI.
- Do not automatically import missing repositories.
- Do not create a hosted benchmark dashboard.
- Do not store raw answer prose, credentials, private repository data, or large generated reports as durable baseline artifacts.
- Do not implement the next release-evidence aggregation change here.

## Decisions

1. Store compact history snapshots, not raw live reports.

   The live report already contains detailed rows. Regression history should store a smaller derived shape: generated date, benchmark version, repo id, value outcome, bounded outcome, pass state, key metrics, limitation categories, follow-up categories, why/drift case summaries, and operational error type if present. This avoids committing noisy `.tmp` output while preserving comparison evidence.

2. Compare by repository id and bounded outcome order.

   Repository ids are stable fixture keys. Comparison should classify each current row against the baseline row with the same id. Value outcome movement should use an explicit ordered family where `useful_now` is strongest, `reviewable_limited` is next, product-limited states are lower, and operational states are not treated as product regressions by default.

3. Keep operational blockers separate from product movement.

   Missing workspaces, API failures, provider configuration, GitHub/network issues, and auth/session failures should produce `operational_blocked` or `missing_workspace` comparison states. They should be visible in release evidence, but they should not be counted as proof that extraction, why-search, or drift quality regressed.

4. Generate both machine-readable and Markdown comparison reports.

   JSON is needed for future release evidence automation. Markdown is needed for operator handoff and release review. The Markdown report should mirror the JSON summary and list each repo movement with short reasons.

5. Make offline validation deterministic.

   Default benchmark validation should validate fixture shape, history snapshot shape, comparison logic, and Markdown rendering with local test data only. It must not require GitHub, model providers, a running API, or existing imported workspaces.

## Risks / Trade-offs

- [Risk] Trend comparisons may overstate movement caused by provider or local-state variance. Mitigation: classify operational blockers separately and keep comparison reasons visible.
- [Risk] Committed baselines may become stale. Mitigation: store only small dated snapshots and document when to refresh them.
- [Risk] Outcome ordering can hide important metric-level regressions. Mitigation: compare supporting metrics such as candidate count, strong count, thin ratio, why pass count, and drift forbidden-case failures.
- [Risk] Benchmark pressure can incentivize product code to special-case curated repositories. Mitigation: keep repository-specific data inside fixtures/reports only and add no runtime product behavior.

## Migration Plan

- Add comparison helpers and CLI options to `scripts/ci/run_benchmark.py`.
- Add or update deterministic tests for history snapshot validation and comparison classification.
- Add a small sanitized example or fixture for comparison tests if needed.
- Update documentation with the operator flow: run live report, save compact baseline when appropriate, compare future report against that baseline, then summarize movement in release notes.
- No database migration is required.
