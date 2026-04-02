## ADDED Requirements

### Requirement: Drift follow-up alerts collapse repeated weak signals
The system SHALL reduce repeated low-signal drift alerts when multiple later artifacts continue the same accepted decision thread without implying a new replacement decision.

#### Scenario: Repeated implementation follow-ups collapse into one review thread
- **WHEN** multiple later artifacts point to the same accepted decision and mostly reflect rollout, cleanup, or bugfix follow-up work for the same chosen option
- **THEN** the system SHALL avoid emitting a separate weak alert for each artifact and SHALL instead surface a compact grouped follow-up signal

#### Scenario: Single weak follow-up signal remains visible
- **WHEN** only one later artifact weakly overlaps an accepted decision without stronger replacement evidence
- **THEN** the system SHALL still be able to emit one `needs_review` style signal rather than dropping the alert entirely

### Requirement: Drift follow-up logic distinguishes continuation from change
The system SHALL treat implementation continuation differently from evidence that the accepted decision itself changed.

#### Scenario: Implementation continuation stays weaker than decision change
- **WHEN** later artifacts continue implementing the same chosen option or close out known operational gaps
- **THEN** the system SHALL classify that material as follow-up review context instead of implying a new decision change

#### Scenario: Strong replacement signal bypasses follow-up grouping
- **WHEN** a later artifact includes stronger replacement evidence that satisfies the supersession bar
- **THEN** the system SHALL preserve an independent `possible_supersession` alert instead of folding it into grouped follow-up noise reduction
