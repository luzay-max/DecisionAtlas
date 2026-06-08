## ADDED Requirements

### Requirement: Governance rule review exposes audit history
Governance rule review and lifecycle actions SHALL create and expose bounded audit history while preserving existing review and lifecycle metadata.

#### Scenario: Rule review history is shown
- **WHEN** a governance rule draft has been accepted or rejected by a reviewer
- **THEN** the governance product surface SHALL show audit history with actor, role, action, review state transition, rationale, and timestamp

#### Scenario: Rule lifecycle history is shown
- **WHEN** an accepted governance rule is marked stale or superseded
- **THEN** the governance product surface SHALL show audit history with actor, role, lifecycle transition, supersession target when present, rationale, and timestamp

#### Scenario: Existing review metadata remains
- **WHEN** governance rule audit events are recorded
- **THEN** existing `reviewed_by`, `reviewed_at`, `review_rationale`, `lifecycle_status`, `superseded_by_rule_id`, and `lifecycle_rationale` fields SHALL remain available for compatibility
