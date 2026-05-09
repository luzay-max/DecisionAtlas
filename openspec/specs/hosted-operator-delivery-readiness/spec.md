# hosted-operator-delivery-readiness Specification

## Purpose
TBD - created by archiving change hosted-operator-delivery-readiness. Update Purpose after archive.
## Requirements
### Requirement: Hosted operator readiness artifact generation
The system SHALL provide a local way to generate hosted/operator delivery readiness evidence for external preview preparation.

#### Scenario: Generate hosted readiness JSON
- **WHEN** an operator runs the hosted readiness command with supported inputs
- **THEN** the system SHALL write a machine-readable readiness artifact
- **AND** the artifact SHALL include generation metadata, lane classifications, source paths, missing inputs, warnings, and recommended next actions.

#### Scenario: Generate hosted readiness Markdown
- **WHEN** hosted readiness generation completes
- **THEN** the system SHALL write an operator-readable Markdown handoff
- **AND** the Markdown SHALL mirror JSON classifications, blockers, limitations, missing inputs, and source paths.

### Requirement: Hosted readiness uses bounded lane classifications
The system SHALL classify hosted/operator readiness by lane rather than hiding status behind a single opaque pass/fail.

#### Scenario: Core hosted lane blocks public walkthrough
- **WHEN** web, API, engine, or seeded guided-demo readiness is classified as blocking
- **THEN** the hosted readiness artifact SHALL identify that the external public walkthrough should not proceed until resolved or explicitly excluded.

#### Scenario: Optional lane does not block stable walkthrough by default
- **WHEN** governance, imported repository, private access, or real-repo benchmark evidence is missing or non-blocking
- **THEN** the hosted readiness artifact SHALL keep the stable public walkthrough classification separate from those optional lanes.

#### Scenario: Operator-guided state is visible
- **WHEN** hosted URLs, credentials, provider access, imported workspaces, or live benchmark reports are not supplied
- **THEN** the hosted readiness artifact SHALL classify the affected lane as operator-guided, known limitation, or not provided rather than passed.

### Requirement: Hosted readiness records recovery posture
The system SHALL record whether seeded demo recovery is known, rehearsed, blocked, or not provided before external preview handoff.

#### Scenario: Recovery drill is recorded
- **WHEN** an operator provides reset or reseed drill evidence
- **THEN** the hosted readiness artifact SHALL record the recovery classification, source path or explicit status, and recommended rerun command.

#### Scenario: Recovery scope is explicit
- **WHEN** hosted readiness output mentions reset or reseed recovery
- **THEN** it SHALL state that default recovery is scoped to `demo-workspace` and does not implicitly delete imported workspaces or governance history.

### Requirement: Hosted readiness references release and benchmark evidence without replacing release gate
The system SHALL allow hosted/operator readiness records to reference release evidence and real-repo benchmark evidence while keeping them separate from default release validation.

#### Scenario: Release evidence bundle is referenced
- **WHEN** an operator provides a release evidence bundle path
- **THEN** hosted readiness output SHALL include the bundle status and source path
- **AND** it SHALL state that hosted readiness does not replace the canonical release gate.

#### Scenario: Real-repo benchmark evidence is referenced
- **WHEN** an operator provides a real-repo benchmark comparison or live report path
- **THEN** hosted readiness output SHALL disclose regressions, operational blockers, or known limitations as optional credibility evidence.

### Requirement: Hosted readiness remains local and non-mutating
The system SHALL keep hosted readiness generation local and non-mutating by default.

#### Scenario: Generate hosted readiness evidence
- **WHEN** an operator runs the hosted readiness command
- **THEN** the command SHALL NOT reset or reseed data, import repositories, run live network checks, create tags, push commits, publish releases, or mutate OpenSpec archives by default.

### Requirement: Hosted readiness can be archived into readiness history
Generated hosted/operator readiness artifacts SHALL be usable as explicit input to readiness evidence history.

#### Scenario: Hosted readiness is archived
- **WHEN** an operator archives readiness evidence with a hosted readiness JSON path
- **THEN** the history entry SHALL preserve the hosted readiness overall status, public walkthrough status, public walkthrough decision, blockers, operator-guided lanes, known limitations, and source artifact filename.

#### Scenario: Hosted readiness is absent
- **WHEN** readiness history is archived without hosted readiness evidence
- **THEN** the history entry SHALL record hosted readiness as not provided rather than passed.

