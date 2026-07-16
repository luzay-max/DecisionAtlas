## MODIFIED Requirements

### Requirement: Self-hosted package has a deterministic layout
The system SHALL build a self-hosted release package directory with a deterministic layout that can be reviewed, archived, handed to an operator, installed, and started without reading runtime files from the maintainer source checkout.

#### Scenario: Package directory is created
- **WHEN** an operator runs the package builder with a label, version label, and commit
- **THEN** the system SHALL create a package directory containing a manifest JSON, package README, environment template, selected operator documents, selected startup/validation scripts, runbook references, dependency manifests and lockfiles, Docker Compose support, Node application runtime, Python engine runtime and migrations, prompts, and the bounded browser smoke needed to prove package independence

#### Scenario: Package excludes local secrets and scratch data
- **WHEN** the package builder collects files
- **THEN** it SHALL exclude `.env`, `.tmp`, provider keys, repository tokens, imported repositories, database files, node modules, Python virtual environments, build output, test output, logs, and other local scratch state

#### Scenario: Package documents deferred product lanes
- **WHEN** the package README or manifest describes product scope
- **THEN** it SHALL preserve deferred lanes including billing, hosted multi-tenancy, Marketplace or self-service OAuth, hosted secret vault, enterprise SSO, and runtime license enforcement

### Requirement: Package manifest is machine-readable
The system SHALL write a machine-readable package manifest describing what was generated, which runtime assets make it runnable, and how to validate it.

#### Scenario: Manifest records package identity
- **WHEN** a package is built
- **THEN** the manifest SHALL include package label, version label, commit, generated timestamp, package path, project name, and package schema version

#### Scenario: Manifest records included assets
- **WHEN** a package is built
- **THEN** the manifest SHALL list included docs, scripts, templates, runtime root files, runtime trees, required services, default service URLs, dependency installation commands, startup command, smoke command, and validation commands

#### Scenario: Manifest records handoff boundary
- **WHEN** a package is built
- **THEN** the manifest SHALL include explicit support boundary, unsupported capabilities, secret custody guidance, dependency-download boundary, and readiness evidence expectations

### Requirement: Package verifier emits readiness evidence
The system SHALL provide an offline verifier that checks package structure and runnable runtime inputs and emits bounded JSON and Markdown readiness evidence.

#### Scenario: Valid runnable package passes verification
- **WHEN** a package contains the required manifest, README, environment template, docs, scripts, runbook references, dependency lockfiles, Compose support, application runtime, engine runtime, prompts, and package smoke entry points
- **THEN** the verifier SHALL emit status `pass` with checked items, runnable-package status, and output paths

#### Scenario: Missing required package asset is blocking
- **WHEN** a required package file, runtime tree, runnable entry point, or manifest field is missing
- **THEN** the verifier SHALL emit status `blocking` and identify the missing item without treating the package as runnable or customer-ready

#### Scenario: Legacy structure-only package is not runnable proof
- **WHEN** a package contains only the historical docs, templates, scripts, and schema-v1 manifest without runtime assets
- **THEN** the verifier SHALL preserve readable structure evidence but SHALL classify runnable handoff as `blocking`

#### Scenario: Optional evidence remains explicit
- **WHEN** runtime smoke, private repository token validation, live benchmark, or readiness history evidence is not included in the package structure
- **THEN** the verifier SHALL record the lane as `operator_guided`, `not_provided`, or `known_limitation` instead of `pass`
