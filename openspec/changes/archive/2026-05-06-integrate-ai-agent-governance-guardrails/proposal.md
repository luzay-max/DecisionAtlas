## Why

DecisionAtlas now has accepted governance rules, current-diff governance checks, and long-term governance drift reports, but AI agents still need a stable way to use those signals during development. Stage 7 should connect the existing governance tools into an agent-facing guardrail so AI can continue, caution, or pause based on source-linked evidence rather than guessing project direction.

## What Changes

- Add an AI-agent governance guardrail capability that aggregates the governance diff checker and governance drift detector into a single agent-facing summary.
- Define agent status semantics: `continue`, `caution`, and `pause`.
- Add conservative pause rules for blocked diff checks, review-required drift reports, accepted-rule conflicts, missing OpenSpec context for behavior changes, unsynced human decisions, and missing validation expectations.
- Add a local entrypoint for agents to run before or after implementation, returning machine-readable JSON with evidence, required tests, human decisions, and recommended next actions.
- Add documentation that tells AI agents when to run the guardrail, how to interpret results, and when to stop for human review.
- Keep the first implementation advisory and local: no CI blocking, no automatic code edits, no automatic spec/rule rewrites, and no external LLM provider dependency.

## Capabilities

### New Capabilities

- `ai-agent-governance-guardrails`: Aggregate governance check and drift report results into an agent-facing advisory summary with continue/caution/pause semantics.

### Modified Capabilities

- None.

## Impact

- New local governance aggregation script or module, likely under `scripts/governance/` and `services/engine/app/governance/`.
- New fixtures and tests for clean, caution, and pause scenarios.
- Documentation for AI-agent usage and pause rules.
- Existing governance diff checker and governance drift detector should remain independently runnable.
