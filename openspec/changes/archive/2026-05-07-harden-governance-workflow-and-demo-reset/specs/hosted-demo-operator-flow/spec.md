## ADDED Requirements

### Requirement: Seeded demo recovery restores guided walkthrough state
The system SHALL define seeded demo recovery as restoring the stable guided demo lane to a known walkthrough-ready state that includes the demo workspace, accepted decision baseline, reviewable candidate queue, source-backed why-search path, timeline history, and drift alert path.

#### Scenario: Reset restores consumed review queue
- **WHEN** the seeded demo review queue has been consumed before an operator runs the seeded demo reset path
- **THEN** the recovery flow SHALL restore at least one reviewable candidate decision for the guided demo workspace

#### Scenario: Reset restores source-backed accepted baseline
- **WHEN** an operator runs the seeded demo reset path
- **THEN** the recovery flow SHALL restore accepted demo decisions with source references sufficient for why-search and timeline walkthroughs

#### Scenario: Reset restores drift walkthrough state
- **WHEN** an operator runs the seeded demo reset path
- **THEN** the recovery flow SHALL restore the seeded drift alert state needed for the guided drift walkthrough

### Requirement: Seeded demo recovery preserves imported workspace lane
The system SHALL keep seeded demo recovery scoped to the stable `demo-workspace` lane and SHALL NOT implicitly delete imported real-repository workspaces.

#### Scenario: Imported workspaces survive seeded reset
- **WHEN** an imported workspace exists and an operator runs the default seeded demo reset path
- **THEN** the imported workspace SHALL remain available after the seeded demo lane is restored

#### Scenario: Recovery docs name the destructive boundary
- **WHEN** hosted operator guidance describes demo reset or reseed
- **THEN** it SHALL state that the default recovery path is scoped to `demo-workspace` and does not perform broad imported-workspace cleanup

### Requirement: Seeded demo readiness can be verified
The system SHALL provide an operator-readable way to verify whether the seeded guided demo lane is ready for a walkthrough after startup, reset, or reseed.

#### Scenario: Readiness verifies required demo state
- **WHEN** an operator checks seeded demo readiness
- **THEN** the result SHALL indicate whether the demo workspace, accepted decisions, candidate queue, source references, timeline path, and drift alert path are present

#### Scenario: Readiness reports recovery guidance
- **WHEN** seeded demo readiness fails
- **THEN** the result SHALL identify whether reset or reseed is the recommended recovery path
