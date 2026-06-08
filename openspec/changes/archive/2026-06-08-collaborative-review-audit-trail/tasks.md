## 1. Data Model and Repository

- [x] 1.1 Add Alembic migration for `review_audit_events` and drift alert disposition metadata.
- [x] 1.2 Add SQLAlchemy model and repository helpers for creating and listing bounded audit events.
- [x] 1.3 Add safe audit serialization with actor, role, target, state transition, rationale, and timestamp.

## 2. Engine API Integration

- [x] 2.1 Record audit events when decision review state changes.
- [x] 2.2 Record audit events when governance rule drafts are accepted or rejected.
- [x] 2.3 Record audit events when governance rules are marked stale or superseded.
- [x] 2.4 Add drift alert disposition endpoint that updates status and records audit history.
- [x] 2.5 Expose target-scoped audit history on decision, governance rule, and drift alert responses.

## 3. API Gateway and Web Surfaces

- [x] 3.1 Proxy any new audit or drift disposition routes through the Fastify API gateway.
- [x] 3.2 Update Web API types and clients for audit events and drift disposition.
- [x] 3.3 Show compact review history on decision detail and governance rule cards.
- [x] 3.4 Show compact drift handling history and reviewer disposition controls on drift alert detail.

## 4. Tests and Validation

- [x] 4.1 Add engine API tests for decision, governance, lifecycle, and drift audit events.
- [x] 4.2 Add API gateway tests for new proxy behavior.
- [x] 4.3 Add Web tests for visible audit history and role-bounded drift disposition.
- [x] 4.4 Run targeted backend, API, Web, and OpenSpec strict validation.
- [x] 4.5 Run browser/operator rehearsal for review history and drift disposition on the real local stack.

## 5. Documentation and Archival

- [x] 5.1 Update team self-hosted documentation with the collaboration audit boundary.
- [x] 5.2 Record update-log evidence including tests and browser rehearsal.
- [x] 5.3 Sync specs, archive the OpenSpec change, commit, push, and confirm CI.
