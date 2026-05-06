## 1. Core Aggregation

- [x] 1.1 Add a governance guardrail service module that accepts diff-check and drift-detection results and returns an agent-facing aggregate.
- [x] 1.2 Implement conservative status mapping from source statuses to `agent_status: continue | caution | pause`.
- [x] 1.3 Preserve source result evidence in `source_results` and expose normalized `findings`, `signals`, `matched_rules`, `required_tests`, `human_decisions_needed`, and `recommended_next_actions`.
- [x] 1.4 De-duplicate repeated required tests and recommended actions while keeping source references traceable.

## 2. Local Agent Entrypoint

- [x] 2.1 Add a local script under `scripts/governance/` that runs the existing diff checker and drift detector, then emits the aggregated guardrail JSON.
- [x] 2.2 Support a machine-readable JSON mode suitable for AI agents and a concise human-readable summary for local debugging.
- [x] 2.3 Ensure the script exits successfully by default for advisory `caution` or `pause` results unless a future explicit gate mode is added.

## 3. Agent Usage Documentation

- [x] 3.1 Add documentation that explains when agents should run the guardrail before implementation, after implementation, and before committing or archiving a change.
- [x] 3.2 Document `continue`, `caution`, and `pause` semantics with examples tied to accepted-rule conflicts, missing OpenSpec context, unsynced human decisions, and missing validation evidence.
- [x] 3.3 Document that `pause` requires human review and must not trigger automatic code, spec, roadmap, or governance-rule edits.

## 4. Tests and Fixtures

- [x] 4.1 Add unit tests for `continue`, `caution`, and `pause` status mapping.
- [x] 4.2 Add tests proving source results remain traceable in the aggregated output.
- [x] 4.3 Add tests proving advisory `pause` results do not imply file mutation or CI-style failure behavior.
- [x] 4.4 Add script-level validation or smoke coverage for JSON output shape.

## 5. Validation

- [x] 5.1 Run targeted governance guardrail tests.
- [x] 5.2 Run existing governance diff checker and drift detector tests to confirm no regressions.
- [x] 5.3 Run OpenSpec validation for the change.
- [x] 5.4 Update task checkboxes as each implementation step completes.
