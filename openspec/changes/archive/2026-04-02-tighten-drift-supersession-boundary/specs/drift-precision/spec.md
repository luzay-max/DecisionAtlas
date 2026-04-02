## MODIFIED Requirements

### Requirement: Semantic drift classification prefers precision over broad overlap
The system SHALL require stronger semantic evidence for `possible_supersession` than broad topical similarity plus a generic replacement marker, and that evidence SHALL indicate replacement at the decision layer rather than only at an implementation layer.

#### Scenario: Explicit replacement language can produce possible supersession
- **WHEN** a later artifact strongly overlaps an accepted decision and includes explicit replacement or migration language that indicates the prior choice is being replaced
- **THEN** the system SHALL allow a `possible_supersession` alert

#### Scenario: Broad overlap alone does not produce possible supersession
- **WHEN** a later artifact overlaps an accepted decision but only provides broad topical similarity or procedural follow-up text
- **THEN** the system SHALL NOT emit `possible_supersession` on semantic overlap alone

#### Scenario: Implementation-level replacement does not over-trigger supersession
- **WHEN** a later artifact uses strong replacement language but appears to substitute a lower-level mechanism while preserving the broader accepted choice
- **THEN** the system SHALL avoid over-promoting that artifact to `possible_supersession`
