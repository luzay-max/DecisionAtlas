## ADDED Requirements

### Requirement: Curated real-repo benchmark fixtures
The system SHALL provide a small fixture-backed benchmark set for real imported repositories that captures repo-level expectations and focused why/drift cases without requiring live imports during default validation, and SHALL allow fixture-backed expectations for candidate-conversion behavior on repositories used to protect imported review-readiness improvements.

#### Scenario: Fixture set validates without live services
- **WHEN** the benchmark validation is run without live mode
- **THEN** the system SHALL validate that the real-repo benchmark fixtures are present, well-formed, and contain required expectations without calling GitHub, model providers, or local APIs

#### Scenario: Fixture set includes focused case expectations
- **WHEN** benchmark fixtures describe a repository with known why or drift regression cases
- **THEN** the fixtures SHALL include case-level expectations such as workspace slug, question or alert pattern, expected broad status, and minimum citation or confidence requirements

#### Scenario: Fixture set includes candidate-conversion expectations
- **WHEN** a curated repository is used to protect improvement of the screened-in-to-candidate funnel
- **THEN** the fixture set SHALL be able to express broad expectations such as minimum reviewable candidates or other bounded candidate-conversion outcomes without relying on exact answer prose or local database snapshots

### Requirement: Optional live benchmark execution
The system SHALL support optional live benchmark execution against an already-running local stack and pre-existing imported workspaces.

#### Scenario: Live why benchmark checks broad answer contract
- **WHEN** live benchmark mode evaluates a focused why case
- **THEN** it SHALL check broad outcome requirements such as answer status, minimum citations, and expected terms rather than exact answer prose

#### Scenario: Live benchmark reports failures clearly
- **WHEN** a live benchmark case fails because the API is unavailable or the observed result does not match the expected broad outcome
- **THEN** the benchmark command SHALL report which case failed and why

### Requirement: Benchmark remains lightweight
The system SHALL keep real-repo benchmark capture bounded to release-smoke validation and SHALL NOT require a large evaluation platform, and SHALL make offline fixture validation part of the canonical release baseline validation path.

#### Scenario: Default pre-release remains fast
- **WHEN** the pre-release validation invokes benchmark checks
- **THEN** the default benchmark path SHALL remain CI-safe and SHALL NOT import repositories or require live provider credentials

#### Scenario: Release baseline invokes fixture benchmark validation
- **WHEN** release baseline validation runs before tagging or publish-style verification
- **THEN** it SHALL execute the offline fixture benchmark validation path as part of the default local release gate rather than leaving benchmark validation as an undocumented optional step

#### Scenario: New benchmark case is reviewable
- **WHEN** a developer adds a new real-repo benchmark case
- **THEN** the case SHALL be represented in versioned fixtures so reviewers can understand the expected product behavior without reading local database state
