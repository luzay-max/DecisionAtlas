## Why

DecisionAtlas already has real-repository benchmark fixtures and a live validation runner, but the output is still closer to operational validation than product-value evidence. Stage 11 should turn the curated repository set into a repeatable value benchmark that explains where DecisionAtlas is useful today, where evidence is thin, and what future extraction or retrieval work should improve.

## What Changes

- Classify each curated repository by benchmark role, such as small Python, medium TypeScript, documentation-heavy, decision-rich, stress, or regression case.
- Extend benchmark expectations and reports to capture value-oriented metrics: import success, artifact and screened-in counts, candidate count, candidate quality distribution, accepted baseline quality, why-search hit quality, and drift signal usefulness.
- Add an operator-readable benchmark report, preferably Markdown plus the existing machine-readable JSON, so results can be reviewed without manually interpreting raw payloads.
- Preserve explicit handling for missing workspaces, provider/network failures, and unavailable local services as operational outcomes rather than product-quality failures.
- Keep offline fixture validation deterministic and keep live real-repository benchmark execution outside default CI.
- Document how to run and interpret the value benchmark.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `lightweight-real-repo-benchmarks`: Expand fixture expectations and live report behavior from readiness checks into a real-repository value benchmark with repository roles, value outcomes, quality distributions, why/drift usefulness summaries, and operator-readable reporting.
- `real-repository-outcomes`: Clarify that real-repository validation output must be able to distinguish product value, product limitation, and operational failure for curated benchmark repositories.

## Impact

- `examples/live-benchmarks/*.json` curated repository and case fixtures.
- `scripts/ci/run_benchmark.py` report generation and validation logic.
- Benchmark/eval tests under `services/engine/tests/evals/`.
- Documentation or report output under `docs/project/` or `.tmp/` for operator-readable benchmark results.
- No product runtime dependency changes and no default CI live-network requirement.
