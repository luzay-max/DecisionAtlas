## Why

DecisionAtlas now has a release-quality imported-repository loop, but the real-repo checks that proved recent improvements are still mostly captured in narrative notes and ad hoc manual validation. A lightweight benchmark set will preserve the highest-value regression cases without turning validation into a large evaluation platform.

## What Changes

- Add a small, curated real-repo benchmark fixture format for imported-workspace checks.
- Capture representative why-search expectations for real imported repositories, starting with high-signal `browser-use/browser-use` cases.
- Capture lightweight drift expectations that protect against known false-positive regressions without requiring continuous drift monitoring.
- Extend benchmark validation so fixture shape and expectations are checked in CI-safe mode.
- Keep live execution optional and bounded; the default benchmark check should remain fast and not require external repository imports.

## Capabilities

### New Capabilities

- `lightweight-real-repo-benchmarks`: Defines the curated real-repo benchmark fixture set and validation behavior.

### Modified Capabilities

- `real-repository-outcomes`: Requires important imported-repo quality expectations to be captured as lightweight benchmark cases, not only prose.

## Impact

- Affected fixtures:
  - `examples/live-benchmarks/`
- Affected validation:
  - `scripts/ci/run_benchmark.py`
  - related tests for benchmark fixture validation
- Affected docs:
  - `docs/project/real-repository-validation-baseline.md`
  - release or roadmap notes if needed

No production API behavior should change. This is a validation and release-confidence change, not a product feature.
