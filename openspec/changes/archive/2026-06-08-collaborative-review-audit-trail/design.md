## Context

The product already has team accounts, workspace roles, decision review actions, governance rule review/lifecycle metadata, and drift alert display. The missing layer is durable collaboration history: state transitions overwrite the current record but do not provide a consistent product-readable timeline of human actions.

This change cuts across Engine persistence, Engine APIs, API gateway proxying, and Web review/governance/drift surfaces. It must preserve current simple review workflows while adding traceability suitable for small-team self-hosted deployments.

## Goals / Non-Goals

**Goals:**

- Persist a bounded audit event for decision review, governance rule review, governance lifecycle, and drift alert disposition actions.
- Include actor username, actor role, owner scope, workspace when applicable, target type/id, action, previous state, new state, rationale, and timestamp.
- Expose audit events on existing detail/list responses where useful and through target-scoped history endpoints.
- Show compact “review history” in Web surfaces without turning DecisionAtlas into a full project-management tool.
- Keep token, local path, and secret material out of audit event payloads.

**Non-Goals:**

- No generic enterprise audit log search UI in this change.
- No immutable cryptographic event store or tamper-proof signing.
- No complex approval workflow, review undo workflow, or assignment queue.
- No broad incident-management system for drift alerts.

## Decisions

1. Use one shared `review_audit_events` table instead of separate history tables.

   Rationale: decision, governance, and drift actions share the same core event shape. A single table keeps API serialization and future evidence/report generation simpler.

   Alternative considered: per-domain tables such as `decision_review_events` and `governance_rule_events`. That would preserve stronger foreign keys but duplicate query and UI code.

2. Store target identity as bounded polymorphic fields.

   Rationale: `target_type`, `target_id`, optional `workspace_id`, and optional `owner_scope` are enough for current product surfaces. This avoids premature schema coupling while still enabling scoped queries.

   Alternative considered: strict nullable foreign keys for every target domain. This is safer relationally but heavier to evolve as new audited target types are added.

3. Record previous/new state snapshots as small JSON objects.

   Rationale: decisions use `review_state/status`, governance uses `review_state/status/lifecycle_status/superseded_by_rule_id`, and drift uses `status`. JSON snapshots preserve enough context without adding many nullable columns.

   Alternative considered: flat columns for `previous_state` and `new_state` strings. That would be easier but lose lifecycle and supersession context.

4. Add drift disposition as a bounded manual action.

   Rationale: P2 requires drift handling records, but the current drift product is read-oriented. A small endpoint that updates status plus rationale gives teams a real audit trail without building a full alert workflow.

   Alternative considered: defer drift handling entirely. That would leave the P2 responsibility chain incomplete.

5. Serialize audit history compactly on detail/list surfaces.

   Rationale: users should see history near the object they are reviewing. Full cross-object audit search can wait for reporting.

   Alternative considered: only provide raw API endpoints. That would be technically complete but weak as a product feature.

## Risks / Trade-offs

- Audit table can become noisy -> Keep scope to human review/disposition actions, not every read or background job.
- Polymorphic target fields lack strict database foreign keys -> Validate target existence in domain APIs before creating events.
- Rationale may contain sensitive text -> Bound length and avoid copying token/path inputs into audit metadata.
- UI can become cluttered -> Show recent compact history first and link/detail only where needed.
- Existing tests may assume exact response shapes -> Add optional fields without removing existing keys.

## Migration Plan

1. Add Alembic migration for `review_audit_events` and drift alert disposition metadata.
2. Add SQLAlchemy model and repository helpers.
3. Create audit events inside existing decision/governance actions and new drift disposition action.
4. Expose histories through target-scoped APIs and compact response fields.
5. Update Web API types and UI rendering.
6. Run targeted backend/API/Web tests, OpenSpec validation, and local browser/operator rehearsal.

Rollback is straightforward for code paths because existing state fields remain authoritative. If needed, disable event writes while preserving current review behavior.

## Open Questions

- Future reporting may need a cross-workspace audit search page, but this change should only expose target-scoped history.
- Future enterprise packaging may require export/signing controls for audit events; that belongs in team reporting or license/support boundary work.
