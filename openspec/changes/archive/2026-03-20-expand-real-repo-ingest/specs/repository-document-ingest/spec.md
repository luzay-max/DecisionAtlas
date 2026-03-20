## ADDED Requirements

### Requirement: GitHub import includes high-signal repository markdown documents
The system SHALL import a conservative set of high-signal markdown repository documents alongside issues, pull requests, and commits for real GitHub workspace imports.

#### Scenario: Import top-level decision-oriented markdown
- **WHEN** the user imports a GitHub repository that contains top-level markdown files such as `README.md`, `ARCHITECTURE.md`, `DECISIONS.md`, `CHANGELOG.md`, or `RELEASE_NOTES.md`
- **THEN** the system SHALL ingest those files as document artifacts for the workspace

#### Scenario: Import docs and decision subdirectories
- **WHEN** the imported repository contains markdown files under `docs/`, ADR directories, ADRS directories, or RFC directories
- **THEN** the system SHALL ingest those high-signal markdown files as document artifacts for the workspace

#### Scenario: Exclude non-markdown and out-of-scope repository files
- **WHEN** the imported repository contains source files, config files, lockfiles, binaries, or non-markdown files outside the supported high-signal paths
- **THEN** the system SHALL skip those files during repository document ingest

### Requirement: Imported repository documents preserve stable artifact identity
The system SHALL persist remote repository documents in a way that keeps imports idempotent and traceable to the original repository path.

#### Scenario: Document artifacts use repo-relative identity
- **WHEN** the system imports a supported repository document
- **THEN** the resulting artifact SHALL use a stable repo-relative path identity so repeat imports update the same artifact rather than duplicating it

#### Scenario: Document artifacts link back to the repository source
- **WHEN** the system imports a supported repository document
- **THEN** the resulting artifact SHALL include a repository URL that lets the user open the original file in GitHub

### Requirement: Import jobs report document coverage and skip reasons
The system SHALL expose enough import summary detail for the product to explain what repository document content was imported and what was skipped.

#### Scenario: Import summary includes document counts
- **WHEN** a GitHub import job completes
- **THEN** the job result SHALL distinguish imported repository document counts from the existing issue, pull request, and commit ingest totals

#### Scenario: Import summary includes skip categories
- **WHEN** the importer skips repository files during document selection
- **THEN** the job result SHALL expose coarse skip categories or counts that explain why files were not imported

### Requirement: Real workspaces explain sparse decision output
The system SHALL provide enough read-model context for the UI to explain when a real imported workspace has low decision coverage because high-signal evidence was limited.

#### Scenario: Imported workspace with low-signal evidence
- **WHEN** a GitHub import succeeds but yields few or no candidate decisions because high-signal repository evidence is limited
- **THEN** the system SHALL provide context that allows the UI to explain this as an evidence limitation rather than an import failure

#### Scenario: Imported workspace with document-backed evidence
- **WHEN** a GitHub import includes supported repository documents and those documents contribute to downstream retrieval or extraction
- **THEN** the system SHALL allow the product to present the workspace as using imported repository evidence rather than only seeded walkthrough data
