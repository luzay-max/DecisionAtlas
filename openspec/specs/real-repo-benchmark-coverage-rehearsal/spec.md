# real-repo-benchmark-coverage-rehearsal Specification

## Purpose

Operator-guided rehearsal that chains fixed-pool real-repo current report, snapshot, comparison, trend, and top-level release evidence.
## Requirements
### Requirement: Coverage rehearsal orchestrates benchmark artifacts
The system SHALL provide a real-repo benchmark coverage rehearsal command that produces or references current report, snapshot, comparison, sparse trend, and top-level rehearsal artifacts.

#### Scenario: Offline current report is supplied
- **WHEN** an operator supplies a current report JSON and baseline snapshot JSON
- **THEN** the rehearsal MUST generate snapshot, comparison, sparse trend, and top-level JSON/Markdown artifacts without calling GitHub, model providers, or local API endpoints

#### Scenario: Live local API mode is explicit
- **WHEN** an operator requests live mode
- **THEN** the rehearsal MUST run against the local API only after an explicit live flag and MUST record the target base URL, selected repo ids, and sparse metric source status

### Requirement: Rehearsal covers the fixed trend pool
The rehearsal command SHALL use the fixed real-repo trend pool as the expected coverage set.

#### Scenario: Fixed pool rows are absent from comparison
- **WHEN** generated comparison evidence does not include every fixed pool repository
- **THEN** the rehearsal MUST preserve the trend warning and list missing coverage in the generated summary

#### Scenario: Fixed pool rows are covered
- **WHEN** generated comparison evidence covers every fixed pool repository without regression or operational blockers
- **THEN** the rehearsal summary MAY report `pass`

### Requirement: Rehearsal artifacts are release-safe
The rehearsal command SHALL avoid writing secrets, private repository contents, raw model output, or unbounded local paths into release-facing JSON and Markdown.

#### Scenario: Rehearsal summary is shared
- **WHEN** an operator shares the generated Markdown summary
- **THEN** the summary MUST contain bounded statuses, artifact paths, repo identifiers, coverage counts, and recommended follow-up
