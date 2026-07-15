## Why

The live real-repository benchmark currently treats `expected_value_outcomes` as exact membership. A repository that improves from a limited profile to `useful_now` can therefore fail validation, as happened with the real n8n workspace after it reached 72 candidates, 7 accepted decisions, 14 strong candidates, and zero thin-candidate pressure.

## What Changes

- Evaluate ranked product value outcomes against the minimum configured product-value floor instead of exact membership only.
- Record whether the observed outcome is an exact fixture match, exceeds the configured floor, falls below it, or is operational.
- Keep missing workspace and operational blocker outcomes separate from product improvement and preserve all dashboard, candidate-quality, Why, and Drift gates.
- Add deterministic regression coverage and rerun the fixed live repository benchmark to prove that n8n's improved state no longer creates a false failure.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `real-repository-outcomes`: Curated benchmark value expectations become monotonic for ranked product outcomes while operational outcomes remain explicit and non-promotable.

## Impact

- `scripts/ci/run_benchmark.py` value-outcome expectation assessment and bounded report fields.
- `services/engine/tests/evals/test_benchmark_fixtures.py` regression tests.
- Live benchmark JSON/Markdown, comparison evidence, release evidence, and readiness history generated from those reports.
