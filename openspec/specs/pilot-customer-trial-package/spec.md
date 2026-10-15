## Purpose

Generate a bounded pilot customer trial handoff package from existing customer-facing materials and selected readiness evidence, while preserving missing, warning, operator-guided, and blocking evidence boundaries.

## Requirements

### Requirement: Pilot customer trial package is generated
The system SHALL generate a bounded pilot customer trial package from existing customer-facing materials and selected evidence artifacts.

#### Scenario: Trial package is generated
- **WHEN** an operator runs the pilot customer trial package collector with output paths
- **THEN** the system SHALL write JSON and Markdown evidence and create a bundle directory containing a README, operator checklist, and evidence manifest.

#### Scenario: Required customer materials are checked
- **WHEN** the collector runs
- **THEN** it SHALL verify the required pilot delivery, commercial, private-repo template, support boundary, and package guide documents exist.

### Requirement: Trial package preserves source evidence boundaries
The pilot customer trial package SHALL preserve source evidence statuses without converting missing or warning evidence into pass.

#### Scenario: Source evidence is supplied
- **WHEN** package verification, pilot kit verification, commercial proposal verification, real external host trial evidence, full-chain evidence, readiness history, or private-repo evidence paths are supplied
- **THEN** the package SHALL include compact source status, source path, warning counts, blocker counts, and selected repository identifiers when available.

#### Scenario: Source evidence is missing
- **WHEN** a source evidence path is omitted
- **THEN** the package SHALL keep that lane as `not_provided` or `operator_guided` and SHALL NOT imply the pilot is fully proven.

### Requirement: Trial package is safe for customer handoff
The pilot customer trial package SHALL avoid committing private customer-specific material.

#### Scenario: Package is generated
- **WHEN** the package is generated
- **THEN** it SHALL state that filled agreements, private tokens, customer identifiers, private repository content, and legal/payment terms belong outside the public repository.

#### Scenario: Sensitive marker is detected
- **WHEN** operator-supplied notes include obvious tokens, private keys, `.env` secret assignments, raw private repository content, or raw backup markers
- **THEN** the package SHALL be marked `blocking` and generated Markdown SHALL NOT include the raw sensitive value.

### Requirement: Trial package defines operator next steps
The pilot customer trial package SHALL provide an actionable operator checklist for the next real external trial.

#### Scenario: Non-clean evidence exists
- **WHEN** any lane is warning, blocking, operator-guided, or not-provided
- **THEN** the package SHALL include recommended next actions that identify which evidence to run or replace before a customer claim.

#### Scenario: Real external host evidence is template-only
- **WHEN** real external host trial evidence reports `template_or_placeholder`
- **THEN** the package SHALL explicitly instruct the operator to rerun on a real non-developer or customer-controlled host before claiming customer-host validation.
