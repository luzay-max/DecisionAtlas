## Context

Imported drift evaluation is now operational, but the semantic layer is still too permissive. The current classifier mostly looks at the top recalled accepted decision, a score threshold, and a small set of replacement/review markers. That makes broad follow-up artifacts such as changelogs, contributing docs, and implementation-planning notes look more decisive than they really are, especially when they overlap topically with an accepted decision.

The product consequence is straightforward: drift alerts exist, but some of them read more like "related artifact found" than "this decision may have changed." This is now the main quality gap in the imported-repository loop because workspace reuse, import resilience, extraction conversion, and why-search support grading have already been improved.

## Goals / Non-Goals

**Goals:**
- Make `possible_supersession` harder to emit than it is today.
- Reduce broad-document false positives without weakening genuinely strong drift signals.
- Distinguish "needs human review" from "likely superseded" more clearly in both classifier output and user-facing copy.
- Keep the current manual drift evaluation flow and accepted-decision trust boundary intact.

**Non-Goals:**
- Add continuous monitoring or automatic re-evaluation.
- Redesign rule-first drift extraction.
- Introduce new alert types beyond tightening the current semantic ones.
- Rebuild semantic recall or indexing in the same change.

## Decisions

### Require stronger supersession evidence than lexical overlap
`possible_supersession` should require a combination of factors rather than a single score threshold plus one replacement marker. The classifier should look for stronger replacement language and avoid treating generic follow-up text as evidence of replacement by default.

Alternative considered:
- Keep existing thresholds and only rewrite UI copy.
  Rejected because noisy alerts would still be created and review load would stay high.

### Treat broad artifact families conservatively
Broad artifacts such as changelogs, contributing docs, roadmap notes, and implementation-phase material should be penalized or blocked from escalating directly to `possible_supersession` unless their text contains unusually explicit replacement semantics.

Alternative considered:
- Exclude broad document families from drift entirely.
  Rejected because they can still contain useful `needs_review` signals.

### Preserve `needs_review` as the default semantic fallback
When an artifact is related enough to matter but not strong enough to claim replacement, the system should prefer `needs_review` over `possible_supersession`.

Alternative considered:
- Return no alert for all ambiguous semantic matches.
  Rejected because it would hide useful follow-up artifacts that still deserve review.

### Improve alert summaries and confidence semantics together
The classifier and UI should move together: summaries should read like cautious review guidance, and confidence labels should reflect that `possible_supersession` is a stronger claim than `needs_review`.

Alternative considered:
- Change backend behavior only.
  Rejected because the current wording itself contributes to the feeling that alerts are overclaiming.

## Risks / Trade-offs

- **Real supersession alerts may decrease initially** → Start by optimizing precision rather than recall and validate against known live-repo cases.
- **Broad-doc suppression could hide meaningful signals** → Allow those artifacts to continue producing `needs_review` when overlap is real.
- **Semantic thresholds may become harder to reason about** → Keep the first pass rule-based and artifact-family-aware rather than introducing a more opaque scoring model.
- **UI wording changes can drift from backend semantics** → Update API expectations and web tests in the same change.

## Migration Plan

- No schema migration is required.
- Roll out by updating classifier logic, alert summaries, and drift UI copy together.
- If the change over-suppresses alerts, rollback is straightforward because behavior is code-only and alert generation is recomputed during manual drift evaluation.

## Open Questions

- Whether changelog-like artifacts should be fully blocked from `possible_supersession` or merely require a stronger evidence threshold.
- Whether confidence labels should remain `low`/`medium` strings or evolve into more product-specific wording in a later change.
