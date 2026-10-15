## ADDED Requirements

### Requirement: Release evidence can be orchestrated by release rehearsal
Release evidence automation SHALL be usable as a lane in the one-command release rehearsal bundle.

#### Scenario: Release evidence JSON is provided
- **WHEN** a release evidence JSON path is supplied to the rehearsal command
- **THEN** the rehearsal SHALL include its status, summary, and evidence path.

#### Scenario: Release evidence is not provided
- **WHEN** release evidence is omitted
- **THEN** the rehearsal SHALL preserve the release lane as `not_provided` or run it only when explicitly requested.
