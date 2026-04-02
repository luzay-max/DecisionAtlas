## ADDED Requirements

### Requirement: Supersession requires decision-layer replacement evidence
The system SHALL require evidence that a later artifact is replacing the accepted decision itself, not merely substituting an implementation detail underneath the same rationale, before emitting `possible_supersession`.

#### Scenario: Implementation substitution does not automatically imply supersession
- **WHEN** a later artifact strongly overlaps an accepted decision and includes replacement language, but the replacement appears scoped to an implementation primitive, dependency, or execution path rather than the accepted decision layer
- **THEN** the system SHALL avoid classifying that artifact as `possible_supersession`

#### Scenario: Decision-layer replacement can still imply supersession
- **WHEN** a later artifact strongly overlaps an accepted decision and clearly indicates that the accepted choice itself is being replaced, retired, or migrated away from
- **THEN** the system SHALL allow `possible_supersession`

### Requirement: Implementation substitutions remain reviewable
The system SHALL preserve review visibility for implementation-level substitutions that do not meet the stronger supersession boundary.

#### Scenario: Implementation substitution falls back to needs review
- **WHEN** a later artifact appears materially related to an accepted decision but does not provide enough evidence of decision-layer replacement
- **THEN** the system SHALL keep that signal in the weaker review path instead of dropping it entirely
