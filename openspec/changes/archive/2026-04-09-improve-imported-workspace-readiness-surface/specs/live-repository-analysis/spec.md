## MODIFIED Requirements

### Requirement: Live analysis reports honest outcomes
The system SHALL distinguish successful analysis, insufficient evidence, operational failure, imported-workspace readiness, existing-workspace reuse state, and clearer import failure classes so users can interpret live-analysis results correctly and know the strongest next action, and SHALL expose imported-workspace readiness in a form that product surfaces can reuse consistently after the import completes.

#### Scenario: Review-ready workspace yields actionable outcome
- **WHEN** a live analysis job completes and the imported workspace contains reviewable candidate decisions
- **THEN** the system SHALL expose enough outcome context for the product to recommend review as the next action

#### Scenario: Existing repository is looked up before rerun
- **WHEN** the user enters a repository that already maps to an imported workspace
- **THEN** the live-analysis entry flow SHALL expose that reuse state before starting another import job

#### Scenario: Imported readiness remains reusable after analysis
- **WHEN** a live analysis run completes and later dashboard or search surfaces load that imported workspace
- **THEN** the system SHALL provide the same imported readiness guidance rather than leaving each surface to infer its own next-step interpretation
