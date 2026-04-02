## Context

The project already reduced broad-document false positives and grouped repeated weak follow-up alerts, but imported drift still has a remaining issue: some later artifacts that replace a library, execution path, or supporting browser primitive are being interpreted as replacing the accepted decision itself. In repositories like `browser-use`, this makes `possible_supersession` too eager when later work still appears to implement the same higher-level choice.

The current classifier relies on explicit replacement language plus semantic overlap. That is necessary but no longer sufficient. The next step is to distinguish “replace the implementation under the same rationale” from “replace the accepted decision.”

## Goals / Non-Goals

**Goals:**
- Tighten the supersession bar so implementation substitutions stay out of `possible_supersession` more often.
- Preserve `needs_review` for related but weaker change signals.
- Keep truly strong decision-replacement signals eligible for `possible_supersession`.
- Improve imported drift readability without hiding meaningful change.

**Non-Goals:**
- Rework drift grouping again.
- Change manual drift evaluation flow.
- Redesign the broader drift storage model.
- Modify why-search, extraction, or indexing behavior.

## Decisions

### 1. Supersession should require evidence about the decision layer, not only the implementation layer
The classifier should look for signs that the later artifact is replacing the accepted choice itself, not merely swapping a mechanism used to carry it out. Strong lexical replacement language alone is insufficient if the later artifact still appears to preserve the same chosen option at a higher level.

This is preferable to the current approach because many real repositories use “replace” language for transport, browser, library, or internal plumbing changes while keeping the broader product or operational decision intact.

### 2. Implementation substitutions should fall back to `needs_review`
When a later artifact is strongly related but the replacement appears scoped to an implementation primitive, dependency, or execution path, the signal should remain reviewable through `needs_review` rather than `possible_supersession`.

This is preferable to suppressing the signal completely because these artifacts are still relevant for human review.

### 3. Strong explicit decision replacement should still win
If the later artifact clearly indicates the accepted decision is being retired, replaced, or migrated away from at the same layer of abstraction, the classifier should still allow `possible_supersession`.

This is preferable to making the classifier so conservative that meaningful decision replacement becomes invisible.

### 4. Validation must use previously noisy real-repo cases
The change should be verified against imported repository examples where implementation substitutions previously over-triggered `possible_supersession`, especially browser-use cases involving lower-level browser control or transport changes.

This is preferable to relying only on synthetic test strings because the problem is fundamentally about abstraction level in real repository language.

## Risks / Trade-offs

- [Risk] The classifier may become too conservative and miss real supersession. → Mitigation: keep stronger explicit decision-retirement and migration signals as independent triggers.
- [Risk] Abstraction-level heuristics may be brittle across repositories. → Mitigation: validate on noisy imported cases and keep the fallback path as `needs_review`, not silence.
- [Risk] Users may still find some `possible_supersession` alerts too strong. → Mitigation: keep wording cautious and continue separating alert semantics from confirmed replacement.
