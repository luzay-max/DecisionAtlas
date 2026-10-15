## Why

The governance drift detector can emit many visually identical `repeated_postmortem_issue` signals when the same underlying issue appears across archived changes or evidence lines. This hides actionable governance work behind noise and contaminates dashboard, guardrail, and release-evidence summaries, so deduplication must happen at the authoritative detector boundary now.

## What Changes

- Reject false repeated-issue candidates caused by substring matches, negated outcomes, policy mentions, or weak recent-context overlap.
- Add deterministic semantic grouping for governance drift signals instead of relying only on generated signal IDs.
- Merge equivalent findings into one representative signal while preserving distinct evidence references.
- Expose occurrence and source counts so operators can distinguish a recurring pattern from an accidental duplicate.
- Bound merged evidence and ordering deterministically for stable API, CLI, dashboard, and release-evidence output.
- Preserve genuinely distinct findings even when they share a signal type or title.
- Add regression tests and a real-stack/browser rehearsal covering dashboard and guardrail output.

## Capabilities

### New Capabilities
- `governance-drift-finding-deduplication`: Defines semantic identity, evidence aggregation, stable ordering, bounded output, and operator-visible recurrence metadata for governance drift findings.

### Modified Capabilities
- `governance-drift-detection`: Requires detector reports to collapse equivalent signals before status, recommendations, and downstream evidence are computed.

## Impact

- Engine drift detection models and report generation in `services/engine/app/governance/drift_detector.py`.
- Engine governance API serialization and tests.
- Dashboard/guardrail TypeScript contracts and rendering where recurrence metadata is displayed.
- Governance CLI and release/readiness evidence consumers.
- Existing response fields remain compatible; recurrence metadata is additive.
