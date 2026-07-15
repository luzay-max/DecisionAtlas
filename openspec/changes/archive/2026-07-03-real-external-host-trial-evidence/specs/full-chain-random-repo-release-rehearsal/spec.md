## ADDED Requirements

### Requirement: Full-chain rehearsal feeds real external host trial evidence
Full-chain random repo release rehearsal evidence SHALL be usable as a source for real external host trial evidence.

#### Scenario: Full-chain evidence is supplied to the trial gate
- **WHEN** real external host trial evidence receives full-chain random repo release JSON
- **THEN** it SHALL preserve full-chain status, selected repository identifiers, lane counts, blockers, warning lanes, operator-guided lanes, and not-provided lanes.

#### Scenario: Full-chain evidence is non-clean
- **WHEN** full-chain random repo release evidence has warning, blocking, operator-guided, or not-provided lanes
- **THEN** the real external host trial gate SHALL keep those states visible and SHALL NOT summarize the source as clean pass.
