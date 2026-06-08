## Purpose
Define bounded collaboration audit history for human review actions across decisions, governance rules, governance rule lifecycle, and drift alert disposition.

## Requirements

### Requirement: Human review actions create audit events
The system SHALL persist bounded audit events for human review actions that change decisions, governance rules, governance rule lifecycle, or drift alert disposition.

#### Scenario: Decision review creates audit event
- **WHEN** an authorized reviewer accepts, rejects, supersedes, or restores a candidate decision
- **THEN** the system SHALL persist an audit event with actor username, actor role, owner scope, workspace id, target type `decision`, target id, action, previous state, new state, optional rationale, and timestamp

#### Scenario: Governance review creates audit event
- **WHEN** an authorized reviewer accepts or rejects a governance rule draft
- **THEN** the system SHALL persist an audit event with target type `governance_rule`, review action, previous state, new state, review rationale, and actor metadata

#### Scenario: Governance lifecycle creates audit event
- **WHEN** an authorized reviewer marks an accepted governance rule stale or superseded
- **THEN** the system SHALL persist an audit event with lifecycle action, previous lifecycle state, new lifecycle state, supersession target when present, lifecycle rationale, and actor metadata

#### Scenario: Drift disposition creates audit event
- **WHEN** an authorized reviewer records a manual disposition for a drift alert
- **THEN** the system SHALL persist an audit event with target type `drift_alert`, previous alert status, new alert status, rationale, and actor metadata

### Requirement: Audit events are bounded and safe
The system SHALL keep review audit events bounded, owner-scoped, and free of credential or sensitive local path material.

#### Scenario: Audit event omits credentials
- **WHEN** an audited action occurs near repository access setup, imported repository metadata, or local path configuration
- **THEN** the audit event SHALL NOT include raw tokens, credential secrets, or sensitive local filesystem paths

#### Scenario: Rationale is bounded
- **WHEN** a reviewer submits rationale for an audited action
- **THEN** the system SHALL store a bounded rationale string and reject or trim values that exceed the supported limit

#### Scenario: Viewer reads scoped history
- **WHEN** a viewer reads audit history for an object inside an authorized workspace or owner scope
- **THEN** the system SHALL return only events visible within that viewer's scope and SHALL NOT expose unrelated owner scopes

### Requirement: Audit history is product-readable
The system SHALL expose compact audit history in APIs and product surfaces so team members can understand responsibility and reasoning.

#### Scenario: Target history endpoint returns events
- **WHEN** an authorized actor requests audit history for a decision, governance rule, or drift alert
- **THEN** the system SHALL return events ordered newest-first with actor, role, action, target, state transition, rationale, and timestamp

#### Scenario: Product surface shows recent history
- **WHEN** a decision detail, governance rule card, or drift alert detail is rendered with audit history
- **THEN** the product SHALL show a compact history explaining who changed the item, what changed, when, and why when rationale exists

#### Scenario: Missing history remains bounded
- **WHEN** an older object has no audit events because it predates the audit trail
- **THEN** the product SHALL show current state normally and SHALL NOT imply that history is complete
