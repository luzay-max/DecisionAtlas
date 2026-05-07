## Context

The current guardrail aggregates diff and drift results into `continue`, `caution`, or `pause`, and Stage 8 made the command part of local workflow checkpoints. The remaining gap is behavioral: different agents can still interpret the same status differently, especially when deciding whether to continue, disclose caution evidence, or stop and ask a human.

Stage 9 should add an explicit workflow protocol on top of the existing guardrail result without replacing the underlying diff checker, drift detector, or advisory-only boundary.

## Goals / Non-Goals

**Goals:**

- Add agent-facing protocol guidance to the guardrail output.
- Make `continue`, `caution`, and `pause` map to predictable allowed and disallowed next actions.
- Ensure `pause` includes concrete human decision requests when source results provide enough evidence.
- Provide a reusable governance summary format for final answers, PR descriptions, and commit handoffs.
- Keep the protocol tool-agnostic so Codex, OpenCode, Claude, or another agent can consume the same contract.

**Non-Goals:**

- Do not introduce a GitHub App PR bot.
- Do not make guardrail results fail CI by default.
- Do not auto-generate or auto-edit OpenSpec artifacts, roadmap documents, governance documents, accepted rules, or application code in response to `pause`.
- Do not add an external LLM dependency.
- Do not replace targeted tests, code review, or OpenSpec validation.

## Decisions

### Add protocol fields to the existing guardrail result

The implementation should extend the existing machine-readable result with protocol-oriented fields rather than adding a separate command. Candidate fields include:

- `workflow_protocol`: stable protocol name/version and advisory-only marker.
- `agent_instruction`: concise imperative guidance for the current status.
- `allowed_next_actions`: actions the agent may take after this result.
- `disallowed_next_actions`: actions the agent must not take without human review.
- `human_questions`: concrete questions the agent should ask when human review is needed.
- `handoff_summary`: a compact, reusable summary for final responses, PR descriptions, and commit handoffs.

Alternative considered: keep JSON unchanged and document the protocol only in prose. That is weaker because every agent must infer behavior from documentation instead of consuming a stable contract.

### Derive protocol guidance from existing source evidence

The protocol should use the already-normalized `findings`, `signals`, `required_tests`, `human_decisions_needed`, `recommended_next_actions`, and `source_results`. It should not invent hidden evidence or require an LLM to interpret prose.

Alternative considered: add a provider-backed summarizer. That would add dependency and determinism risk without being necessary for the first protocol layer.

### Treat `pause` as stop-and-ask, not self-remediation

When status is `pause`, allowed actions should be limited to summarizing evidence, asking human questions, and recording the handoff. Disallowed actions should explicitly include silently rewriting code/specs/roadmap/rules to clear the guardrail and committing without human review.

Alternative considered: let agents attempt automatic remediation first. That is dangerous because the most important `pause` cases involve governance authority, missing OpenSpec context, or unsynced human decisions.

### Keep examples agent-specific but contract tool-agnostic

Documentation can include Codex/OpenCode/Claude examples, but the normative contract should be expressed as agent-agnostic JSON and handoff semantics.

Alternative considered: create separate protocols per agent. That would fragment the contract before there is evidence that agent-specific behavior is needed.

## Risks / Trade-offs

- Protocol fields duplicate existing recommendations -> keep them derived from the same normalized result and make their purpose behavioral rather than evidentiary.
- Human questions become vague -> generate questions from `human_decisions_needed`, pause findings, and pause signals, and test representative pause cases.
- Agents over-trust `continue` -> continue guidance must still require targeted tests and normal validation.
- Caution gets ignored -> handoff summary must include caution evidence and recommended actions.
- Protocol versioning is premature -> include a small stable protocol identifier so future changes can evolve without breaking consumers.
