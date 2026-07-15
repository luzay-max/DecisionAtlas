## Purpose

Define repeatable customer-host rehearsal evidence that bundles external host, package, clean install, browser smoke, release rehearsal, and readiness-history signals without collecting secrets or mutating customer infrastructure.

## Requirements

### Requirement: Customer-host v2 rehearsal bundles delivery evidence
The system SHALL generate customer-host rehearsal v2 evidence that bundles external host, package, clean install, browser smoke, release rehearsal, and readiness-history signals.

#### Scenario: Rehearsal evidence is generated
- **WHEN** an operator runs the customer-host v2 rehearsal collector with output paths
- **THEN** the system SHALL write JSON and Markdown evidence containing schema version, generated timestamp, rehearsal label, host proof level, lane summaries, blockers, limitations, and recommended next actions.

#### Scenario: Source evidence is provided
- **WHEN** package verification, clean install, external install, release rehearsal, browser smoke, or readiness history evidence paths are provided
- **THEN** the collector SHALL preserve each source status without converting warnings or missing evidence into pass.

### Requirement: Customer-host v2 rehearsal uses sanitized host input
The system SHALL accept explicit sanitized customer-host input without collecting secrets or raw customer data.

#### Scenario: Host template is provided
- **WHEN** a sanitized customer-host input JSON is provided
- **THEN** the evidence SHALL include host class, operating system family, deployment mode, package identity, commands run, health check summary, browser smoke summary, redaction acknowledgement, and limitations.

#### Scenario: Host template is absent
- **WHEN** no customer-host input JSON is provided
- **THEN** the evidence SHALL preserve customer-host proof as `operator_guided` or `not_provided` and SHALL NOT claim customer-controlled host validation.

### Requirement: Customer-host v2 rehearsal is safe by default
The customer-host rehearsal v2 workflow SHALL remain local, explicit, and non-mutating by default.

#### Scenario: Collector runs
- **WHEN** the collector runs
- **THEN** it SHALL NOT run migrations, reset databases, publish packages, push git commits, upload evidence, or mutate customer infrastructure by default.

#### Scenario: Secret marker is detected
- **WHEN** input or generated Markdown includes obvious token, private key, `.env` secret assignment, raw private repository content, or raw backup material
- **THEN** the collector SHALL fail or mark the rehearsal `blocking` with a bounded redaction error.

### Requirement: Customer-host v2 rehearsal can be archived
The customer-host rehearsal v2 evidence SHALL be archivable into readiness history when requested.

#### Scenario: Archive is requested
- **WHEN** the operator runs the collector with readiness-history archival enabled
- **THEN** the generated customer-host JSON and Markdown SHALL be copied into a dated or labeled readiness history entry.

#### Scenario: Archive is skipped
- **WHEN** archival is not requested
- **THEN** the collector SHALL still write `.tmp` JSON and Markdown and SHALL mark history archival as `operator_guided`.

### Requirement: Customer-host v2 can feed full-chain rehearsal
Customer-host v2 evidence SHALL be usable as a source lane for full-chain random repository release rehearsal.

#### Scenario: Customer-host v2 evidence is supplied
- **WHEN** full-chain rehearsal receives customer-host v2 JSON or Markdown
- **THEN** it SHALL preserve host proof level, status, lane counts, blockers, and limitations.

#### Scenario: Customer-host v2 evidence is template-only
- **WHEN** customer-host v2 evidence was generated from an example or operator-filled template
- **THEN** the full-chain bundle SHALL preserve the template limitation and SHALL NOT claim final customer-controlled host validation.

### Requirement: Customer-host v2 feeds real external host trial evidence
Customer-host v2 evidence SHALL be usable as a source for the stricter real external host trial evidence gate.

#### Scenario: Customer-host v2 evidence is supplied to the trial gate
- **WHEN** real external host trial evidence receives customer-host v2 JSON
- **THEN** it SHALL preserve customer-host v2 status, host proof level, lane counts, blockers, limitations, and warnings.

#### Scenario: Customer-host v2 evidence is template-like
- **WHEN** customer-host v2 evidence was generated from an example template, placeholder input, or local-only proof
- **THEN** the real external host trial gate SHALL keep the final trial evidence non-clean and SHALL NOT claim real external/customer-controlled host validation.
