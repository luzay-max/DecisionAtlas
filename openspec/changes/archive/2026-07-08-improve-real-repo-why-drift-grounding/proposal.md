## Why

The latest real-repo quality run still leaves `Textualize/rich` with product-controlled `why_search` and `drift` warnings. These warnings are too coarse for release decisions because they identify that core-loop quality work remains, but they do not preserve enough grounded reason detail to make the next remediation measurable.

## What Changes

- Add grounded reason metadata for real-repo `why_search` and `drift` lanes.
- Distinguish unsupported/weak evidence from actionable accepted-decision and drift follow-up gaps.
- Surface compact reason codes and evidence summaries in JSON and Markdown outputs.
- Extend regression tests to prove `rich`-style warning lanes remain product-controlled but become explainable and targetable.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `real-repo-core-loop-quality`: real-repo core-loop diagnosis must explain why/drift warnings with bounded grounded reason codes and release-readable summaries.

## Impact

- Affected scripts: `scripts/ci/collect_imported_workspace_core_loop.py`, `scripts/ci/collect_multi_repo_live_diagnosis.py`, `scripts/ci/collect_random_repo_warning_lane_reduction.py`.
- Affected tests: CI evidence collector tests under `services/engine/tests/ci/`.
- Affected evidence: `.tmp/*diagnosis*`, `.tmp/*warning-lane-reduction*`, and archived readiness evidence.
- No expected API, database, dependency, or UI breaking change.
