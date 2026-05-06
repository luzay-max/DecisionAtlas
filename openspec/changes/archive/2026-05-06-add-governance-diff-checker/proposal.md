## Why

DecisionAtlas now has accepted governance rules from Markdown documents, but there is no way for a developer or AI agent to check whether the current change still aligns with those rules, the active OpenSpec change, and the project roadmap. Stage 5 should add a conservative governance checker so project direction can be evaluated before code is merged, without turning AI into an automatic authority.

## What Changes

- Add a local governance diff check entrypoint that can inspect the current git diff and relevant project governance context.
- Collect bounded context from:
  - current git diff
  - active OpenSpec change, if any
  - main OpenSpec specs
  - master roadmap / plan documents
  - accepted governance rules from the governance knowledge layer
  - recent update logs or postmortem-style governance documents when available
- Produce a structured check result with:
  - overall status: `pass`, `warning`, or `blocked`
  - findings with severity and source references
  - matched governance rules
  - conflicting or missing governance context
  - likely required tests or validation commands
  - recommended next action
- Keep the first implementation deterministic and explainable where possible, with AI-facing output schema ready for later agent use.
- Keep CI blocking, automatic code modification, and automatic rule rewriting out of scope.

## Capabilities

### New Capabilities

- `governance-diff-checker`: Check a current change against OpenSpec, roadmap context, accepted governance rules, and validation expectations, returning a structured conservative governance result.

### Modified Capabilities

- None.

## Impact

- New governance checker module or script for local checks.
- Possible API/CLI wrapper only if needed for the first usable entrypoint.
- Tests and fixtures for git diff analysis, missing OpenSpec detection, matched accepted-rule references, and status grading.
- Documentation updates describing how to run the checker and how to interpret `pass`, `warning`, and `blocked`.
