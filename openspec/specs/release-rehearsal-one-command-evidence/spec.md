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
The release rehearsal SHALL aggregate lane outcomes without hiding warnings or blockers.

#### Scenario: A lane is warning
- **WHEN** release, hosted readiness, benchmark trend, multi-repo diagnosis, guardrail, or history evidence reports warning
- **THEN** the top-level rehearsal status SHALL be warning unless a blocking lane exists.

#### Scenario: A lane is blocking
- **WHEN** any included lane reports blocking, provider failure, local stack failure, or command failure
- **THEN** the top-level rehearsal status SHALL be blocking and include recommended follow-up.

### Requirement: Release rehearsal evidence is customer-safe
The release rehearsal SHALL avoid writing secrets or raw private repository contents.

#### Scenario: Markdown is generated
- **WHEN** the Markdown bundle is written
- **THEN** it SHALL include only lane statuses, bounded summaries, evidence paths, and next actions.
