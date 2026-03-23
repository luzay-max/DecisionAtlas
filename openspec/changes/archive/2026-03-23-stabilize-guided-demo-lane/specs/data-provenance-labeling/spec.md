## MODIFIED Requirements

### Requirement: Main demo surfaces label provenance explicitly
The system SHALL display provenance context on the primary trust-sensitive product surfaces so users do not confuse demo data with live imported repository analysis.

#### Scenario: Dashboard labels workspace mode
- **WHEN** the user opens the workspace dashboard
- **THEN** the page SHALL display whether the workspace is demo, imported, or mixed

#### Scenario: Review labels queue context
- **WHEN** the user views the review queue for a workspace
- **THEN** the page SHALL explain whether the queue is grounded in seeded walkthrough data, imported repository analysis, or a mixed workspace

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
The system SHALL use homepage and demo-facing explanatory copy that distinguishes seeded demo walkthrough behavior from real repository import behavior and from advanced experimental controls.

#### Scenario: Homepage copy sets correct expectation
- **WHEN** a user lands on the product homepage
- **THEN** the page SHALL describe the demo workspace as a guided demo experience rather than implying it is automatically real imported repository analysis

#### Scenario: Homepage marks advanced controls as secondary
- **WHEN** a user is shown provider switching or live-analysis entry points from the homepage or guided demo shell
- **THEN** the UI SHALL label those controls as advanced or experimental and SHALL explain that they do not redefine the seeded walkthrough results already on screen

#### Scenario: Demo script aligns with product provenance language
- **WHEN** the team uses the public demo script or related walkthrough text
- **THEN** the wording SHALL distinguish demo workspace output from true imported workspace output
