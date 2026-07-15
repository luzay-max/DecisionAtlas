# sparse-conversion-benchmark-trends Specification

## Purpose
TBD - created by archiving change benchmark-sparse-conversion-trends. Update Purpose after archive.
## Requirements
### Requirement: Sparse conversion metrics are normalized per repository
The system SHALL normalize bounded sparse conversion metrics into each real-repository benchmark snapshot row when the source import summary provides them.

#### Scenario: Normal candidates are present
- **WHEN** a repository import creates normal candidates before sparse recovery
- **THEN** the snapshot SHALL record normal attempts/candidates and mark sparse recovery as `skipped` with its explicit skip reason

#### Scenario: Sparse recovery is attempted
- **WHEN** normal extraction yields no candidates and the bounded sparse lane runs
- **THEN** the snapshot SHALL record eligible artifacts, attempted artifacts, model attempts, recovered candidates, rejection reasons, elapsed time, and sparse status

#### Scenario: Provider failure occurs
- **WHEN** sparse or normal extraction is interrupted by a provider or operational failure
- **THEN** the snapshot SHALL preserve the failure category and partial counters without claiming a clean conversion result

#### Scenario: Legacy source has no sparse fields
- **WHEN** a benchmark report or import summary has no sparse conversion fields
- **THEN** normalization SHALL return `not_provided` sparse status and SHALL NOT infer zero attempts or recovered candidates

### Requirement: Sparse metrics are compared with explicit movement
The system SHALL compare current and baseline sparse metrics per repository with bounded numeric deltas, yield changes, rejection-reason changes, and an explicit movement state.

#### Scenario: Recovered yield improves
- **WHEN** current recovered yield is higher than the baseline and no operational blocker exists
- **THEN** the comparison SHALL expose the current value, baseline value, positive delta, and `improved` or equivalent non-regressed movement

#### Scenario: Recovered yield regresses
- **WHEN** current recovered yield or candidate yield is lower than the baseline
- **THEN** the comparison SHALL mark the repository as `regressed` and include a bounded reason naming the changed metric

#### Scenario: Repository is missing from one side
- **WHEN** a repository exists in the fixed pool but is absent from the current or baseline snapshot
- **THEN** the comparison SHALL preserve missing coverage and SHALL NOT treat it as unchanged

#### Scenario: Rejection reasons change
- **WHEN** current rejection reasons differ from the baseline
- **THEN** the comparison SHALL expose added and removed reason categories without including raw provider output

### Requirement: Repository profiles define sparse expectations
The system SHALL associate each fixed benchmark repository with a bounded profile and explicit sparse-conversion expectations.

#### Scenario: Profile metadata validates offline
- **WHEN** the fixed pool is validated without network or provider access
- **THEN** profile names and expectation fields SHALL be validated deterministically

#### Scenario: Zero-candidate outcome is allowed explicitly
- **WHEN** a profile allows zero candidates or sparse recovery exhaustion
- **THEN** the trend report SHALL preserve that outcome as an observed limitation rather than converting it to a pass or failure without context

### Requirement: Trend evidence preserves non-clean states
The system SHALL generate JSON and Markdown sparse trend evidence that keeps zero-candidate, provider failure, product limitation, operator-guided setup, missing coverage, and regression states visible.

#### Scenario: Trend has mixed repository outcomes
- **WHEN** one repository improves while another is operationally blocked or zero-candidate
- **THEN** the report SHALL show each repository state and overall status SHALL remain warning or blocking according to the existing evidence policy

#### Scenario: Comparison is omitted
- **WHEN** an operator generates trend evidence without a current comparison
- **THEN** the report SHALL write `not_provided` rows and recommended follow-up rather than claiming trend coverage

### Requirement: Sparse trend evidence is release-safe and deterministic
The system SHALL avoid secrets, private source content, raw model output, unbounded local paths, and nondeterministic repository ordering in sparse trend evidence.

#### Scenario: Evidence is shared
- **WHEN** an operator shares the generated Markdown or JSON
- **THEN** it SHALL contain only bounded repository identifiers, metrics, statuses, provider mode/model labels, timestamps, and follow-up guidance

#### Scenario: Same inputs are rerun
- **WHEN** the same pool, snapshots, seed, and generated timestamp are supplied again
- **THEN** repository order, metric deltas, movement labels, and summary counts SHALL remain identical
