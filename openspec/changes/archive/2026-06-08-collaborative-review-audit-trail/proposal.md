## Why

DecisionAtlas is now moving from a single-operator analysis tool into a small-team self-hosted product, but review actions are still mostly represented as final state. Teams need a durable responsibility trail that explains who accepted, rejected, superseded, or handled governance/drift items and why.

## What Changes

- Add a shared audit trail capability for human review actions across decisions, governance rules, lifecycle transitions, and drift handling.
- Record actor username, role, owner scope, workspace when applicable, target type/id, action, previous state, new state, bounded rationale, and timestamp.
- Expose audit history through backend APIs and product surfaces so admins/reviewers/viewers can inspect “who did what and why” without seeing secrets.
- Preserve existing simple review actions; this change adds traceability rather than introducing a separate approval workflow.
- Keep drift handling minimal: add a bounded manual action path for recording alert disposition and audit history, not a full incident management system.

## Capabilities

### New Capabilities

- `collaborative-review-audit-trail`: durable team audit events for review, lifecycle, and drift handling actions.

### Modified Capabilities

- `imported-review-decision-quality`: decision review responses and product surfaces include bounded review history.
- `governance-markdown-ingest`: governance rule review and lifecycle transitions create and expose audit events.
- `governance-drift-detection`: drift alerts can be manually dispositioned with audited actor/rationale history.

## Impact

- Engine database model and Alembic migration for audit events and drift alert update metadata.
- Engine decision, governance, and drift APIs plus repository helpers.
- API gateway proxy routes for new audit/drift action endpoints if needed.
- Web API types and review/governance/drift UI surfaces to show history.
- Backend, API gateway, web unit tests, plus local browser/operator rehearsal.
