## MODIFIED Requirements

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
