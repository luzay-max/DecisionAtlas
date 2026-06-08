## Why

DecisionAtlas has the core self-hosted team loop in place, but a small team still needs a clear handoff artifact that explains what was imported, what was reviewed, what drift remains, and what evidence supports a release or delivery decision. Without a repeatable report, the product is useful internally but harder to sell, demo, or hand over to a customer/operator.

## What Changes

- Add a team handoff reporting capability that generates customer/operator-readable JSON and Markdown reports.
- Summarize workspace scope, repository sources, decisions, review/audit activity, drift status, governance readiness, benchmark evidence, hosted readiness, and known limitations.
- Include role-aware reporting boundaries so viewer/reviewer/admin audiences can consume the same evidence without exposing credentials or secrets.
- Add CLI/reporting entry points that can be used in release rehearsal and self-hosted delivery workflows.
- Add tests and a real browser/operator rehearsal for reading the generated Markdown report as a handoff artifact.

## Capabilities

### New Capabilities

- `team-handoff-reporting`: Generates team/customer handoff reports from workspace, decision, drift, audit, readiness, and benchmark evidence.

### Modified Capabilities

- `readiness-evidence-history`: Handoff reports reference archived readiness evidence as source material instead of duplicating one-off outputs.
- `collaborative-review-audit-trail`: Handoff reports include compact review/audit history summaries without exposing sensitive actor credentials.
- `offline-self-hosted-release-package`: Self-hosted package documentation points operators to handoff report generation as part of delivery acceptance.

## Impact

- Adds reporting scripts or service helpers for JSON/Markdown report generation.
- May add lightweight API or repository read paths if existing reporting data is not already exposed in one place.
- Updates docs for self-hosted handoff and release rehearsal usage.
- Adds tests under backend/reporting and smoke/operator evidence under `.tmp` during validation.
