## ADDED Requirements

### Requirement: Readiness history can archive customer-host v2 rehearsal
Readiness evidence history SHALL support customer-host v2 rehearsal artifacts as durable delivery evidence.

#### Scenario: Customer-host v2 evidence is supplied
- **WHEN** readiness history archival receives customer-host v2 JSON and Markdown
- **THEN** the archive SHALL preserve the bundle status, host proof level, lane summaries, blockers, limitations, and linked artifact filenames.

#### Scenario: Customer-host v2 evidence is omitted
- **WHEN** readiness history archival omits customer-host v2 evidence
- **THEN** history summaries SHALL keep that evidence family visible as `not_provided` rather than implying external customer-host validation.
