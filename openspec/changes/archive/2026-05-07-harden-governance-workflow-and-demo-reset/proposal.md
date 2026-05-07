## Why

Post-stage-7 DecisionAtlas has the core governance memory, diff, drift, and agent guardrail capabilities, but the development and demo workflow is not yet stable enough to rely on repeatedly. The seeded demo lane can be consumed by prior walkthroughs, real-stack startup currently uses non-destructive seeding that does not restore full guided-demo state, and the agent guardrail needs a clearer place in the day-to-day development rhythm.

## What Changes

- Define a deterministic seeded-demo recovery contract that restores the guided demo lane to a known state without deleting imported workspaces.
- Clarify reset versus reseed behavior for demo recovery, including when migrations or database drift require the deeper path.
- Clarify real-stack startup behavior as non-destructive by default, with an explicit path for restoring consumed seeded-demo state.
- Keep Alembic revision length validation visible as part of real-stack and migration hardening expectations.
- Harden the AI-agent governance workflow by documenting when developers and agents run the guardrail and how `continue`, `caution`, and `pause` should affect next actions.
- Preserve the guardrail as advisory: `pause` is a human-decision signal, not an automatic code/spec rewrite or CI blocker.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `hosted-demo-operator-flow`: strengthen seeded-demo reset/reseed recovery requirements so the review queue, accepted baseline, why-search, timeline, and drift walkthrough state can be restored predictably while preserving imported workspaces.
- `v0-3-real-stack-validation`: require real-stack validation to distinguish non-destructive seed behavior from explicit demo reset behavior and keep migration revision ID length validation in the expected validation set.
- `ai-agent-governance-guardrails`: clarify the development workflow checkpoints where agents and developers should run the guardrail, and preserve `pause` as an advisory human-review signal.

## Impact

- Affected scripts may include `scripts/demo/reset_seeded_demo.py`, `scripts/demo/reset-demo.ps1`, `scripts/demo/reseed-demo.ps1`, `scripts/dev/start-real-stack.ps1`, and related package shortcuts if an explicit reset option is added.
- Affected validation may include engine migration tests, seeded-demo state checks, and governance guardrail tests.
- Affected documentation may include quick start, deployment, hosted operator guidance, release checklist, and governance agent guardrail guidance.
- No breaking API changes are expected.
