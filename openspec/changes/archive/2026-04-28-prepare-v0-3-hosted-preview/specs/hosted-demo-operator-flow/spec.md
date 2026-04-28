## ADDED Requirements

### Requirement: Hosted preview defines a pre-demo readiness checklist
The system SHALL define a concise hosted preview readiness checklist that an operator can run before externally demonstrating the v0.3 RC baseline.

#### Scenario: Checklist names minimum hosted conditions
- **WHEN** an operator prepares an external hosted preview
- **THEN** the checklist SHALL identify required service health, seeded demo data readiness, browser smoke coverage, reset/reseed recovery status, and known limitations

#### Scenario: Checklist separates stable and optional lanes
- **WHEN** the checklist describes what can be shown during the preview
- **THEN** it SHALL distinguish the stable seeded guided demo lane from optional imported repository, GitHub App, and private repository operator/admin lanes

#### Scenario: Checklist records pass and limitation state
- **WHEN** an operator completes hosted preview readiness checks
- **THEN** the checklist or report SHALL record pass, blocking failure, non-blocking failure, or known limitation for each relevant lane

### Requirement: Hosted preview provides an external walkthrough script
The system SHALL provide a bounded external walkthrough script for hosted preview demonstrations.

#### Scenario: Walkthrough starts with guided demo
- **WHEN** an operator follows the external walkthrough script
- **THEN** it SHALL start with the seeded guided demo workspace and preserve the dashboard, review, why, timeline, and drift order

#### Scenario: Walkthrough frames advanced lanes correctly
- **WHEN** the walkthrough mentions imported real repositories, GitHub App sync, or private repository access
- **THEN** it SHALL frame those lanes as optional operator/admin capabilities with provider, credential, and network dependencies

### Requirement: Hosted preview recovery drill is documented
The system SHALL document and, when possible, rehearse hosted preview recovery steps before external demonstration.

#### Scenario: Reset drill restores seeded lane
- **WHEN** an operator runs the hosted preview reset drill
- **THEN** the documented path SHALL restore the seeded demo lane without implicitly deleting imported workspaces

#### Scenario: Reseed drill explains deeper recovery
- **WHEN** reset is insufficient because migrations or data drift affected the seeded lane
- **THEN** the documented path SHALL explain when and how to run the reseed operation
