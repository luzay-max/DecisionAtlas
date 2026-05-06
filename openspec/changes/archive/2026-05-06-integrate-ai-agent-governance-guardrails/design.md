## Context

DecisionAtlas already has three governance layers:

- Governance Markdown ingestion stores human-readable rules, roadmap notes, postmortems, and decisions as reviewable governance knowledge.
- The governance diff checker evaluates the current workspace diff against accepted rules, OpenSpec context, roadmap direction, and validation expectations.
- The governance drift detector analyzes longer-term project direction across specs, archived changes, roadmap documents, update logs, and optional current diff context.

The missing layer is an AI-agent-facing contract. Agents need a stable way to run the existing governance tools before or after implementation and decide whether to continue, proceed with caution, or pause for human review. This change should not make the AI more autonomous in changing governance. It should make the AI more conservative and evidence-driven.

## Goals / Non-Goals

**Goals:**

- Provide one local entrypoint that aggregates governance diff checker and drift detector results for AI-agent use.
- Normalize existing statuses into `continue`, `caution`, and `pause` semantics.
- Return machine-readable output with source-linked evidence, required tests, human decisions, and recommended next actions.
- Document when agents should run the guardrail and when they must stop for human review.
- Keep the first implementation advisory, local, deterministic, and testable without an external LLM provider.

**Non-Goals:**

- Do not automatically edit code, OpenSpec artifacts, roadmap documents, or accepted governance rules.
- Do not introduce a CI blocking gate.
- Do not require network access or an external LLM provider.
- Do not replace the existing diff checker or drift detector CLIs.
- Do not infer and accept new governance rules without human review.

## Decisions

### Decision 1: Add an aggregator instead of changing existing tools

Create a small aggregation module and script that call or reuse the existing governance diff checker and drift detector, then produce an agent-specific summary.

Rationale: the diff checker and drift detector already encode separate product concerns. Changing their native status models would blur their boundaries and risk regressions. An aggregator keeps stage 7 additive.

Alternatives considered:

- Extend the diff checker directly: rejected because drift detection is not only about the current diff.
- Extend the drift detector directly: rejected because current-diff rule conflicts and validation expectations need stronger near-term semantics.
- Build a new independent checker: rejected because it would duplicate existing governance logic.

### Decision 2: Use conservative status mapping

Map source tool statuses to agent status as follows:

- `continue`: diff check passes and drift report is clean or only informational.
- `caution`: diff warning or drift watch/drift_detected signals that do not require a human decision.
- `pause`: diff blocked, drift review_required, accepted-rule conflict, missing OpenSpec context for behavior changes, unsynced human decision, or missing required validation for non-trivial implementation.

Rationale: AI agents should not resolve governance ambiguity silently. If the system cannot distinguish safe continuation from human decision, it should pause.

Alternatives considered:

- Preserve raw statuses only: rejected because agents need a single operational contract.
- Add more statuses such as `fail`, `review`, or `blocked`: rejected for the first slice because three statuses are enough for agent behavior.

### Decision 3: Make output evidence-first and machine-readable

The guardrail result should include `agent_status`, `summary`, `findings`, `signals`, `matched_rules`, `required_tests`, `human_decisions_needed`, `recommended_next_actions`, and `source_results`.

Rationale: agent usage needs both compact interpretation and full traceability. Keeping raw source results prevents loss of context and allows later UI/API integration.

Alternatives considered:

- Return only a prose report: rejected because AI and automation clients need stable fields.
- Return only raw checker outputs: rejected because callers would each reimplement inconsistent status mapping.

### Decision 4: Keep first integration local and advisory

The first implementation should be a local script, likely under `scripts/governance/`, backed by a service module under `services/engine/app/governance/`.

Rationale: the project is still shaping governance semantics. Local advisory usage lets the team validate signal quality before turning this into CI policy, PR automation, or product UI.

Alternatives considered:

- Add a CI gate now: rejected because false positives would block velocity before the semantics are proven.
- Add a product UI now: rejected because the first need is agent consumption and repeatable local validation.

## Risks / Trade-offs

- [Risk] Existing checker and detector result shapes drift independently -> Mitigation: keep adapter tests for each source status and fail clearly on unknown statuses.
- [Risk] False-positive `pause` results slow development -> Mitigation: pause only on explicit high-risk conditions and include actionable next steps.
- [Risk] Agents over-trust advisory output -> Mitigation: document that clean output is not a correctness proof and does not replace tests or human review.
- [Risk] The guardrail becomes a hidden policy engine -> Mitigation: expose source results and avoid automatic code/spec/rule mutation.
- [Risk] Duplicate validation suggestions appear from both source tools -> Mitigation: de-duplicate required tests and recommended actions in the aggregator.

## Migration Plan

This is additive. Existing governance diff and drift commands remain supported.

1. Add the aggregation module and local script.
2. Add fixtures and targeted tests for `continue`, `caution`, and `pause`.
3. Add agent-facing documentation.
4. Keep CI/release gates unchanged.

Rollback is deleting the new aggregator module, script, tests, and documentation. Existing governance tools remain unaffected.

## Open Questions

- Should later product UI expose the same guardrail result, or should it get a separate user-facing summary shape?
- Should a future CI mode treat `pause` as a soft annotation or hard failure?
- Which AI agent entrypoints should call this first: local Codex workflow, GitHub PR review helper, or hosted operator flow?
