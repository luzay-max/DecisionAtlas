## ADDED Requirements

### Requirement: Readiness history can archive one-command rehearsal bundles
Readiness evidence history SHALL support release rehearsal bundle outputs as dated/versioned evidence.

#### Scenario: Rehearsal bundle is supplied
- **WHEN** a release rehearsal JSON path is supplied to readiness history archival
- **THEN** the archive SHALL preserve the bundle status, generated paths, and lane summaries.

#### Scenario: History archival is skipped
- **WHEN** the operator does not request archival
- **THEN** the rehearsal SHALL still write `.tmp` JSON and Markdown and mark history as `operator_guided`.
