## Why

The guided demo lane is now stable, but the imported-workspace lane still too often ends in thin candidate output, weak why-answer coverage, or drift surfaces that are hard to use operationally. The next slice should improve whether a real public repository can produce useful decisions, credible answers, and actionable drift evaluation instead of only a successful import job.

## What Changes

- Improve the real imported-workspace path so live analysis produces more reviewable candidate decisions from high-signal repository evidence.
- Add clearer imported-workspace outcome and readiness summaries so users know whether to review, ask why, re-run drift, or treat the run as evidence-limited.
- Tighten imported why-answer behavior so answers are grounded in accepted imported decisions with citations or fail with a more actionable explanation.
- Make drift more usable on imported workspaces with explicit evaluation status, clearer empty states, and a more operational evaluation flow.
- Add outcome-oriented validation against curated public repositories so the team can measure whether real runs are getting more useful over time.

## Capabilities

### New Capabilities
- `real-repository-outcomes`: imported-workspace readiness, imported why-answer trust signals, and operational drift evaluation behavior for real repository analysis

### Modified Capabilities
- `live-repository-analysis`: live analysis outcomes should communicate real-workspace usefulness and strongest next action, not only job success vs failure
- `repository-document-ingest`: imported repository evidence selection should prioritize more rationale-heavy markdown sources and report stronger evidence contribution context

## Impact

- `services/engine`: import summarization, extraction inputs, why-answer gating, drift evaluation status, benchmark validation
- `apps/api`: read-model responses for dashboard, query, and drift evaluation flows
- `apps/web`: imported workspace dashboard, why-search, drift page, and empty/error states
- docs and validation: release checklist, benchmark corpus, and operator guidance for real repository runs
