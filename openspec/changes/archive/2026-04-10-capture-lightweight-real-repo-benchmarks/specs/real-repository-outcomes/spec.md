## ADDED Requirements

### Requirement: Important real-repo expectations are benchmark-captured
The system SHALL capture important imported real-repository expectations in lightweight benchmark fixtures when those expectations are used to protect known release-quality behavior.

#### Scenario: Known why-search regression is fixture-backed
- **WHEN** a real repository has a known focused why-search case that protects an important imported-lane behavior
- **THEN** the expected why outcome SHALL be captured in a lightweight benchmark fixture rather than only in narrative notes

#### Scenario: Known drift-noise regression is fixture-backed
- **WHEN** a real repository has a known drift-noise regression pattern that should remain conservative
- **THEN** the expected broad drift outcome SHALL be captured in a lightweight benchmark fixture rather than only in narrative notes

#### Scenario: Sparse or conversion-limited repository remains represented
- **WHEN** a real repository is intentionally used to represent sparse or conversion-limited outcomes
- **THEN** the benchmark fixtures SHALL preserve that bounded expectation without treating the repository as a generic failure
