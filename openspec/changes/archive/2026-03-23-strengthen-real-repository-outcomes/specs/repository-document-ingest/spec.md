## MODIFIED Requirements

### Requirement: GitHub import includes high-signal repository markdown documents
The system SHALL import a conservative but more outcome-oriented set of high-signal markdown repository documents alongside issues, pull requests, and commits for real GitHub workspace imports.

#### Scenario: Import top-level decision-oriented markdown
- **WHEN** the user imports a GitHub repository that contains top-level markdown files such as `README.md`, `ARCHITECTURE.md`, `DECISIONS.md`, `CHANGELOG.md`, or `RELEASE_NOTES.md`
- **THEN** the system SHALL ingest those files as document artifacts for the workspace

#### Scenario: Import docs and decision subdirectories
- **WHEN** the imported repository contains markdown files under `docs/`, ADR directories, ADRS directories, or RFC directories
- **THEN** the system SHALL ingest those high-signal markdown files as document artifacts for the workspace

#### Scenario: Import migration and rollout-oriented markdown
- **WHEN** the imported repository contains markdown files that describe migration, rollout, operations, architecture, release, or deprecation decisions within supported high-signal paths
- **THEN** the system SHALL ingest those files as document artifacts for the workspace

#### Scenario: Exclude non-markdown and out-of-scope repository files
- **WHEN** the imported repository contains source files, config files, lockfiles, binaries, or non-markdown files outside the supported high-signal paths
- **THEN** the system SHALL skip those files during repository document ingest

### Requirement: Real workspaces explain sparse decision output
The system SHALL provide enough read-model context for the UI to explain when a real imported workspace has low decision coverage because high-signal evidence was limited, when imported evidence contributed to usable downstream features, and to distinguish those cases from operational failure.

#### Scenario: Imported workspace with low-signal evidence
- **WHEN** a GitHub import succeeds but yields few or no candidate decisions because high-signal repository evidence is limited
- **THEN** the system SHALL provide context that allows the UI to explain this as an evidence limitation rather than an import failure

#### Scenario: Imported workspace with document-backed evidence
- **WHEN** a GitHub import includes supported repository documents and those documents contribute to downstream extraction, review, or why-answer support
- **THEN** the system SHALL allow the product to present the workspace as using imported repository evidence rather than only seeded walkthrough data

#### Scenario: Imported workspace with analysis failure
- **WHEN** a GitHub import does not reach a successful analysis result because import execution, indexing, or extraction fails
- **THEN** the system SHALL provide context that allows the UI to distinguish a failed analysis run from a successful but sparse repository analysis
