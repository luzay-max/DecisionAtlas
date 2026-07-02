## Why

DecisionAtlas already has self-hosted package verification, clean install rehearsal, delivery rehearsal, and backup/restore/upgrade evidence, but the strongest remaining commercial gap is proof from a non-developer or customer-controlled environment. This change makes external self-hosted install evidence explicit, sanitized, and reusable in release, handoff, and Code Decision Audit materials without pretending that local clean-install evidence proves customer-host readiness.

## What Changes

- Add a bounded external install evidence collector/verifier for operator-submitted evidence from a clean VM, another machine, or customer-controlled host.
- Generate JSON and Markdown summaries that distinguish `passed`, `warning`, `operator_guided`, `not_provided`, and `blocked` states.
- Require evidence for package identity, host profile, startup checks, health checks, browser smoke, public repository import or explicit operator-guided outcome, readiness evidence, and sensitive-material redaction.
- Integrate external install evidence into self-hosted handoff and commercial readiness language so customer-facing claims do not overstate local-only validation.
- Preserve current self-hosted package and clean-install flows; this change adds an external evidence layer rather than replacing them.

## Capabilities

### New Capabilities

- `external-self-hosted-install-evidence`: Defines how DecisionAtlas records and verifies external or customer-controlled self-hosted install evidence.

### Modified Capabilities

- `clean-self-hosted-install-rehearsal`: Clarify that clean local rehearsals are not a substitute for external/customer-host install evidence.
- `self-hosted-delivery-rehearsal`: Allow delivery rehearsal summaries to reference external install evidence when present and disclose missing external evidence when absent.
- `team-handoff-reporting`: Include external install evidence status in customer handoff reports without exposing secrets or private repository content.
- `code-decision-audit-report-builder`: Allow Code Decision Audit outputs to reference external install readiness when sanitized evidence is provided.

## Impact

- New or updated CI/operator script for external install evidence collection and verification.
- Templates for external host evidence input.
- Documentation under `docs/project/` describing how to run and interpret external install evidence.
- Tests for evidence schema, redaction, status classification, and downstream report integration.
- OpenSpec specs for external evidence and updated self-hosted/handoff/audit requirements.
