# guided-demo-experience Specification

## Purpose
TBD - created by archiving change stabilize-guided-demo-lane. Update Purpose after archive.
## Requirements
### Requirement: Guided demo is the primary MVP path
The system SHALL present the seeded demo workspace as the primary MVP walkthrough and SHALL demote non-walkthrough controls to a clearly secondary advanced or experimental area.

#### Scenario: Homepage prioritizes guided demo
- **WHEN** a user lands on the homepage
- **THEN** the page SHALL present a guided-demo entry as the primary call to action

#### Scenario: Homepage demotes advanced controls
- **WHEN** a user views homepage controls related to provider switching or live repository analysis
- **THEN** the page SHALL place those controls in an explicitly labeled advanced or experimental section rather than at the same priority as the guided demo

### Requirement: Guided demo uses a fixed ordered walkthrough
The system SHALL present the guided demo as a consistent ordered walkthrough from dashboard through review, why-search, timeline, and drift.

#### Scenario: Dashboard identifies walkthrough start
- **WHEN** a user opens the guided demo workspace dashboard
- **THEN** the page SHALL identify the current walkthrough step and the next recommended action

#### Scenario: Downstream pages preserve walkthrough order
- **WHEN** a user opens review, why-search, timeline, or drift from the guided demo lane
- **THEN** each page SHALL indicate where it sits in the walkthrough order

### Requirement: Guided demo pages provide next-step guidance
The system SHALL help the user continue the walkthrough without guessing which page to visit next.

#### Scenario: Review points to why-search
- **WHEN** the user completes the demo review step or reaches a review state that allows the next step
- **THEN** the review experience SHALL provide an explicit next action that continues to the why-search step

#### Scenario: Why-search points to timeline
- **WHEN** the user completes the demo why-search step
- **THEN** the why-search experience SHALL provide an explicit next action that continues to the timeline step

#### Scenario: Timeline points to drift
- **WHEN** the user views the timeline in the guided demo lane
- **THEN** the timeline experience SHALL provide an explicit next action that continues to the drift step

### Requirement: Guided demo actions report progress and completion clearly
The system SHALL expose user-facing progress and completion cues for key demo actions so the walkthrough feels stable and understandable.

#### Scenario: Demo import reports stage-aware progress
- **WHEN** the user starts the demo import
- **THEN** the UI SHALL report user-facing progress using the available import stages until the action succeeds, fails, or continues in background

#### Scenario: Guided demo explains completed step
- **WHEN** a guided demo step reaches a meaningful completion point such as import success or review completion
- **THEN** the page SHALL show a completion-oriented message and the next recommended action

### Requirement: Guided demo empty and error states preserve the walkthrough
The system SHALL keep the user oriented in the walkthrough even when data is absent or an action cannot complete immediately.

#### Scenario: Empty review state remains walkthrough-aware
- **WHEN** the user reaches the review page and no candidate decisions are available for the guided demo
- **THEN** the page SHALL explain what prerequisite step is missing and how to continue the walkthrough

#### Scenario: Why-search remains walkthrough-aware before execution
- **WHEN** the user opens why-search in the guided demo lane before asking a question
- **THEN** the page SHALL provide a guided starting action rather than only a blank tool surface

