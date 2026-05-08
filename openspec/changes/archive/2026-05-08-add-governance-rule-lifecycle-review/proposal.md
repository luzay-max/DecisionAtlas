## Why

Governance rule drafts now preserve lifecycle metadata, but accepted rules still behave mostly like static records: reviewers cannot explicitly mark a rule stale, supersede it with another rule, or explain lifecycle changes through the product flow. This change turns prepared lifecycle metadata into a human-reviewed rule evolution loop so accepted governance rules can remain trustworthy over time.

## What Changes

- Add a human-reviewed lifecycle transition path for accepted governance rules.
- Let reviewers mark accepted rules as `stale` with bounded rationale.
- Let reviewers mark accepted rules as `superseded` by another accepted current rule with bounded rationale and a supersession reference.
- Keep `review_state` separate from `lifecycle_status`: review state records whether a draft was accepted or rejected, while lifecycle status records whether an accepted rule remains authoritative.
- Update governance UI/API surfaces so lifecycle transitions are explicit, source-linked, and auditable.
- Ensure checker/guardrail inputs continue to use only accepted active current rules.
- Improve drift reporting when inactive, stale, or superseded governance rules appear to be reused as active guidance.

## Capabilities

### New Capabilities

### Modified Capabilities

- `governance-markdown-ingest`: add explicit human lifecycle review operations for accepted rules, including stale and superseded transitions with rationale.
- `governance-diff-checker`: clarify that only accepted active current rules remain authoritative and preserve supersession traceability where stale or superseded rules are encountered.
- `governance-drift-detection`: surface stale or superseded rule reuse as a human decision signal with enough evidence to decide whether to keep, replace, or create a new rule.

## Impact

- Engine API and repository methods for rule lifecycle transition.
- Governance rule serialization and validation for bounded lifecycle rationale and supersession references.
- Web governance page controls for marking accepted rules stale or superseded.
- Governance checker and drift detector tests for current-only authority and stale/superseded evidence.
- Documentation and OpenSpec specs describing lifecycle semantics and advisory boundaries.
