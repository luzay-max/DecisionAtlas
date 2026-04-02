## Context

The recent drift-precision work reduced false `possible_supersession` alerts from changelogs and other broad documents, but live imported workspaces still show many `needs_review` alerts attached to the same accepted decision. In practice, these alerts often represent implementation follow-ups, bugfixes, or completion work around one accepted decision rather than independent evidence that the decision changed.

The current drift pipeline treats each triggering artifact mostly in isolation. That is enough for broad precision control, but it is not enough to collapse multiple closely related follow-ups into one review thread. This change should improve scanability without weakening the conservative trust boundary around stronger replacement signals.

## Goals / Non-Goals

**Goals:**
- Reduce repeated weak drift alerts around the same accepted decision.
- Distinguish implementation-follow-up work from likely decision change.
- Present grouped follow-up drift results as compact review guidance.
- Preserve stronger `possible_supersession` alerts when replacement evidence exists.

**Non-Goals:**
- Redesign the entire drift model or storage schema.
- Add continuous monitoring or background reevaluation.
- Eliminate all `needs_review` alerts.
- Change review, why-search, or extraction behavior outside drift output semantics.

## Decisions

### 1. Follow-up alerts should collapse by accepted decision and rationale thread
The evaluator should avoid emitting many separate low-signal alerts when multiple later artifacts reinforce the same accepted decision thread. Instead, it should prefer one representative follow-up alert with compact supporting context.

This is preferable to trying to suppress each weak artifact independently because the noisy behavior comes from repetition across artifacts, not just from any single artifact being wrong.

### 2. Implementation-follow-up signals should remain reviewable but weaker
Artifacts that continue rollout, cleanup, bugfixing, or completion work for the same chosen option should remain visible as review material, but they should not be phrased as if they imply a new decision. They should either merge into an existing `needs_review` thread or be suppressed when they add no materially new signal.

This is preferable to dropping all related follow-up alerts because users still benefit from one compact reminder that post-decision work is happening.

### 3. Strong replacement evidence still wins over grouping
If a later artifact contains explicit replacement semantics that satisfy the stronger supersession gate, that signal should still surface independently as `possible_supersession`.

This is preferable to blindly grouping everything because grouping should reduce weak alert spam, not hide stronger change signals.

### 4. UI should make grouped follow-up alerts feel like one thread
The web surface should present grouped or deduplicated follow-up alerts as a compact review thread tied to one accepted decision, rather than as repeated independent warnings with nearly identical wording.

This is preferable to a backend-only change because the user problem is not just alert count; it is also the perception of repeated warning cards.

## Risks / Trade-offs

- [Risk] Grouping rules may hide a meaningful follow-up artifact that deserves separate review. → Mitigation: only group weak `needs_review` alerts and keep stronger supersession signals separate.
- [Risk] Overly aggressive suppression could make drift feel empty. → Mitigation: preserve one representative grouped follow-up alert per accepted decision thread instead of dropping all weak signals.
- [Risk] UI semantics may become harder to explain if grouped alerts have inconsistent summaries. → Mitigation: standardize grouped follow-up wording around “continued implementation or follow-up work.”
- [Risk] Real repositories vary widely in PR naming. → Mitigation: validate on at least one noisy imported workspace and include regression tests for repeated follow-up artifacts.
