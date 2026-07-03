# multi-repo-live-diagnosis-rotation Specification

## Purpose

Defines repeatable multi-repo diagnosis evidence for real public GitHub repository rotation.

## Requirements

### Requirement: Multi-repo diagnosis rotates through real public repositories
The system SHALL provide a repeatable multi-repo diagnosis rehearsal using real public GitHub repository identities.

#### Scenario: Explicit repositories are selected
- **WHEN** an operator supplies one or more repository IDs from the benchmark pool
- **THEN** the diagnosis SHALL run setup and core-loop evidence for each selected repository.

#### Scenario: Random repositories are selected
- **WHEN** an operator supplies a random count and seed
- **THEN** the diagnosis SHALL select that many repositories deterministically from the pool.

### Requirement: Multi-repo diagnosis preserves per-repo outcomes
The diagnosis SHALL preserve each repository's setup, dashboard, review, why-search, drift, and guardrail statuses.

#### Scenario: Repository has partial evidence
- **WHEN** a repository imports or opens but review, why-search, drift, or guardrail evidence is incomplete
- **THEN** the repository result SHALL remain warning or non-pass rather than being summarized as pass.

#### Scenario: Repository cannot be reached
- **WHEN** GitHub, the API, the engine, or the workspace lookup fails
- **THEN** the repository result SHALL classify the outcome as provider, local-stack, operator-guided, or not-provided failure with next actions.

### Requirement: Multi-repo diagnosis produces handoff evidence
The diagnosis SHALL produce customer-safe JSON and Markdown evidence.

#### Scenario: Diagnosis completes
- **WHEN** the diagnosis finishes across selected repositories
- **THEN** it SHALL write a report with selected repo IDs, per-repo statuses, aggregate counts, recommended follow-up, and secret-boundary notes.

### Requirement: Multi-repo diagnosis can feed release rehearsal
Multi-repo live diagnosis evidence SHALL be includable as a lane in the one-command release rehearsal bundle.

#### Scenario: Diagnosis evidence is provided
- **WHEN** a multi-repo diagnosis JSON path is supplied
- **THEN** the release rehearsal SHALL include selected repository IDs, aggregate counts, status, and follow-up actions.

#### Scenario: Diagnosis is run live
- **WHEN** the operator enables live multi-repo diagnosis
- **THEN** the rehearsal SHALL run diagnosis against selected real public repository metadata and include the generated evidence paths.
