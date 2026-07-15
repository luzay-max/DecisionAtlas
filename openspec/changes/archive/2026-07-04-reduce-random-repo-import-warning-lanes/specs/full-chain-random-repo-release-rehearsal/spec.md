## ADDED Requirements

### Requirement: Full-chain evidence can feed warning-lane reduction
Full-chain random repository release rehearsal evidence SHALL be usable as an input source for warning-lane reduction.

#### Scenario: Full-chain evidence is supplied to reducer
- **WHEN** the warning-lane reducer receives full-chain random repository release evidence
- **THEN** it SHALL preserve selected repository identifiers, lane IDs, lane statuses, lane summaries, blockers, limitations, and recommended next actions as source evidence.

#### Scenario: Full-chain evidence has non-clean lanes
- **WHEN** full-chain evidence includes warning, blocking, operator-guided, or not-provided lanes
- **THEN** the reducer SHALL classify those lanes without summarizing the full-chain evidence as clean pass.
