## ADDED Requirements

### Requirement: Release rehearsal can feed full-chain evidence
One-command release rehearsal evidence SHALL be usable as a source lane for full-chain random repository release rehearsal.

#### Scenario: Release rehearsal is supplied
- **WHEN** full-chain rehearsal receives release rehearsal JSON or Markdown
- **THEN** it SHALL preserve release status, lane counts, selected random repository evidence when present, and recommended follow-up.

#### Scenario: Release rehearsal is missing
- **WHEN** full-chain rehearsal runs without release rehearsal evidence
- **THEN** it SHALL mark the release rehearsal lane as `not_provided` or `operator_guided`.
