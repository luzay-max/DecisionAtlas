## Purpose
Define the offline/source-tree self-hosted release package contract for DecisionAtlas operator handoff.

## Requirements

### Requirement: Self-hosted package has a deterministic layout
The system SHALL build a self-hosted release package directory with a deterministic layout that can be reviewed, archived, or handed to an operator.

#### Scenario: Package directory is created
- **WHEN** an operator runs the package builder with a label, version label, and commit
- **THEN** the system SHALL create a package directory containing a manifest JSON, package README, environment template, selected operator documents, selected startup/validation scripts, and runbook references

#### Scenario: Package excludes local secrets and scratch data
- **WHEN** the package builder collects files
- **THEN** it SHALL exclude `.env`, `.tmp`, provider keys, repository tokens, database files, node modules, Python virtual environments, logs, and other local scratch state

#### Scenario: Package documents deferred product lanes
- **WHEN** the package README or manifest describes product scope
- **THEN** it SHALL preserve deferred lanes including billing, hosted multi-tenancy, Marketplace or self-service OAuth, hosted secret vault, enterprise SSO, and runtime license enforcement

### Requirement: Package manifest is machine-readable
The system SHALL write a machine-readable package manifest describing what was generated and how to validate it.

#### Scenario: Manifest records package identity
- **WHEN** a package is built
- **THEN** the manifest SHALL include package label, version label, commit, generated timestamp, package path, project name, and package schema version

#### Scenario: Manifest records included assets
- **WHEN** a package is built
- **THEN** the manifest SHALL list included docs, scripts, templates, required services, default service URLs, and validation commands

#### Scenario: Manifest records handoff boundary
- **WHEN** a package is built
- **THEN** the manifest SHALL include explicit support boundary, unsupported capabilities, secret custody guidance, and readiness evidence expectations

### Requirement: Package verifier emits readiness evidence
The system SHALL provide an offline verifier that checks package structure and emits bounded JSON and Markdown readiness evidence.

#### Scenario: Valid package passes verification
- **WHEN** a package contains the required manifest, README, environment template, docs, scripts, and runbook references
- **THEN** the verifier SHALL emit status `pass` with checked items and output paths

#### Scenario: Missing required package asset is blocking
- **WHEN** a required package file or manifest field is missing
- **THEN** the verifier SHALL emit status `blocking` and identify the missing item without treating the package as customer-ready

#### Scenario: Optional evidence remains explicit
- **WHEN** runtime smoke, private repository token validation, live benchmark, or readiness history evidence is not included in the package structure
- **THEN** the verifier SHALL record the lane as `operator_guided`, `not_provided`, or `known_limitation` instead of `pass`

### Requirement: Package handoff includes deployment runbooks
The self-hosted package SHALL include operator-facing runbooks for first setup, first-admin initialization, backup, restore, upgrade, and validation.

#### Scenario: First setup runbook is included
- **WHEN** an operator opens the package README or setup guide
- **THEN** it SHALL explain required services, environment variables, startup commands, health checks, first-admin/bootstrap expectation, and where credentials must be configured

#### Scenario: Backup and restore runbook is included
- **WHEN** an operator prepares a self-hosted handoff
- **THEN** the package SHALL reference PostgreSQL backup, Redis recovery expectations, `.env` custody, restore, rollback, and rerun-readiness steps

#### Scenario: Upgrade runbook is included
- **WHEN** an operator plans to upgrade a package
- **THEN** the package SHALL explain how to record the prior version, back up data and credentials, apply the new revision, run migrations, rerun readiness checks, and rollback if validation fails

### Requirement: Self-hosted package references handoff reporting
The self-hosted package SHALL document how operators can generate team handoff reports as part of delivery acceptance.

#### Scenario: Package docs include handoff report generation
- **WHEN** an operator opens the self-hosted package README or runbook
- **THEN** the documentation SHALL identify the handoff report command, expected JSON and Markdown outputs, recommended source evidence inputs, and secret-handling boundary

#### Scenario: Package verifier acknowledges handoff evidence
- **WHEN** a package verifier or readiness flow evaluates delivery evidence
- **THEN** it SHALL be able to record whether team handoff report evidence was provided, not provided, operator-guided, or blocking

### Requirement: Package includes license and support boundary artifacts
The self-hosted package SHALL include license/support boundary documentation and entitlement template references.

#### Scenario: Package includes boundary docs
- **WHEN** a self-hosted package is built
- **THEN** it SHALL include customer-readable license/support boundary documentation and an offline entitlement template

#### Scenario: Package verifier records boundary lane
- **WHEN** a package verifier evaluates a self-hosted package
- **THEN** it SHALL record whether license/support boundary evidence is present and SHALL keep entitlement absence non-blocking for evaluation

### Requirement: Package references clean install rehearsal
The self-hosted package SHALL document how operators can run clean install rehearsal before customer handoff.

#### Scenario: Package docs include clean rehearsal command
- **WHEN** an operator opens the self-hosted package README or package guide
- **THEN** the documentation SHALL identify the clean install rehearsal command, expected JSON and Markdown outputs, required package input, and optional source evidence inputs

#### Scenario: Package verifier notes clean rehearsal boundary
- **WHEN** package verification evidence is generated
- **THEN** the evidence SHALL state that package structure verification is not the same as clean install rehearsal and SHALL identify clean rehearsal evidence as a separate customer-readiness input

### Requirement: Self-hosted package includes pilot delivery kit references
The self-hosted release package SHALL include or reference pilot customer delivery kit materials for external evaluation.

#### Scenario: Package includes pilot materials
- **WHEN** a self-hosted package is built for external pilot evaluation
- **THEN** the package SHALL include the pilot delivery kit entry point, deployment checklist, demo script, customer FAQ, tier comparison, and delivery email template

#### Scenario: Package verifier records pilot kit lane
- **WHEN** package verification evaluates a self-hosted package
- **THEN** it SHALL record whether pilot delivery kit materials are present or explicitly operator-guided
