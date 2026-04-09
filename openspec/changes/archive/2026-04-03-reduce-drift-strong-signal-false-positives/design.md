## Context

Imported drift now has better grouping, stronger boundary checks, and stale-alert replacement, but the strongest alert lane still over-fires in some real repository cases. In `browser-use`, several later bugfixes, lifecycle fixes, and support-path cleanups still reach `possible_supersession` even though they appear to preserve the broader accepted choice and mainly repair or extend the same implementation path.

The remaining issue is no longer storage or stale rows. It is a classifier precision problem inside the stronger-signal boundary: some artifacts contain replacement-heavy wording while still behaving more like implementation maintenance than decision replacement.

## Goals / Non-Goals

**Goals:**
- Reduce false positives in `possible_supersession` for implementation-heavy fixes and lifecycle repairs.
- Keep clearly relevant artifacts visible through `needs_review` when they do not justify stronger replacement semantics.
- Preserve true decision-layer replacement detection for cases that really indicate the accepted choice is being replaced.
- Validate against the noisy imported `browser-use` cases that still look too strong today.

**Non-Goals:**
- Rework follow-up grouping again.
- Change stale-alert replacement behavior.
- Change manual drift evaluation flow or UI structure.
- Modify why-search, extraction, or indexing behavior.

## Decisions

### 1. Stronger signals will require replacement intent plus decision displacement
Replacement wording alone is no longer enough for `possible_supersession`. The classifier should also look for evidence that the newer artifact is displacing the accepted decision's rationale or operational contract, not merely touching a component, dependency, or lifecycle detail within the same chosen path.

This is preferable to the current behavior because implementation fixes often contain replacement verbs while preserving the same broader decision.

### 2. Bugfix and maintenance patterns should bias toward weaker review semantics
Artifacts dominated by bugfix, stability, test, transport, cookie, websocket, or lifecycle repair language should be harder to promote into `possible_supersession` unless there is unusually explicit evidence that the accepted decision itself is being retired.

This is preferable to suppressing them entirely because they can still matter for human review.

### 3. Real noisy cases should be captured as first-class regressions
The implementation should encode the current noisy imported cases as regression tests so future classifier tweaks do not reintroduce strong-signal false positives.

This is preferable to relying on ad hoc manual checks because the problem is subtle and easy to regress.

## Risks / Trade-offs

- [Risk] The classifier may become too conservative and hide real decision replacement. → Mitigation: keep very explicit retire/replace/migrate-away signals eligible for stronger alerts when they clearly target the accepted decision layer.
- [Risk] Heuristics may become too repository-specific. → Mitigation: frame the rules around maintenance and implementation patterns rather than around a single project name.
- [Risk] Some borderline cases may still need human review. → Mitigation: bias them into `needs_review` instead of dropping them.

## Migration Plan

1. Tighten classifier heuristics for implementation-heavy fixes and lifecycle repairs.
2. Add regression coverage for browser-use style noisy cases that should remain weaker.
3. Re-run drift engine/API/web tests plus targeted imported-case validation.

## Open Questions

- None for this slice. The next missing signal is already visible in the current imported drift output.
