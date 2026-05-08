## ADDED Requirements

### Requirement: Accepted governance rules can be lifecycle-reviewed
The system SHALL let authorized reviewers update the lifecycle state of accepted governance rules without changing the original human review state.

#### Scenario: Mark accepted rule stale
- **WHEN** a reviewer marks an accepted current governance rule as stale with bounded rationale
- **THEN** the system SHALL preserve the rule as accepted, set `lifecycle_status` to `stale`, preserve the lifecycle rationale or equivalent audit evidence, and stop exposing the rule as active accepted checker input

#### Scenario: Supersede accepted rule
- **WHEN** a reviewer marks an accepted current governance rule as superseded by another accepted current rule in the same owner scope with bounded rationale
- **THEN** the system SHALL preserve the original rule as accepted, set `lifecycle_status` to `superseded`, preserve `superseded_by_rule_id`, preserve the lifecycle rationale or equivalent audit evidence, and stop exposing the original rule as active accepted checker input

#### Scenario: Reject invalid lifecycle target
- **WHEN** a reviewer attempts to supersede a rule with itself, a missing rule, a rejected rule, a pending draft, a stale rule, a superseded rule, or a rule outside the current owner scope
- **THEN** the system SHALL reject the lifecycle transition with a bounded validation error

#### Scenario: Review state remains separate
- **WHEN** an accepted rule is marked stale or superseded
- **THEN** the system SHALL keep `review_state` as `accepted` so the rule remains historical accepted evidence while lifecycle status controls current authority

### Requirement: Governance product surface supports lifecycle review
The product SHALL expose bounded lifecycle review actions for accepted governance rules.

#### Scenario: Accepted rule shows lifecycle actions
- **WHEN** an accepted current governance rule is rendered on the governance page
- **THEN** the product SHALL let an authorized reviewer mark it stale or superseded with rationale

#### Scenario: Supersession target is selected from valid replacements
- **WHEN** a reviewer supersedes an accepted governance rule from the product surface
- **THEN** the product SHALL offer only accepted current rules from the same owner scope as replacement candidates where available

#### Scenario: Lifecycle result updates without page reload
- **WHEN** a lifecycle transition succeeds
- **THEN** the product SHALL update the displayed rule lifecycle state, supersession reference, and rationale without requiring a full page reload

#### Scenario: Lifecycle actions remain unavailable for non-authoritative drafts
- **WHEN** a pending, rejected, stale, or superseded rule is rendered
- **THEN** the product SHALL NOT offer lifecycle transition actions that would imply the rule is current authoritative input
