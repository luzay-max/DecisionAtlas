## ADDED Requirements

### Requirement: Imported review queues explain precision ranking and duplicate context
The imported review experience SHALL expose the canonical precision tier, ranking reasons, extraction origin, and near-duplicate context needed to understand queue order without presenting the ranking as an approval decision.

#### Scenario: Queue summarizes precision tiers
- **WHEN** an imported review queue contains candidate decisions
- **THEN** the page SHALL summarize the number of strong, partial, weak, and secondary duplicate candidates

#### Scenario: Review card explains queue position
- **WHEN** an imported candidate has a precision profile
- **THEN** its review card SHALL show its tier and bounded reasons including extraction origin when known

#### Scenario: Duplicate member points to representative
- **WHEN** an imported candidate is a secondary member of a near-duplicate cluster
- **THEN** its review card SHALL identify the cluster size and link to or name the representative candidate

#### Scenario: Weak candidates remain visible
- **WHEN** a candidate is weak or a secondary duplicate
- **THEN** it SHALL remain individually visible and reviewable rather than being automatically hidden or rejected

#### Scenario: Ranking does not imply acceptance
- **WHEN** a candidate is classified strong or ranked first
- **THEN** the review experience SHALL still require an explicit human review action before it becomes accepted
