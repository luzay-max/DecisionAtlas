## Purpose
Define lightweight real-repository benchmark expectations for validating product quality.
## Requirements
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

### Requirement: Real-repository value reports are optional hosted-preview evidence
The system SHALL treat live real-repository value benchmark reports as optional hosted-preview credibility evidence that can support external discussions without becoming a prerequisite for the stable public walkthrough or default CI.

#### Scenario: Preview checklist marks real-repo value report optional
- **WHEN** hosted preview readiness references live real-repository validation
- **THEN** it SHALL classify JSON and Markdown value reports as optional operator-provided evidence rather than required guided-demo readiness

#### Scenario: Report status is summarized without committing stale output
- **WHEN** an operator generates a live real-repository value benchmark report for preview evidence
- **THEN** guidance SHALL tell the operator to summarize or attach the dated report externally and avoid committing default `.tmp/` generated reports as durable evidence

#### Scenario: Operational blockers do not block public demo
- **WHEN** live real-repository validation reports missing workspaces, provider failures, GitHub/network failure, or operational blockers
- **THEN** hosted preview readiness SHALL treat those outcomes as optional-lane limitations unless the external walkthrough explicitly depends on showing that repository

### Requirement: Real-repo benchmark history snapshots
The benchmark runner SHALL support a compact history snapshot format derived from live real-repository validation reports so benchmark evidence can be compared across releases without committing raw generated `.tmp` reports.

#### Scenario: Snapshot preserves bounded repository evidence
- **WHEN** a live real-repo validation report is converted into a history snapshot
- **THEN** the snapshot SHALL preserve generated date, benchmark version or schema version, repository id, repository role, benchmark purpose, value outcome, bounded outcome, pass state, key metrics, limitation categories, follow-up categories, why-case summary, drift-case summary, and operational error category when available

#### Scenario: Snapshot excludes volatile generated prose
- **WHEN** a benchmark history snapshot is written
- **THEN** it SHALL NOT require exact answer prose, raw model output, credentials, private repository content, or local-only `.tmp` paths as durable evidence

#### Scenario: Snapshot validation is offline deterministic
- **WHEN** default benchmark validation runs without live services
- **THEN** it SHALL validate committed or fixture-backed history snapshot shape without calling GitHub, model providers, local APIs, or existing imported workspaces

### Requirement: Real-repo benchmark comparison reports
The benchmark runner SHALL compare a current live real-repository validation report against a selected history snapshot and produce machine-readable plus operator-readable regression output.

#### Scenario: Repository movement is classified
- **WHEN** a current report row and baseline snapshot row share the same repository id
- **THEN** comparison output SHALL classify the repository movement as improved, unchanged, regressed, product-limited, operationally-blocked, or needs-review using bounded value outcome and metric evidence

#### Scenario: New and missing repositories are explicit
- **WHEN** the current report contains a repository not present in the baseline snapshot or the baseline contains a repository absent from the current report
- **THEN** comparison output SHALL classify the row as newly-evaluated or missing-from-current rather than silently dropping it

#### Scenario: Metric movement is summarized
- **WHEN** comparison output is generated
- **THEN** it SHALL summarize trend-relevant metric deltas such as candidate count, accepted count, strong candidate count, thin candidate ratio, why-case pass count, drift-case pass count, limitation categories, and follow-up categories when those fields are available

#### Scenario: Markdown comparison mirrors JSON
- **WHEN** benchmark comparison writes a machine-readable JSON report
- **THEN** it SHALL also be able to write an operator-readable Markdown report that mirrors the repository movement summary, overall counts, and recommended follow-up categories

### Requirement: Real-repo benchmark regression remains operator-guided
The system SHALL keep live real-repository benchmark comparison explicit and operator-guided while preserving deterministic offline validation.

#### Scenario: Default release gate stays offline
- **WHEN** the canonical local release gate or default benchmark command runs
- **THEN** it SHALL validate fixtures, snapshot shape, and comparison logic without requiring live benchmark execution, live providers, GitHub network access, or existing imported workspaces

#### Scenario: Live comparison uses explicit input paths
- **WHEN** an operator compares a current live benchmark report with a previous baseline
- **THEN** the command SHALL require explicit current and baseline report or snapshot paths instead of implicitly reading stale `.tmp` output

#### Scenario: Comparison output is release-evidence ready
- **WHEN** a live comparison report is generated
- **THEN** it SHALL include enough structured summary fields for a later release evidence automation step to reference pass counts, regression counts, operational blockers, and recommended follow-up categories

### Requirement: Benchmark comparison can be archived into readiness history
Real-repo benchmark comparison reports SHALL be usable as explicit input to readiness evidence history.

#### Scenario: Benchmark comparison is archived
- **WHEN** an operator archives readiness evidence with a benchmark comparison JSON path
- **THEN** the history entry SHALL preserve repository count, movement counts, regression count, improvement count, operational blocker count, and source artifact filename.

#### Scenario: Benchmark comparison is absent
- **WHEN** readiness history is archived without benchmark comparison evidence
- **THEN** the history entry SHALL record benchmark comparison as not provided rather than passed.

### Requirement: Live benchmark evidence distinguishes import setup from product result
Live real-repository benchmark evidence SHALL distinguish selected-but-not-imported repositories, successfully imported repositories, and imported repositories with product-quality limitations.

#### Scenario: Selected repository is not imported
- **WHEN** live benchmark validation targets a curated repository whose expected workspace is missing
- **THEN** the benchmark report SHALL classify the result as missing-workspace/operator-setup evidence and SHALL NOT count it as a product benchmark pass

#### Scenario: Repository is imported before benchmark
- **WHEN** live benchmark validation targets a curated repository whose expected workspace exists after public import rehearsal
- **THEN** the benchmark report SHALL evaluate the workspace as product evidence and include bounded readiness, candidate, why, drift, limitation, and follow-up fields

#### Scenario: Imported workspace has weak product evidence
- **WHEN** the imported workspace exists but benchmark observations show thin candidates, weak why support, drift limitations, or insufficient accepted baseline
- **THEN** the benchmark report SHALL classify those as product limitations or follow-up categories rather than operator setup failures
