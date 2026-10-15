## ADDED Requirements

### Requirement: Readiness history supports full delivery evidence families
Readiness evidence history SHALL support external install, real continuity rehearsal, team handoff, and Code Decision Audit evidence families in addition to release, hosted, and benchmark evidence.

#### Scenario: New evidence families are supplied
- **WHEN** archive generation receives external install evidence, real continuity rehearsal, team handoff, or Code Decision Audit JSON and Markdown paths
- **THEN** the history entry SHALL copy the supplied artifacts and record compact summaries for those families

#### Scenario: New evidence families are omitted
- **WHEN** archive generation omits one or more full delivery evidence families
- **THEN** the history entry SHALL mark the omitted families `not_provided` rather than omitting them from the entry

### Requirement: Readiness history trend includes delivery readiness signals
Readiness evidence history trend output SHALL include compact full delivery readiness signals.

#### Scenario: Trend is rendered
- **WHEN** trend Markdown is generated from entries containing full delivery evidence families
- **THEN** the trend SHALL expose release, hosted walkthrough, benchmark regressions, external install status, real continuity status, handoff status, audit status, warnings, operator-guided count, and not-provided count
