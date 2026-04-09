## ADDED Requirements

### Requirement: Strong drift alerts avoid implementation-heavy false positives
The system SHALL avoid promoting implementation-heavy fixes, lifecycle repairs, and support-path maintenance into `possible_supersession` unless stronger evidence shows the accepted decision itself is being displaced.

#### Scenario: Bugfix-heavy artifact stays out of strong replacement path
- **WHEN** a later artifact is dominated by bugfix, repair, or maintenance semantics and only weakly implies replacement of the accepted decision layer
- **THEN** the system SHALL avoid classifying that artifact as `possible_supersession`

#### Scenario: Lifecycle repair artifact stays reviewable but weaker
- **WHEN** a later artifact mainly repairs lifecycle, websocket, cookie, transport, or shutdown behavior while staying related to an accepted decision
- **THEN** the system SHALL keep that signal on the weaker review path instead of promoting it to a stronger replacement alert
