## ADDED Requirements

### Requirement: Full-chain random repo release rehearsal bundle is generated
The system SHALL generate a full-chain rehearsal bundle that combines random real repository diagnosis, release rehearsal, customer-host v2, and browser rehearsal evidence.

#### Scenario: Bundle is generated from source evidence
- **WHEN** an operator runs the full-chain rehearsal collector with output paths and evidence inputs
- **THEN** the system SHALL write JSON and Markdown containing schema version, generated timestamp, selected repositories, lane summaries, blockers, limitations, and recommended next actions.

#### Scenario: Source evidence has warnings
- **WHEN** release, random repo, customer-host, browser, or readiness-history evidence reports warning or operator-guided state
- **THEN** the full-chain bundle SHALL preserve that state rather than summarizing the rehearsal as clean pass.

### Requirement: Full-chain rehearsal supports random real repositories
The full-chain rehearsal SHALL support real public GitHub repository evidence.

#### Scenario: Random diagnosis evidence is supplied
- **WHEN** multi-repo live diagnosis evidence includes selected repository IDs
- **THEN** the full-chain bundle SHALL include those IDs and aggregate diagnosis status.

#### Scenario: Random diagnosis is unavailable
- **WHEN** random real repository diagnosis evidence is absent or failed
- **THEN** the full-chain bundle SHALL mark that lane as `not_provided`, `operator_guided`, `warning`, or `blocking` and SHALL NOT claim live repo validation.

### Requirement: Full-chain rehearsal is safe and customer-readable
The full-chain rehearsal SHALL produce customer-safe handoff material.

#### Scenario: Markdown is generated
- **WHEN** Markdown output is written
- **THEN** it SHALL include compact lane status, selected repository IDs, evidence paths, limitations, and next actions without embedding secrets, raw logs, or private source.

#### Scenario: Archive is requested
- **WHEN** readiness-history archival is enabled
- **THEN** the generated full-chain JSON and Markdown SHALL be copied into a durable dated or labeled readiness history entry.
