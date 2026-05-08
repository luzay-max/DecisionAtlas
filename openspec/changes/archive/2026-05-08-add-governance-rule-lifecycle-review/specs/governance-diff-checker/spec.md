## ADDED Requirements

### Requirement: Governance checker preserves lifecycle review traceability
The system SHALL keep checker authority limited to accepted active current governance rules while preserving lifecycle review evidence for stale or superseded rule context.

#### Scenario: Current accepted replacement is authoritative
- **WHEN** a current accepted rule supersedes an older accepted rule and the current diff matches the replacement rule
- **THEN** the checker SHALL treat the replacement rule as authoritative and include its source, review, and lifecycle metadata in matched-rule output

#### Scenario: Superseded rule is not authoritative
- **WHEN** the current diff appears to match a superseded accepted rule
- **THEN** the checker SHALL NOT create a blocker finding solely from the superseded rule and SHALL preserve enough lifecycle evidence to explain that the rule is no longer authoritative when such evidence is available

#### Scenario: Stale rule is not authoritative
- **WHEN** the current diff appears to match a stale accepted rule
- **THEN** the checker SHALL NOT create a blocker finding solely from the stale rule and SHALL preserve enough lifecycle evidence to explain that the rule is no longer authoritative when such evidence is available

#### Scenario: Checker output remains additive
- **WHEN** lifecycle traceability is included in checker output
- **THEN** the system SHALL preserve existing `status`, `findings`, `matched_rules`, `conflicts`, `required_tests`, and `recommended_next_action` fields
