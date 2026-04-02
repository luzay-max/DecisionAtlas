## Context

Imported drift reevaluation now produces better semantics for some noisy artifacts, but the stored alert set can still contain stale rows from earlier runs. The visible failure mode is a single artifact-decision thread showing both an older `possible_supersession` alert and a newer `needs_review` alert after reevaluation, which makes the latest classifier result look inconsistent.

The current drift flow already recreates grouped weak follow-up alerts, but it does not guarantee that obsolete alerts of a different type are removed when the latest semantic outcome changes. This change is about storage replacement semantics during reevaluation, not about classifier quality.

## Goals / Non-Goals

**Goals:**
- Ensure reevaluation keeps one current alert outcome per artifact-decision thread.
- Remove obsolete alerts when the same artifact and accepted decision are reclassified from one semantic level to another.
- Preserve grouped follow-up behavior and stronger supersession alerts that still remain valid in the latest run.
- Keep drift UI consistent with the latest reevaluation result set.

**Non-Goals:**
- Rework semantic drift classification again.
- Change manual drift evaluation flow or trigger timing.
- Introduce historical alert versioning in the product UI.
- Redesign the drift schema beyond what is needed to replace stale alerts safely.

## Decisions

### 1. Reevaluation will treat the latest run as the source of truth for a workspace
Before persisting fresh semantic alerts, reevaluation should clear or replace obsolete semantic alert rows for the workspace so only the latest conclusions remain visible.

This is preferable to incremental append behavior because the product currently reads the active drift table as current truth, not as an audit log.

### 2. Replacement should happen at the semantic-alert layer, not only per alert type
Deleting only one alert type is not sufficient because the same artifact-decision thread can move between `possible_supersession` and `needs_review`. Reevaluation should remove stale semantic alerts broadly enough that a downgraded or upgraded thread cannot leave contradictory rows behind.

This is preferable to narrower cleanup because the bug is specifically caused by cross-type leftovers.

### 3. Grouped weak follow-ups remain regenerated from the latest evaluator state
Grouped `needs_review` follow-up alerts should continue to be rebuilt from the current evaluator run after stale semantic rows are removed.

This is preferable to partial in-place updates because grouped alerts are aggregate outputs, and regeneration is simpler and less error-prone than trying to diff individual members.

## Risks / Trade-offs

- [Risk] Broad cleanup could remove alerts that should remain visible. → Mitigation: scope replacement to semantic drift alerts for the reevaluated workspace and immediately rebuild the latest result set in the same run.
- [Risk] Losing old rows means there is no implicit history in the active alert table. → Mitigation: accept this because the UI already treats the table as current state, not historical audit state.
- [Risk] Future alert families may need different persistence semantics. → Mitigation: keep cleanup logic scoped to semantic reevaluation output and avoid changing unrelated drift storage paths.

## Migration Plan

1. Update reevaluation persistence so stale semantic alerts are removed before new alerts are written.
2. Run existing drift evaluator, API, and UI regressions plus a stale-alert replacement case.
3. Roll back by restoring the prior persistence path if replacement unexpectedly hides valid current alerts.

## Open Questions

- None for this slice. The user-visible bug and the replacement boundary are already clear from the imported browser-use reevaluation case.
