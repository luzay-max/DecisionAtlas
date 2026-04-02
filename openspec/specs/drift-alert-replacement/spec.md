## ADDED Requirements

### Requirement: Drift reevaluation replaces stale semantic alerts
The system SHALL treat the latest drift reevaluation result as the current semantic alert set for the reevaluated imported workspace.

#### Scenario: Downgraded artifact does not keep stale supersession alert
- **WHEN** a reevaluation reclassifies an artifact-decision thread from `possible_supersession` to `needs_review`
- **THEN** the system SHALL remove the obsolete stronger alert before exposing the latest reevaluation result

#### Scenario: Upgraded artifact does not keep stale weak alert
- **WHEN** a reevaluation reclassifies an artifact-decision thread from `needs_review` to `possible_supersession`
- **THEN** the system SHALL remove the obsolete weaker alert before exposing the latest reevaluation result

### Requirement: Reevaluation preserves only current semantic outcomes
The system SHALL avoid surfacing contradictory semantic alert types for the same reevaluated workspace because of stale rows left by earlier runs.

#### Scenario: Latest reevaluation keeps one current conclusion per thread
- **WHEN** drift reevaluation finishes for an imported workspace
- **THEN** the active semantic alert set SHALL only contain conclusions produced by that latest reevaluation pass
