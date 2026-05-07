## MODIFIED Requirements

### Requirement: Curated real-repo benchmark fixtures
The system SHALL provide a small fixture-backed benchmark set for real imported repositories that captures repo-level expectations, repository role and benchmark purpose, review-readiness milestones, focused why/drift cases, value-oriented outcome expectations, and operator-guided live observed outcomes without requiring live imports during default validation, SHALL allow fixture-backed expectations for candidate-conversion behavior on repositories used to protect imported review-readiness improvements, and SHALL allow why-specific expectations that protect stronger post-acceptance support quality without relying on exact answer prose.

#### Scenario: Fixture set validates without live services
- **WHEN** the benchmark validation is run without live mode
- **THEN** the system SHALL validate that the real-repo benchmark fixtures are present, well-formed, include repository role metadata, include value outcome expectations, and contain required expectations without calling GitHub, model providers, or local APIs

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
- **THEN** the system SHALL collect observed repository readiness, candidate counts, accepted baseline state, why status, drift status, candidate quality distribution, and value outcome classification for curated repositories and write an operator-readable report

#### Scenario: Live mode remains outside default release gate
- **WHEN** maintainers run the default offline benchmark or canonical pre-release gate
- **THEN** the system SHALL validate fixture shape and offline expectations without requiring live providers, GitHub network access, or existing imported workspaces

#### Scenario: Live mode reports missing or unavailable workspaces explicitly
- **WHEN** a curated repository workspace is missing, unreachable, or blocked by provider or network failure during live validation
- **THEN** the report SHALL classify that as an operational or missing-workspace outcome rather than silently treating it as a product evidence result

### Requirement: Benchmarks capture candidate value quality
The lightweight real-repository benchmark set SHALL capture candidate value quality expectations and observations without relying on exact generated prose, and SHALL summarize how candidate quality affects real-repository product usefulness.

#### Scenario: Fixture expresses candidate quality expectations
- **WHEN** a curated repository fixture is used to protect review quality
- **THEN** it SHALL be able to express expectations such as minimum strong candidates, maximum thin-candidate pressure, required provenance/source-ref availability, and expected value outcome family

#### Scenario: Live report includes candidate quality summary
- **WHEN** an operator runs live real-repo validation
- **THEN** the report SHALL summarize candidate quality observations and identify low-value candidate patterns as follow-up work when they appear

#### Scenario: Offline benchmark remains deterministic
- **WHEN** default validation runs without live services
- **THEN** it SHALL validate candidate-quality fixture shape without requiring GitHub, model providers, or existing imported workspaces

#### Scenario: Value outcome derives from bounded observations
- **WHEN** the live benchmark evaluates a curated repository
- **THEN** the report SHALL derive a bounded value outcome from observed readiness, candidate quality, accepted baseline, why-case support, drift-case usefulness, and operational availability rather than from exact generated answer prose

#### Scenario: Markdown report mirrors machine-readable evidence
- **WHEN** the live benchmark writes a machine-readable report
- **THEN** it SHALL also be able to write an operator-readable Markdown report that summarizes the same repository rows, value outcomes, key metrics, limitations, and follow-up actions

## ADDED Requirements

### Requirement: Real-repository benchmark reports are operator-readable
The benchmark runner SHALL produce an operator-readable real-repository value report that explains repository coverage, observed value outcomes, product limitations, operational blockers, and follow-up opportunities.

#### Scenario: Report summarizes curated repository coverage
- **WHEN** a live real-repository benchmark report is generated
- **THEN** it SHALL list each curated repository with its repository role, benchmark purpose, workspace slug, bounded outcome, and pass or follow-up state

#### Scenario: Report separates product limitations from operational blockers
- **WHEN** live benchmark validation encounters missing workspaces, local API failures, provider failures, or network failures
- **THEN** the report SHALL classify those rows as operational or missing-workspace outcomes instead of evidence-limited product outcomes

#### Scenario: Report records why and drift usefulness
- **WHEN** a curated repository has focused why or drift cases
- **THEN** the report SHALL summarize whether why-search hit the expected rationale thread and whether drift checks avoided forbidden false-positive outcomes

#### Scenario: Report can guide future optimization
- **WHEN** a benchmark report includes thin candidates, missing provenance, weak why support, or drift false-positive pressure
- **THEN** it SHALL identify those as follow-up categories that can guide future extraction, retrieval, or drift work
