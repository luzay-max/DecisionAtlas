## MODIFIED Requirements

### Requirement: Import jobs report document coverage and skip reasons
The system SHALL expose enough import summary detail for the product to explain what repository document content was imported, what was skipped, and which analysis stage the job has reached.

#### Scenario: Import summary includes document counts
- **WHEN** a GitHub import job completes
- **THEN** the job result SHALL distinguish imported repository document counts from the existing issue, pull request, and commit ingest totals

#### Scenario: Import summary includes skip categories
- **WHEN** the importer skips repository files during document selection
- **THEN** the job result SHALL expose coarse skip categories or counts that explain why files were not imported

#### Scenario: Import status includes stage context
- **WHEN** a real repository analysis job is queued or running
- **THEN** the job result SHALL expose the current pipeline stage so the product can report whether the system is importing artifacts, indexing, or extracting decisions

### Requirement: Real workspaces explain sparse decision output
The system SHALL provide enough read-model context for the UI to explain when a real imported workspace has low decision coverage because high-signal evidence was limited, and to distinguish that case from operational failure.

#### Scenario: Imported workspace with low-signal evidence
- **WHEN** a GitHub import succeeds but yields few or no candidate decisions because high-signal repository evidence is limited
- **THEN** the system SHALL provide context that allows the UI to explain this as an evidence limitation rather than an import failure

#### Scenario: Imported workspace with document-backed evidence
- **WHEN** a GitHub import includes supported repository documents and those documents contribute to downstream retrieval or extraction
- **THEN** the system SHALL allow the product to present the workspace as using imported repository evidence rather than only seeded walkthrough data

#### Scenario: Imported workspace with analysis failure
- **WHEN** a GitHub import does not reach a successful analysis result because import execution, indexing, or extraction fails
- **THEN** the system SHALL provide context that allows the UI to distinguish a failed analysis run from a successful but sparse repository analysis
