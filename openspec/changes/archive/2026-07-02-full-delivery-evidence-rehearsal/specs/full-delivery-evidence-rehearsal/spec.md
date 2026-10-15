## ADDED Requirements

### Requirement: Full delivery evidence rehearsal archives all delivery families
The system SHALL archive a complete self-hosted delivery evidence bundle from explicit evidence artifact paths.

#### Scenario: Full evidence archive is generated
- **WHEN** an operator supplies release evidence, hosted readiness, benchmark comparison, external install evidence, real continuity rehearsal, team handoff, and Code Decision Audit JSON or Markdown paths
- **THEN** the system SHALL copy the supplied artifacts into one dated readiness history entry and SHALL summarize each evidence family

#### Scenario: Full evidence is partially missing
- **WHEN** one or more optional full delivery evidence artifacts are omitted
- **THEN** the archive SHALL preserve those families as `not_provided` or equivalent non-pass state and SHALL NOT treat them as pass

### Requirement: Full delivery evidence rehearsal is customer-safe
The system SHALL keep the full delivery evidence archive safe for customer/operator review.

#### Scenario: Index is generated
- **WHEN** full delivery evidence is archived
- **THEN** the system SHALL update readiness history index and trend Markdown with compact family statuses, blocker counts, warning counts, and recommended follow-up without embedding secrets or raw private content

#### Scenario: Source artifact is missing or unreadable
- **WHEN** an explicitly supplied source path is missing, unreadable, or invalid JSON
- **THEN** the archive SHALL record a warning for that source and preserve the affected family as non-pass
