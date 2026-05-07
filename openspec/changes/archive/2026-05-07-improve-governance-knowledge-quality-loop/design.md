## Context

Governance Markdown ingest currently creates rule drafts through a deterministic section parser. The parser is intentionally local and provider-free, but it treats broad language such as `must`, `shall`, `should`, or `规范` as enough evidence to create a draft. That is useful for a prototype and too noisy for an accepted-rule loop, because accepted rules now feed the local diff checker and agent guardrail.

The current rule draft model already stores title, description, severity, scope, rationale, source excerpt, review state, and reviewer metadata. The review API only accepts `accepted` or `rejected`, and the product surface shows pending and accepted rules with a collapsible source excerpt. There is no stored review rationale, document-type-aware rule classification, extraction reason, or lifecycle marker for stale or superseded rules.

## Goals / Non-Goals

**Goals:**

- Make deterministic extraction stricter without requiring live AI provider credentials.
- Preserve enough metadata for reviewers to understand why a section became a rule draft.
- Capture reviewer rationale for both accepted and rejected drafts.
- Let reviewers filter accepted rules and inspect source evidence quickly.
- Keep accepted rules traceable through diff checker and agent guardrail outputs.
- Prepare explicit stale and superseded metadata for later lifecycle work.

**Non-Goals:**

- No automatic rule acceptance.
- No full knowledge graph UI.
- No enterprise permission model changes.
- No CI enforcement mode.
- No LLM-backed governance extraction in this change.
- No automatic stale or superseded rule detection.

## Decisions

1. Keep extraction deterministic and document-type-aware.

   The extractor should continue running without provider credentials, but it should use stronger signals than generic modal verbs. Rule-like headings, explicit markers, checklist commands, postmortem lesson sections, decision outcome sections, and anti-pattern prohibitions should carry more weight than ordinary prose. This keeps local validation stable and avoids adding a new operational dependency. The alternative was LLM classification; that would be more flexible but would make tests and local workflow less predictable.

2. Store extraction metadata on the rule draft.

   Add bounded metadata such as `rule_type`, `extraction_reason`, and source document type context to serialized rule drafts. `rule_type` should use a small vocabulary, for example `standard`, `postmortem_lesson`, `decision_rule`, and `anti_pattern`. `extraction_reason` should be human-readable and deterministic, such as `rule heading with severity marker` or `anti-pattern prohibition marker`. The alternative was to infer these in the UI, but that would duplicate extraction logic and weaken API traceability.

3. Capture review rationale as part of the review transition.

   The review request should accept an optional bounded `review_rationale`. It should be stored with the draft and returned in rule listings. Reject rationale is especially important because rejected drafts are not authoritative, while accept rationale helps explain why a noisy or contextual source became an accepted rule.

4. Prepare lifecycle metadata without implementing automatic lifecycle transitions.

   Add explicit fields or serialized metadata for stale and superseded preparation, such as a lifecycle status and optional supersession reference. This change should only allow humans or future code to represent the state; it should not infer stale rules automatically. That keeps stage 10 focused on quality and traceability.

5. Extend checker output by passing accepted-rule metadata through, not by changing enforcement semantics.

   The diff checker should still only use accepted and active rules as authoritative input. It should include review rationale and lifecycle/source metadata in matched rules and findings where available. Pending, rejected, stale, or superseded rules must not become authoritative checker input.

## Risks / Trade-offs

- [Risk] Stricter extraction misses valid rules written as prose. Mitigation: support explicit markers and document-type-specific patterns, and make source documents persist even when they create no drafts.
- [Risk] More metadata increases migration and API surface area. Mitigation: use bounded string fields and keep values optional where possible.
- [Risk] Review rationale becomes noisy if free-form text is unbounded. Mitigation: enforce API-side trimming and length limits.
- [Risk] Lifecycle preparation is mistaken for full lifecycle management. Mitigation: document that stale and superseded states are manual or future-facing and do not run automatic replacement.
- [Risk] Checker output changes break consumers. Mitigation: add fields additively and preserve existing status, findings, matched_rules, conflicts, required_tests, and recommended_next_action fields.

## Migration Plan

- Add a schema migration for bounded rule draft review and lifecycle metadata.
- Backfill existing rule drafts with safe defaults: existing accepted rules stay active, pending drafts stay pending, and lifecycle metadata defaults to current.
- Update serializers and TypeScript types additively.
- Update tests and fixtures before changing extractor behavior so quality regressions are visible.
- Rollback can remove the additive fields and keep existing rule draft records because existing core columns remain unchanged.

## Resolved Questions

- `review_rationale` is optional for both accepted and rejected rules in this slice, with API-side trimming and length bounding.
- Stale and superseded state uses separate `lifecycle_status` metadata so `review_state` continues to represent human review state and `status` continues to represent active or rejected storage state.
