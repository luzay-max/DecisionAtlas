# guided-demo-experience Specification

## Purpose
Establishes the seeded guided demo as the primary MVP walkthrough with a fixed ordered path, next-step guidance, progress cues, and governance second-act boundaries for hosted preview.
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

### Requirement: Governed hosted walkthrough has a bounded second act
The system SHALL keep the seeded guided demo as the first public walkthrough during governed hosted preview and SHALL present governance capabilities as a bounded second act after the viewer understands the core decision-memory flow.

#### Scenario: Walkthrough starts with stable guided demo
- **WHEN** an operator follows the governed hosted preview script
- **THEN** the script SHALL begin with `demo-workspace` dashboard, review, why-search, timeline, and drift before introducing governance-specific surfaces

#### Scenario: Governance second act is explicitly bounded
- **WHEN** the walkthrough transitions to governance Markdown ingest, accepted rules, or agent guardrail output
- **THEN** it SHALL explain that governance rules are human-reviewed and guardrails are advisory by default rather than automatic production enforcement

#### Scenario: Optional lanes do not interrupt the core walkthrough
- **WHEN** the walkthrough mentions live repository import, private repository access, GitHub App sync, or real-repository benchmark reports
- **THEN** it SHALL frame them as optional credibility or operator/admin lanes with provider, credential, hosted environment, and network dependencies

### Requirement: Governed preview copy preserves product boundaries
The system SHALL ensure governed hosted preview guidance does not imply production SaaS scope or default governance enforcement.

#### Scenario: Preview names production non-goals
- **WHEN** guided demo or preview docs describe the external hosted preview
- **THEN** they SHALL state that billing, full organization administration, secret vault, marketplace self-service, multiplayer review, and default CI enforcement are out of scope

#### Scenario: Caution and pause are explainable demo outcomes
- **WHEN** the demo script references guardrail `caution` or `pause`
- **THEN** it SHALL frame those statuses as evidence-backed human decision boundaries rather than hidden failures or automatic remediation requests
