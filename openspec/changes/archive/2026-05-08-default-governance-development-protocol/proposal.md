## Why

DecisionAtlas already has governance diff, drift, and AI-agent guardrail capabilities, but the latest master plan identifies that they are still too easy to treat as optional scripts. This change makes the governance workflow a default development protocol so AI-assisted changes consistently run, report, and act on project governance signals.

## What Changes

- Define a default local governance development protocol for non-trivial changes.
- Add a single status entrypoint that summarizes active OpenSpec context, guardrail status, required validation, and handoff obligations.
- Require AI agents and developers to run governance preflight before implementation and governance postflight before completion, archive, or commit.
- Standardize handoff behavior for `continue`, `caution`, and `pause`.
- Keep guardrail behavior advisory by default; this change does not introduce default CI blocking or automatic remediation.
- Update release/development documentation so the default protocol is visible from normal project guidance.

## Capabilities

### New Capabilities

### Modified Capabilities

- `ai-agent-governance-guardrails`: require the guardrail workflow to participate in a default local development protocol with preflight, postflight, status summary, and handoff behavior.
- `release-baseline-validation`: require release/development-facing docs to distinguish the default local governance development protocol from optional enforcement preview and canonical release gates.

## Impact

- Affected scripts: `scripts/governance/*`, with a likely lightweight protocol/status entrypoint or extension to the existing guardrail command.
- Affected docs: README, quick start or developer workflow guidance, release checklist, and `docs/project/governance-agent-guardrail.md`.
- Affected specs: `openspec/specs/ai-agent-governance-guardrails/spec.md` and `openspec/specs/release-baseline-validation/spec.md` through delta specs.
- Affected tests: targeted governance script tests and any release/checklist validation that covers the canonical protocol guidance.
