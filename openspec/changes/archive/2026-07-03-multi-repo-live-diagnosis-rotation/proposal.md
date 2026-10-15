## Why

The completion taskbook still marks real GitHub repository validation as partial. Single-repo browser and core-loop evidence exists, but the project needs a repeatable way to rotate across several real public repositories, classify outcomes, and preserve trends without hiding provider/local-stack failures.

This change creates a multi-repo diagnosis rehearsal that moves DecisionAtlas closer to a complete, evidence-backed product loop.

## What Changes

- Add a multi-repo diagnosis script that selects real public GitHub repositories from the existing benchmark pool.
- Support explicit repo IDs and deterministic random selection.
- For each repo, run or consume public import rehearsal and imported workspace core-loop evidence.
- Summarize setup, dashboard, review, why-search, drift, and guardrail status per repository.
- Generate JSON and Markdown evidence suitable for release/readiness handoff.
- Preserve `operator_guided`, `provider_failure`, `local_stack_failure`, `warning`, and `not_provided` states.

## Capabilities

### New Capabilities

- `multi-repo-live-diagnosis-rotation`: Defines repeatable multi-repo diagnosis evidence for real public GitHub repository rotation.

### Modified Capabilities

- `imported-workspace-core-loop-rehearsal`: Allows its evidence to be aggregated across multiple repositories.
- `real-repo-benchmark-trend-pool`: Extends the trend pool role from benchmark comparison to diagnosis rotation selection.
- `project-completion-taskbook`: Updates next priorities after multi-repo diagnosis exists.

## Impact

- Adds `scripts/ci/collect_multi_repo_live_diagnosis.py`.
- Adds CI tests for deterministic selection, partial outcomes, and Markdown summary.
- Adds docs and update-log entries.
- No API, database, or frontend behavior changes expected.
