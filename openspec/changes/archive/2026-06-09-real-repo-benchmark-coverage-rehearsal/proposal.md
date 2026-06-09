## Why

The fixed real-repo trend pool now exposes missing coverage, but operators still have to manually chain live validation, snapshot creation, comparison, and trend generation. This makes release rehearsal error-prone and keeps the 5-repo pool from becoming a repeatable evidence lane.

## What Changes

- Add a real-repo benchmark coverage rehearsal command that coordinates fixed-pool coverage evidence.
- Support offline deterministic rehearsal from explicit current report/baseline inputs.
- Support optional live local API rehearsal against the full fixed pool without requiring GitHub/model/provider access in default CI.
- Generate a top-level JSON/Markdown rehearsal summary that links current report, snapshot, comparison, and trend artifacts.
- Document how to use this as the next release rehearsal step after fixed-pool trend evidence.

## Capabilities

### New Capabilities
- `real-repo-benchmark-coverage-rehearsal`: Coordinates fixed-pool real-repo validation, snapshot, comparison, and trend evidence into one operator-readable rehearsal.

### Modified Capabilities
- `real-repo-benchmark-trend-pool`: Trend evidence receives a documented upstream rehearsal flow.
- `lightweight-real-repo-benchmarks`: Benchmark comparison workflows can be orchestrated by a release rehearsal wrapper.

## Impact

- Affected code: new script under `scripts/ci/`, tests under `services/engine/tests/ci/`, release docs and update log.
- Affected evidence: `.tmp/real-repo-benchmark-coverage-rehearsal.json/md`, plus generated current report, snapshot, comparison, and trend artifacts.
- No database migration, frontend API change, GitHub API dependency, model-provider dependency, or default live network dependency.
