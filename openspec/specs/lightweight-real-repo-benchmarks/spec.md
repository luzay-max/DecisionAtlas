## Purpose
Define lightweight real-repository benchmark expectations for validating product quality.

## Requirements

### Requirement: Curated real-repo benchmark fixtures
The system SHALL provide a small fixture-backed benchmark set for real imported repositories that captures repo-level expectations, review-readiness milestones, focused why/drift cases, and operator-guided live observed outcomes without requiring live imports during default validation, SHALL allow fixture-backed expectations for candidate-conversion behavior on repositories used to protect imported review-readiness improvements, and SHALL allow why-specific expectations that protect stronger post-acceptance support quality without relying on exact answer prose.

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

#### Scenario: Fixture set protects post-acceptance why support quality
- **WHEN** a curated repository is used to protect imported why improvements after an accepted baseline exists
- **THEN** the fixture set SHALL be able to express bounded expectations such as expected why status family, minimum citations, and equivalent-question coverage without snapshotting exact answer wording

#### Scenario: Live mode records observed repository outcomes
- **WHEN** an operator runs live real-repo benchmark validation against an already running local stack
- **THEN** the system SHALL collect observed repository readiness, candidate counts, accepted baseline state, why status, and drift status for curated repositories and write an operator-readable report

#### Scenario: Live mode remains outside default release gate
- **WHEN** maintainers run the default offline benchmark or canonical pre-release gate
- **THEN** the system SHALL validate fixture shape and offline expectations without requiring live providers, GitHub network access, or existing imported workspaces

#### Scenario: Live mode reports missing or unavailable workspaces explicitly
- **WHEN** a curated repository workspace is missing, unreachable, or blocked by provider or network failure during live validation
- **THEN** the report SHALL classify that as an operational or missing-workspace outcome rather than silently treating it as a product evidence result
