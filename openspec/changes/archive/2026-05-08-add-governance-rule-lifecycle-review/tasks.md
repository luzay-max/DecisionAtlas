## 1. Lifecycle API And Repository

- [x] 1.1 Inspect existing governance rule draft model, serializer, repository, and API review endpoint to identify the smallest lifecycle transition surface.
- [x] 1.2 Add a lifecycle transition request contract for accepted rules covering `stale`, `superseded`, bounded rationale, and optional `superseded_by_rule_id`.
- [x] 1.3 Implement repository validation so lifecycle transitions only apply to accepted rules in the current owner scope.
- [x] 1.4 Reject self-supersession and invalid supersession targets such as missing, pending, rejected, stale, superseded, or cross-owner rules.
- [x] 1.5 Preserve `review_state=accepted` while updating `lifecycle_status`, `superseded_by_rule_id`, and lifecycle rationale or equivalent audit metadata.

## 2. Governance Product Surface

- [x] 2.1 Extend TypeScript API types and client helper functions for lifecycle transition requests and responses.
- [x] 2.2 Add accepted-rule lifecycle actions on the governance page for marking current rules stale with rationale.
- [x] 2.3 Add accepted-rule lifecycle actions for superseding a current rule with another accepted current rule.
- [x] 2.4 Update the governance page state without full reload after lifecycle transitions.
- [x] 2.5 Keep lifecycle actions unavailable for pending, rejected, stale, and superseded rules.

## 3. Checker And Drift Behavior

- [x] 3.1 Add checker coverage proving current replacement rules remain authoritative.
- [x] 3.2 Add checker coverage proving stale and superseded rules remain non-authoritative while lifecycle traceability is preserved.
- [x] 3.3 Extend drift detector evidence or tests so stale/superseded rule reuse produces a human-review lifecycle signal.
- [x] 3.4 Ensure guardrail questions or recommended actions explain lifecycle misuse without treating inactive rules as authoritative blockers.

## 4. Tests And Documentation

- [x] 4.1 Add engine API tests for stale transition, superseded transition, invalid targets, owner-scope validation, and review/lifecycle separation.
- [x] 4.2 Add web governance page tests for lifecycle controls, rationale submission, replacement selection, and no-reload state update.
- [x] 4.3 Update governance documentation to explain review state versus lifecycle status and advisory-first lifecycle behavior.
- [x] 4.4 Run targeted engine governance tests.
- [x] 4.5 Run targeted web governance page tests.
- [x] 4.6 Run `openspec validate --all --strict`.
- [x] 4.7 Run `python scripts/governance/agent_guardrail.py --protocol-status --summary` and record any caution or pause evidence in the implementation handoff.
