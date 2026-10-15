## Why

The latest random-repo warning reduction showed three product-controlled warning lanes, but one was a release rehearsal interpretation bug and the remaining multi-repo warnings mixed real product quality gaps with import-wait/operator proof states. Real repository release evidence needs stronger core-loop quality signals before the project can claim improvement trends.

## What Changes

- Fix release rehearsal benchmark comparison summarization so ready comparison evidence is not reported as `unknown`.
- Add richer multi-repo diagnosis fields that separate product quality actions from operator/setup actions.
- Add core-loop lane metadata for actionable category, especially when review/why/drift warnings are caused by import still not being benchmark-ready.
- Regenerate random-repo warning reduction evidence to verify product-controlled warning lanes decrease without hiding source warning status.

## Capabilities

### New Capabilities
- `real-repo-core-loop-quality`: Tracks real repository core-loop quality gaps and separates product-controlled work from operator/setup proof.

### Modified Capabilities
- `release-rehearsal-one-command-evidence`: Benchmark comparison lanes derive status from comparison summary when the source has no explicit status.
- `multi-repo-live-diagnosis-rotation`: Multi-repo diagnosis reports product action counts and operator/setup action counts.
- `imported-workspace-core-loop-rehearsal`: Core-loop lanes expose action categories for downstream aggregation.
- `random-repo-warning-lane-reduction`: Warning-lane reduction uses core-loop action categories and avoids classifying import-wait/operator setup lanes as product-controlled.

## Impact

- Updates CI evidence collectors under `scripts/ci/`.
- Updates targeted CI tests under `services/engine/tests/ci/`.
- Regenerates `.tmp` release/warning evidence and readiness history entry.
- Updates OpenSpec specs, project logs, and taskbook guidance.
