## Context

DecisionAtlas already stores governance rule lifecycle metadata (`current`, `stale`, `superseded`) and keeps stale or superseded rules out of authoritative checker input. That metadata is currently mostly prepared state: reviewers can accept or reject drafts, and the UI can display lifecycle fields, but there is no explicit human workflow to mark an accepted rule stale, supersede one accepted rule with another, or explain the lifecycle decision.

The next quality step is not more extraction metadata. It is lifecycle review: accepted governance rules need a controlled way to evolve as project decisions change, while AI agents and local checkers continue to treat only current accepted rules as authoritative.

## Goals / Non-Goals

**Goals:**

- Add an explicit lifecycle transition path for accepted governance rules.
- Let reviewers mark accepted rules `stale` with bounded rationale.
- Let reviewers mark accepted rules `superseded` by another accepted current rule with bounded rationale and a supersession reference.
- Keep `review_state` and `lifecycle_status` separate.
- Preserve lifecycle decisions in API responses, UI cards, checker traceability, and drift evidence.
- Keep all lifecycle operations human-driven and advisory.

**Non-Goals:**

- No automatic stale detection.
- No automatic rule replacement.
- No LLM rule judge.
- No knowledge graph UI.
- No default CI enforcement.
- No broad permission model redesign beyond using the existing reviewer/admin role boundaries.

## Decisions

1. Use explicit lifecycle transitions instead of overloading review.

   Review answers whether a draft is accepted or rejected. Lifecycle answers whether an accepted rule is still current. Keeping these separate avoids confusing `accepted but stale` with `rejected`, and it preserves old rules as historical evidence rather than deleting them.

2. Limit lifecycle transitions to accepted rules.

   Pending and rejected drafts do not need lifecycle management in this slice. A stale or superseded state only matters after a rule has become accepted and potentially authoritative. This keeps UI and API behavior bounded.

3. Require human rationale for lifecycle changes.

   Marking a rule stale or superseded changes what the checker treats as authoritative. The transition should preserve a bounded human rationale so future reviewers and AI agents can understand why the rule stopped applying.

4. Represent supersession as a reference to another accepted current rule.

   `superseded_by_rule_id` should point to the replacement rule where possible. The replacement should be accepted and current at transition time. The system should reject self-supersession and references outside the current owner scope.

5. Keep checker semantics current-only.

   The diff checker should continue to use accepted active current rules as authoritative input. Stale and superseded rules can appear in traceability or drift evidence, but they must not create blocker findings by themselves.

6. Use drift to surface lifecycle misuse, not to mutate lifecycle.

   If old stale or superseded guidance appears to be reused, the drift detector should produce a human decision signal. It should not rewrite lifecycle fields or create replacement rules automatically.

## Risks / Trade-offs

- [Risk] Reviewers mark useful rules stale too casually. Mitigation: require rationale and keep the source-linked historical record visible.
- [Risk] Supersession chains become confusing. Mitigation: first version supports one direct replacement reference and validates that the replacement is accepted and current.
- [Risk] Lifecycle transitions get mistaken for enforcement. Mitigation: docs and UI keep advisory-first language and checker behavior remains current-only.
- [Risk] UI becomes cluttered. Mitigation: expose lifecycle actions only on accepted rule cards and keep pending draft review unchanged.
- [Risk] Drift detector over-reports old rule reuse. Mitigation: keep stale/superseded reuse as advisory evidence requiring human review, not as automatic blocker or mutation.

## Migration Plan

No new table is expected because lifecycle columns already exist. Implementation should add API/repository behavior, validation, UI controls, and tests around existing fields.

If an implementation discovers that `lifecycle_rationale` or lifecycle transition history is needed beyond current fields, prefer a bounded additive field or serialized metadata rather than changing existing review state semantics. Existing accepted rules should remain `current` by default.
