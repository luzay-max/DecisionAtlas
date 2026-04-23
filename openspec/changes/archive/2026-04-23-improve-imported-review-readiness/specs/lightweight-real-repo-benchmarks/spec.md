## MODIFIED Requirements

### Requirement: Curated real-repo benchmark fixtures
The system SHALL provide a small fixture-backed benchmark set for real imported repositories that captures repo-level expectations, review-readiness milestones, and focused why/drift cases without requiring live imports during default validation, and SHALL allow fixture-backed expectations for candidate-conversion behavior on repositories used to protect imported review-readiness improvements.

#### Scenario: Fixture set validates without live services
- **WHEN** the benchmark validation is run without live mode
- **THEN** the system SHALL validate that the real-repo benchmark fixtures are present, well-formed, and contain required expectations without calling GitHub, model providers, or local APIs

#### Scenario: Fixture set includes focused case expectations
- **WHEN** benchmark fixtures describe a repository with known why or drift regression cases
- **THEN** the fixtures SHALL include case-level expectations such as workspace slug, question or alert pattern, expected broad status, and minimum citation or confidence requirements

#### Scenario: Fixture set includes candidate-conversion expectations
- **WHEN** a curated repository is used to protect improvement of the screened-in-to-candidate funnel
- **THEN** the fixture set SHALL be able to express broad expectations such as minimum reviewable candidates or other bounded candidate-conversion outcomes without relying on exact answer prose or local database snapshots

#### Scenario: Fixture set includes first accepted baseline expectations
- **WHEN** a curated repository is used to protect imported review-readiness improvements after review
- **THEN** the fixture set SHALL be able to express bounded milestone expectations such as minimum accepted decisions or expected imported why readiness after the first acceptance without relying on exact local database state
