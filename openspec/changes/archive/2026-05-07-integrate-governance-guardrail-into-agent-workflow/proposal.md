## Why

DecisionAtlas now has a local advisory guardrail and stable workflow checkpoints, but agents still have to infer how to act on `continue`, `caution`, and `pause` from prose and raw JSON. Stage 9 turns the guardrail into an explicit AI-agent workflow protocol so agents can proceed, disclose, or stop in a predictable way.

## What Changes

- Add an agent-facing workflow protocol summary to the guardrail output, with allowed next actions, disallowed next actions, and handoff expectations.
- Define how agents should respond to `continue`, `caution`, and `pause` without converting advisory results into a default CI gate.
- Make `pause` produce concrete human decision requests tied to source evidence, rather than a vague instruction to review.
- Add a reusable governance summary format for final responses, PR descriptions, and commit handoffs.
- Document Codex/OpenCode/Claude-style usage as examples while keeping the protocol tool-agnostic.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `ai-agent-governance-guardrails`: extend the guardrail contract from status reporting to an agent workflow protocol that identifies allowed/disallowed actions, human decision requests, evidence links, required tests, and reusable handoff summary expectations.

## Impact

- Affected implementation may include `services/engine/app/governance/agent_guardrail.py`, `scripts/governance/agent_guardrail.py`, and related governance tests.
- Affected docs may include `docs/project/governance-agent-guardrail.md`, quick-start/release workflow references, and project guidance for agent usage.
- No default CI blocking, GitHub App PR bot, automatic spec/rule rewriting, or external LLM dependency is introduced.
