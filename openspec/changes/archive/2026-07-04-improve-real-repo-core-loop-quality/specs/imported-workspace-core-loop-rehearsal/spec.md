## ADDED Requirements

### Requirement: Core-loop lanes expose action categories
Imported workspace core-loop evidence SHALL expose an action category for each lane.

#### Scenario: Lane is not clean
- **WHEN** setup, review, why-search, drift, or guardrail produces a non-pass lane
- **THEN** the lane SHALL include an action category that downstream multi-repo diagnosis can aggregate.

#### Scenario: Lane is pass
- **WHEN** a lane produces clean evidence
- **THEN** the lane MAY omit action category or mark it as `pass` without creating follow-up counts.
