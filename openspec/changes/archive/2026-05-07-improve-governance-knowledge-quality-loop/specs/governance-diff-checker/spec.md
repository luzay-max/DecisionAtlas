## MODIFIED Requirements

### Requirement: Governance checker uses accepted rules as authoritative governance input
The system SHALL use accepted active governance rules as authoritative checker input, SHALL preserve source and human-review traceability for matched accepted rules, and SHALL NOT treat pending, rejected, stale, or superseded rule drafts as enforceable rules.

#### Scenario: Accepted rule can produce a finding
- **WHEN** the current diff appears to violate an accepted active governance rule
- **THEN** the checker SHALL return a finding that references the matched accepted rule, source document metadata, source excerpt, review rationale when available, rule type, and lifecycle metadata

#### Scenario: Pending rule is not enforceable
- **WHEN** the governance knowledge layer contains a pending rule draft that matches the current diff
- **THEN** the checker SHALL NOT create a blocker finding solely from that pending rule

#### Scenario: Rejected rule is ignored
- **WHEN** the governance knowledge layer contains a rejected rule draft that matches the current diff
- **THEN** the checker SHALL NOT treat that rejected rule as active governance input

#### Scenario: Stale or superseded rule is ignored
- **WHEN** the governance knowledge layer contains a stale or superseded rule draft that matches the current diff
- **THEN** the checker SHALL NOT treat that draft as active authoritative governance input

### Requirement: Governance checker returns structured conservative results
The system SHALL return structured check results with an overall status, source-linked findings, matched rules, conflicts, required tests, recommended next action, and accepted-rule traceability metadata.

#### Scenario: Passing check
- **WHEN** the current diff has OpenSpec context, no accepted-rule conflicts, and adequate validation evidence
- **THEN** the checker SHALL return `status: pass` with any informational findings bounded to non-blocking notes

#### Scenario: Warning check
- **WHEN** the current diff has incomplete evidence, ambiguous roadmap alignment, or missing recommended validation
- **THEN** the checker SHALL return `status: warning` with findings that explain what needs human attention

#### Scenario: Blocked check
- **WHEN** the current diff directly contradicts an accepted active governance rule or lacks required OpenSpec context for non-trivial product behavior changes
- **THEN** the checker SHALL return `status: blocked` with source-linked blocker findings and a recommended next action

#### Scenario: Result is machine-readable
- **WHEN** the checker completes
- **THEN** it SHALL produce a machine-readable result containing `status`, `findings`, `matched_rules`, `conflicts`, `required_tests`, and `recommended_next_action`

#### Scenario: Matched rules include review traceability
- **WHEN** the checker returns a matched accepted rule
- **THEN** the matched rule SHALL include available source excerpt, source title, severity, scope, rule type, extraction reason, review rationale, and lifecycle metadata without requiring a separate database lookup
