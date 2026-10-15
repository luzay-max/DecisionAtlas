## ADDED Requirements

### Requirement: Readiness history can archive real external host trial evidence
Readiness evidence history SHALL support real external host trial evidence as a durable evidence family.

#### Scenario: Real external host trial evidence is supplied
- **WHEN** readiness history archival receives real external host trial JSON and Markdown
- **THEN** the archive SHALL preserve the status, host proof level, placeholder finding count, redaction finding count, selected repository identifiers, source statuses, blockers, and linked artifact filenames.

#### Scenario: Real external host trial evidence is omitted
- **WHEN** readiness history archival omits real external host trial evidence
- **THEN** history summaries SHALL keep that evidence family visible as `not_provided` rather than implying real external/customer-controlled host validation.

### Requirement: Readiness history trend includes real external host trial state
Readiness evidence history trend output SHALL include compact real external host trial readiness state.

#### Scenario: Trend is rendered
- **WHEN** trend Markdown is generated from entries containing real external host trial evidence
- **THEN** the trend SHALL expose real external host trial status, host proof level, warning counts, blocker counts, placeholder finding counts, operator-guided counts, and not-provided counts.
