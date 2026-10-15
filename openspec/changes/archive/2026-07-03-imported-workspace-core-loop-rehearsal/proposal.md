## Why

The completion taskbook marks the core product loop as partial because current evidence proves demo/browser flow and benchmark behavior, but does not yet produce one operator-readable artifact that connects an imported workspace to review, why-search, drift, and governance guardrail checks.

This change adds that missing evidence lane so a real public GitHub repository workspace can be evaluated as a complete DecisionAtlas loop instead of a collection of separate checks.

## What Changes

- Add a CI/operator rehearsal collector for imported workspace core-loop evidence.
- Reuse or accept public GitHub import rehearsal output to identify the imported workspace.
- Probe dashboard, review queue, why-search, drift, and guardrail evidence and summarize each lane.
- Add a browser rehearsal for an imported workspace using a real public GitHub repository reference while keeping mocked UI provider lanes explicit.
- Preserve `operator_guided`, `not_provided`, `warning`, and provider/local stack failures rather than converting them to pass.
- Update the completion taskbook and update log with this new evidence lane.

## Capabilities

### New Capabilities

- `imported-workspace-core-loop-rehearsal`: Defines evidence for an imported workspace moving through setup/reuse, dashboard, review, why-search, drift, and guardrail lanes.

### Modified Capabilities

- `live-repository-analysis`: Adds core-loop evidence expectations after a public repository workspace exists or is reused.
- `real-browser-workflow-rehearsal`: Adds imported workspace browser coverage expectations.
- `project-completion-taskbook`: Updates the P0 core-loop task from partial toward complete when evidence exists.

## Impact

- Adds `scripts/ci/collect_imported_workspace_core_loop.py`.
- Adds tests under `services/engine/tests/ci/`.
- Adds an imported workspace browser rehearsal under `apps/web/tests-e2e/`.
- Updates docs, taskbook, and OpenSpec specs.
- No database schema or API contract changes expected.
