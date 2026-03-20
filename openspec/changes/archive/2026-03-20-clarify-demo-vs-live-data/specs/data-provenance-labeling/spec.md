## ADDED Requirements

### Requirement: Workspace provenance classification
The system SHALL classify each workspace presented in the product as `demo`, `imported`, or `mixed` so the user can distinguish seeded walkthrough data from real imported repository data.

#### Scenario: Demo workspace classification
- **WHEN** the user opens a workspace whose visible content comes from seeded walkthrough data
- **THEN** the system SHALL classify that workspace as `demo`

#### Scenario: Imported workspace classification
- **WHEN** the user opens a workspace whose visible content comes from imported repository data without seeded demo content
- **THEN** the system SHALL classify that workspace as `imported`

#### Scenario: Mixed workspace classification
- **WHEN** the user opens a workspace that contains both seeded walkthrough content and imported repository content
- **THEN** the system SHALL classify that workspace as `mixed`

### Requirement: Read APIs expose provenance summary
The system SHALL expose workspace provenance summary fields through the read APIs that power dashboard, why search, timeline, drift, and decision detail experiences.

#### Scenario: Dashboard summary returns provenance
- **WHEN** the client requests dashboard summary for a workspace
- **THEN** the response SHALL include the workspace provenance mode and a human-readable source summary

#### Scenario: Why search returns provenance context
- **WHEN** the client submits a why-search question
- **THEN** the response SHALL include enough provenance context for the UI to explain whether the answer is based on demo evidence, imported evidence, or a mixed workspace

#### Scenario: Timeline and drift support provenance-aware UI
- **WHEN** the client requests timeline or drift data for a workspace
- **THEN** the system SHALL provide workspace provenance context needed to label those pages accurately

### Requirement: Main demo surfaces label provenance explicitly
The system SHALL display provenance context on the primary trust-sensitive product surfaces so users do not confuse demo data with live imported repository analysis.

#### Scenario: Dashboard labels workspace mode
- **WHEN** the user opens the workspace dashboard
- **THEN** the page SHALL display whether the workspace is demo, imported, or mixed

#### Scenario: Why search labels answer context
- **WHEN** the user views a why-search answer
- **THEN** the page SHALL explain whether the answer is grounded in demo evidence, imported evidence, or a mixed workspace

#### Scenario: Timeline labels history context
- **WHEN** the user views the decision timeline
- **THEN** the page SHALL explain whether the timeline reflects seeded demo history, imported accepted decisions, or a mixed workspace

#### Scenario: Drift labels alert context
- **WHEN** the user views drift alerts
- **THEN** the page SHALL explain whether the alert context comes from a demo scenario, imported evaluation, or a mixed workspace

#### Scenario: Decision detail inherits workspace provenance
- **WHEN** the user opens decision detail from a workspace flow
- **THEN** the page SHALL expose workspace provenance context so the user can interpret the decision correctly

### Requirement: Public demo copy does not overclaim live analysis
The system SHALL use homepage and demo-facing explanatory copy that distinguishes seeded demo walkthrough behavior from real repository import behavior.

#### Scenario: Homepage copy sets correct expectation
- **WHEN** a user lands on the product homepage
- **THEN** the page SHALL describe the demo workspace as a guided demo experience rather than implying it is automatically real imported repository analysis

#### Scenario: Demo script aligns with product provenance language
- **WHEN** the team uses the public demo script or related walkthrough text
- **THEN** the wording SHALL distinguish demo workspace output from true imported workspace output
