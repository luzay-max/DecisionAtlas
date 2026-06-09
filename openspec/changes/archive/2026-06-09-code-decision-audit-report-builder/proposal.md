## Why

DecisionAtlas has a Code Decision Audit template and readiness evidence, but producing a customer-readable audit report is still manual. This blocks the commercialization plan's "可销售交付物" step because a maintainer must hand-copy release, readiness, benchmark, and handoff evidence into a report.

## What Changes

- Add a local Code Decision Audit report builder that reads explicit evidence JSON inputs and writes customer-readable JSON/Markdown.
- Preserve non-clean evidence states such as `warning`, `operator_guided`, `known_limitation`, and `not_provided`.
- Include commercial tier fit, limitations, evidence table, benchmark trend/coverage summary, and recommended next actions.
- Update docs so paid pilots can generate a report without exposing secrets or raw private repository content.
- Keep the command offline and deterministic; no GitHub, provider, or live API dependency.

## Capabilities

### New Capabilities
- `code-decision-audit-report-builder`: Builds customer-readable Code Decision Audit reports from explicit release, readiness, benchmark, handoff, and license/support evidence.

### Modified Capabilities
- `team-handoff-reporting`: Handoff reports can be used as source evidence for customer audit reports.
- `offline-self-hosted-release-package`: Self-hosted delivery docs reference audit report generation for paid pilots.

## Impact

- Affected code: new `scripts/ci/collect_code_decision_audit_report.py`, tests under `services/engine/tests/ci/`.
- Affected docs: Code Decision Audit template, release checklist, self-hosted/pilot handoff docs, update log.
- No runtime API, database, frontend, live provider, or network dependency.
