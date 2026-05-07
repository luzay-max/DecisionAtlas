## 1. Protocol Output Contract

- [x] 1.1 Extend the guardrail result model with workflow protocol fields such as `workflow_protocol`, `agent_instruction`, `allowed_next_actions`, `disallowed_next_actions`, `human_questions`, and `handoff_summary`.
- [x] 1.2 Derive protocol guidance from existing normalized findings, signals, required tests, human decisions, and recommended next actions without adding an external LLM dependency.
- [x] 1.3 Keep `context.advisory_only` and CLI exit behavior non-blocking by default for `continue`, `caution`, and `pause`.

## 2. Status-Specific Agent Behavior

- [x] 2.1 Add tests proving `continue` permits normal work while still requiring targeted validation and handoff reporting.
- [x] 2.2 Add tests proving `caution` requires addressing or disclosing recommended next actions and caution evidence.
- [x] 2.3 Add tests proving `pause` stops implementation and includes disallowed self-remediation actions.

## 3. Human Decision Requests

- [x] 3.1 Convert `human_decisions_needed` into concrete `human_questions` for agent handoff.
- [x] 3.2 Add fallback human questions for pause-causing findings or signals such as missing OpenSpec context, missing validation evidence, blocked diff, accepted-rule conflict, and review-required drift.
- [x] 3.3 Ensure questions remain traceable to findings, signals, or source results.

## 4. Handoff Summary And Documentation

- [x] 4.1 Add a machine-readable handoff summary with agent status, diff status, drift status, required tests, human questions, and recommended next actions.
- [x] 4.2 Update guardrail documentation with tool-agnostic protocol semantics and Codex/OpenCode/Claude-style examples.
- [x] 4.3 Document a reusable governance summary format for final responses, PR descriptions, and commit handoffs.

## 5. Validation

- [x] 5.1 Run targeted guardrail tests.
- [x] 5.2 Run `openspec validate --all --strict`.
- [x] 5.3 Run `python scripts/governance/agent_guardrail.py --summary` and report any `caution` or `pause` evidence before handoff.
