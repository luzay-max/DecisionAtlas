# release-rehearsal-one-command-evidence Specification

## Purpose

Defines the one-command release rehearsal bundle and output contract.
## Requirements
### Requirement: One-command release rehearsal bundle is generated
The system SHALL provide a single operator command that generates release rehearsal JSON and Markdown.

#### Scenario: Default rehearsal runs
- **WHEN** an operator runs the release rehearsal command without optional live flags
- **THEN** the command SHALL generate a top-level bundle with lane statuses, evidence paths, summaries, and recommended next actions.

#### Scenario: Optional evidence is missing
- **WHEN** an optional evidence input is not provided
- **THEN** the bundle SHALL mark that lane as `not_provided` or `operator_guided` rather than failing.

### Requirement: Release rehearsal preserves mixed outcomes
The release rehearsal SHALL aggregate release, hosted, benchmark comparison, sparse benchmark trend, multi-repo diagnosis, guardrail, and history lane outcomes without hiding warnings or blockers.

#### Scenario: A lane is warning
- **WHEN** release, hosted readiness, benchmark trend, sparse benchmark trend, multi-repo diagnosis, guardrail, or history evidence reports warning
- **THEN** the top-level rehearsal status SHALL be warning unless a blocking lane exists.

#### Scenario: A lane is blocking
- **WHEN** any included lane reports blocking, provider failure, local stack failure, or command failure
- **THEN** the top-level rehearsal status SHALL be blocking and include recommended follow-up.

### Requirement: Release rehearsal evidence is customer-safe
The release rehearsal SHALL avoid writing secrets or raw private repository contents.

#### Scenario: Markdown is generated
- **WHEN** the Markdown bundle is written
- **THEN** it SHALL include only lane statuses, bounded summaries, evidence paths, and next actions.

### Requirement: Release rehearsal can feed full-chain evidence
One-command release rehearsal evidence SHALL be usable as a source lane for full-chain random repository release rehearsal.

#### Scenario: Release rehearsal is supplied
- **WHEN** full-chain rehearsal receives release rehearsal JSON or Markdown
- **THEN** it SHALL preserve release status, lane counts, selected random repository evidence when present, and recommended follow-up.

#### Scenario: Release rehearsal is missing
- **WHEN** full-chain rehearsal runs without release rehearsal evidence
- **THEN** it SHALL mark the release rehearsal lane as `not_provided` or `operator_guided`.

### Requirement: Release rehearsal evidence can feed warning-lane reduction
One-command release rehearsal evidence SHALL be usable as an input source for warning-lane reduction.

#### Scenario: Release rehearsal evidence is supplied to reducer
- **WHEN** the warning-lane reducer receives release rehearsal JSON evidence
- **THEN** it SHALL preserve lane IDs, lane statuses, lane summaries, warning counts, operator-guided counts, missing lane counts, and recommended follow-up as source evidence.

#### Scenario: Release rehearsal contains operator-guided or warning lanes
- **WHEN** release rehearsal evidence includes warning or operator-guided lanes
- **THEN** the reducer SHALL classify those lanes into operator-guided, product-controlled, external dependency, not-provided, or blocking categories without changing the source release rehearsal status.

