## ADDED Requirements

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
