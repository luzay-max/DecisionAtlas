## Why

DecisionAtlas now has many independent evidence collectors, but release rehearsal still requires an operator to remember several commands and manually connect their outputs. A complete self-hosted product loop needs one stable command that generates a bounded release evidence bundle without hiding partial or operator-guided states.

## What Changes

- Add a one-command release rehearsal collector that composes existing evidence scripts.
- Generate JSON and Markdown bundle outputs under `.tmp` by default.
- Include release evidence, hosted/external readiness, benchmark trend, multi-repo live diagnosis, and readiness-history archive status when inputs are available.
- Preserve `warning`, `operator_guided`, `not_provided`, `provider_failure`, and `local_stack_failure` instead of forcing an all-green release.
- Document the command and update the completion taskbook / update log.

## Capabilities

### New Capabilities
- `release-rehearsal-one-command-evidence`: Defines the one-command release rehearsal bundle and output contract.

### Modified Capabilities
- `release-evidence-automation`: Release evidence can be orchestrated by the one-command bundle.
- `readiness-evidence-history`: Readiness history can archive the one-command bundle outputs.
- `multi-repo-live-diagnosis-rotation`: Multi-repo diagnosis can be included in release rehearsal evidence.
- `project-completion-taskbook`: The taskbook moves from multi-repo diagnosis to the next release rehearsal priority.

## Impact

- Adds a Python CLI under `scripts/ci`.
- Adds targeted CI tests under `services/engine/tests/ci`.
- Adds project documentation for the operator command.
- Updates OpenSpec specs, taskbook, and update log.
- No API, database, or frontend behavior changes expected.
