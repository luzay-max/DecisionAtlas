## ADDED Requirements

### Requirement: Accepted-decision baseline is measured
The system SHALL expose accepted-decision baseline status in real repository core-loop evidence without auto-accepting candidate decisions.

#### Scenario: Accepted baseline is empty
- **WHEN** a real repository workspace has candidate decisions but zero accepted decisions
- **THEN** the core-loop evidence SHALL report an accepted baseline status of `empty` with bounded candidate and accepted counts.

#### Scenario: Accepted baseline is present
- **WHEN** a real repository workspace has one or more accepted decisions
- **THEN** the core-loop evidence SHALL report an accepted baseline status of `present` with bounded accepted-decision samples.

### Requirement: Accepted baseline explains why and drift warnings
The system SHALL include accepted baseline status in why/drift grounding details for product-controlled warning lanes.

#### Scenario: Why-search lacks accepted baseline
- **WHEN** a why-search warning uses `missing_accepted_decision_evidence`
- **THEN** its grounding evidence SHALL include accepted baseline status and accepted decision count.

#### Scenario: Drift lacks accepted baseline
- **WHEN** a drift warning uses `missing_accepted_decision_evidence`
- **THEN** its grounding evidence SHALL include accepted baseline status and accepted decision count.

### Requirement: Baseline summaries flow into release evidence
The system SHALL preserve accepted baseline summaries through multi-repo diagnosis and warning-lane reduction outputs.

#### Scenario: Multi-repo diagnosis is generated
- **WHEN** multi-repo diagnosis includes repositories with accepted baseline metadata
- **THEN** each repository result SHALL include the compact accepted baseline summary.

#### Scenario: Warning-lane reduction is generated
- **WHEN** warning-lane reduction classifies a product-controlled repository lane
- **THEN** the classified lane SHALL include accepted baseline summary when supplied by the multi-repo source.
