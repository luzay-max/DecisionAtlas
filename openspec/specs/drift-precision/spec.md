## ADDED Requirements

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

### Requirement: Broad document families stay conservative
The system SHALL treat broad artifact families conservatively during semantic drift classification.

#### Scenario: Changelog-like artifact is downgraded from supersession
- **WHEN** a changelog, contributing guide, roadmap note, or implementation-planning artifact overlaps an accepted decision without unusually explicit replacement semantics
- **THEN** the system SHALL avoid classifying that artifact as `possible_supersession`

#### Scenario: Broad document can still require review
- **WHEN** a broad artifact family overlaps an accepted decision strongly enough to matter but not strongly enough to imply replacement
- **THEN** the system SHALL allow a `needs_review` alert instead of dropping the signal completely

### Requirement: Semantic drift summaries read as review guidance
The system SHALL describe semantic drift alerts with wording that reflects uncertainty and review intent.

#### Scenario: Possible supersession summary is cautious
- **WHEN** the system emits a `possible_supersession` alert
- **THEN** the summary SHALL describe it as a possible replacement signal rather than as an already-confirmed decision change

#### Scenario: Needs review summary stays broad
- **WHEN** the system emits a `needs_review` alert
- **THEN** the summary SHALL describe it as related follow-up work that deserves review rather than as implied replacement
