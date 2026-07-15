# external-self-hosted-install-evidence Specification

## Purpose
Define sanitized external or customer-controlled self-hosted install evidence for DecisionAtlas package delivery claims.

## Requirements

### Requirement: External install evidence is generated from explicit input
The system SHALL generate external self-hosted install evidence from an explicit operator-provided input file.

#### Scenario: External evidence is generated
- **WHEN** an operator runs the external install evidence collector with an input JSON path and output paths
- **THEN** the system SHALL write JSON and Markdown evidence containing schema version, generated timestamp, external host profile, package identity, source evidence paths, lane statuses, blockers, limitations, and recommended next actions

#### Scenario: Missing input is blocking
- **WHEN** the external install evidence collector is run without a readable input file
- **THEN** the system SHALL fail with a bounded error and SHALL NOT synthesize pass evidence from local project state

### Requirement: External install evidence validates required lanes
The system SHALL classify required external install lanes without converting missing or weak evidence into pass.

#### Scenario: Required lanes are present
- **WHEN** the input includes package identity, host profile, startup checks, health checks, browser smoke, repository import evidence or explicit rerun condition, readiness evidence, and redaction acknowledgement
- **THEN** the generated evidence SHALL classify each lane as `passed`, `warning`, `operator_guided`, `not_provided`, or `blocked`

#### Scenario: Required lane is absent
- **WHEN** a required external install lane is absent
- **THEN** the generated evidence SHALL mark that lane `not_provided` or `blocked` and include a recommended next action

### Requirement: External install evidence protects sensitive material
The system SHALL reject obvious sensitive material in external install evidence.

#### Scenario: Secret marker is detected
- **WHEN** submitted input or generated Markdown contains token-like values, provider key markers, `.env` secret assignments, private key markers, raw backup contents, or raw private repository snippets
- **THEN** the collector SHALL mark the evidence `blocked` or fail generation with a bounded redaction error

#### Scenario: Evidence is sanitized
- **WHEN** external install evidence is generated successfully
- **THEN** it SHALL state that tokens, provider keys, `.env` files, private repository contents, database backups, and customer-specific raw logs remain under operator or customer control

### Requirement: External install evidence is honest about customer-host proof
The system SHALL distinguish an external install evidence workflow from completed customer-host proof.

#### Scenario: Customer-host proof is absent
- **WHEN** external install evidence is not provided for a delivery, handoff, or audit report
- **THEN** customer-facing material SHALL preserve `not_provided` or `operator_guided` state and SHALL NOT claim that the package was validated on a customer-controlled host

#### Scenario: Customer-host proof is provided
- **WHEN** sanitized external install evidence is provided
- **THEN** customer-facing material MAY reference the evidence status, host class, package identity, checks performed, and limitations without exposing sensitive material

### Requirement: External install evidence can feed customer-host v2 rehearsal
External self-hosted install evidence SHALL be usable as a source lane for customer-host v2 rehearsal.

#### Scenario: External evidence is supplied to v2 rehearsal
- **WHEN** customer-host v2 rehearsal receives external install evidence JSON or Markdown
- **THEN** it SHALL preserve the external evidence status, host class, blockers, and limitations as a source lane.

#### Scenario: External evidence is missing from v2 rehearsal
- **WHEN** customer-host v2 rehearsal runs without external install evidence
- **THEN** it SHALL mark the external install lane `not_provided` or `operator_guided` and SHALL NOT claim customer-controlled install proof.
