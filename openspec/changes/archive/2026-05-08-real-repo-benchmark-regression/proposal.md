## Why

DecisionAtlas already has curated real-repository benchmark fixtures and live value reports, but each live run is still mostly a standalone snapshot. The next step is to turn those snapshots into a repeatable regression trail so release work can compare current real-repo value against prior observed baselines without relying on memory.

## What Changes

- Add a benchmark history format that stores dated real-repo validation summaries outside generated `.tmp/` reports.
- Add comparison logic that can compare a current live real-repo report against a selected previous baseline.
- Classify repository-level movement as improved, unchanged, regressed, newly evaluated, missing, or operationally blocked.
- Summarize trend-relevant metrics such as value outcome, readiness state, candidate count, strong/thin quality pressure, why-case support, drift false-positive checks, limitation categories, and follow-up categories.
- Keep live benchmark execution operator-guided and outside default CI while making offline fixture/history validation deterministic.
- Add operator documentation for capturing benchmark baselines and interpreting regression output before release.

## Capabilities

### New Capabilities

### Modified Capabilities

- `lightweight-real-repo-benchmarks`: Extend live real-repo benchmark reporting with persisted baseline snapshots, deterministic history validation, and current-vs-baseline comparison output.
- `real-repository-outcomes`: Clarify that curated repository value outcomes can be compared over time and that regressions should distinguish product-value movement from operational blockers.

## Impact

- `scripts/ci/run_benchmark.py` live real-repo report generation and validation helpers.
- `examples/live-benchmarks/` fixture or history metadata for expected regression comparison shape.
- `services/engine/tests/evals/test_benchmark_fixtures.py` targeted benchmark validation coverage.
- `docs/project/real-repository-validation-baseline.md` or adjacent docs explaining how to capture and compare benchmark baselines.
- Optional generated reports under `.tmp/`; durable baseline examples should be small, sanitized, and explicitly versioned if committed.
