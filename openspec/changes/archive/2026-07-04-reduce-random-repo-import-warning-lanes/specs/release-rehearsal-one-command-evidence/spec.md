## ADDED Requirements

### Requirement: Release rehearsal evidence can feed warning-lane reduction
One-command release rehearsal evidence SHALL be usable as an input source for warning-lane reduction.

#### Scenario: Release rehearsal evidence is supplied to reducer
- **WHEN** the warning-lane reducer receives release rehearsal JSON evidence
- **THEN** it SHALL preserve lane IDs, lane statuses, lane summaries, warning counts, operator-guided counts, missing lane counts, and recommended follow-up as source evidence.

#### Scenario: Release rehearsal contains operator-guided or warning lanes
- **WHEN** release rehearsal evidence includes warning or operator-guided lanes
- **THEN** the reducer SHALL classify those lanes into operator-guided, product-controlled, external dependency, not-provided, or blocking categories without changing the source release rehearsal status.
