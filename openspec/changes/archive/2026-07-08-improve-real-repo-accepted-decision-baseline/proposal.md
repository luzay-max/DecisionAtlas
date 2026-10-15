## Why

The latest real-repo run identifies `Textualize/rich` why/drift warnings as `missing_accepted_decision_evidence`. The next improvement is to make accepted-decision baseline quality measurable so release evidence can distinguish "no accepted baseline", "weak accepted baseline", and "baseline present but still insufficient".

## What Changes

- Add accepted-decision baseline metadata to imported workspace core-loop evidence.
- Summarize accepted decision count, candidate count, sample titles, and baseline status in JSON and Markdown.
- Use baseline status to make why/drift grounding more specific and actionable.
- Propagate baseline summaries through multi-repo live diagnosis and warning-lane reduction.
- Add tests and a real `n8n`/`rich` rehearsal to verify the behavior.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `real-repo-core-loop-quality`: real-repo core-loop diagnosis must expose accepted-decision baseline status and use it to explain why/drift warnings.

## Impact

- Affected scripts: `scripts/ci/collect_imported_workspace_core_loop.py`, `scripts/ci/collect_multi_repo_live_diagnosis.py`, `scripts/ci/collect_random_repo_warning_lane_reduction.py`.
- Affected tests: `services/engine/tests/ci/test_imported_workspace_core_loop.py`, `test_multi_repo_live_diagnosis.py`, `test_random_repo_warning_lane_reduction.py`.
- Affected evidence: `.tmp/*core-loop*`, `.tmp/*multi-repo*`, `.tmp/*warning-lane-reduction*`, and readiness history archives.
- No database, API, auth, or UI breaking change.
