## ADDED Requirements

### Requirement: Guided demo remains the hosted preview public lane
The system SHALL keep the seeded guided demo as the stable public walkthrough during hosted preview.

#### Scenario: Hosted preview starts from seeded workspace
- **WHEN** an external user or operator begins the hosted preview walkthrough
- **THEN** the documented path SHALL start from the seeded demo workspace rather than requiring a live repository import first

#### Scenario: Guided demo explains bounded data source
- **WHEN** the hosted preview presents seeded demo data
- **THEN** the walkthrough or surrounding docs SHALL explain that the stable demo lane uses curated seeded data while imported workspaces reflect real repository analysis

#### Scenario: Advanced paths do not interrupt walkthrough
- **WHEN** the hosted preview includes links or mentions for live analysis, GitHub App sync, or private repository access
- **THEN** those paths SHALL remain secondary to the guided demo and SHALL NOT be required to complete the public walkthrough
