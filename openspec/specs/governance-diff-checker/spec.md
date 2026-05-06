## Purpose
Provide a local, advisory governance checker that lets developers and AI agents compare the current workspace diff against OpenSpec context, roadmap direction, accepted governance rules, and validation expectations before a change is merged.

## Requirements

### Requirement: Governance checker evaluates current changes against project context
The system SHALL provide a local governance check that evaluates the current workspace diff against bounded project context including active OpenSpec change information, main specs, roadmap documents, accepted governance rules, and recent project logs.

#### Scenario: Check uses current git diff
- **WHEN** a developer runs the governance checker in a workspace with uncommitted or staged changes
- **THEN** the checker SHALL include the current git diff as the primary change input

#### Scenario: Check reads OpenSpec context
- **WHEN** an active OpenSpec change exists
- **THEN** the checker SHALL include the active change proposal, design, specs, and tasks as governance context when available

#### Scenario: Check detects missing OpenSpec context
- **WHEN** the current diff changes product behavior or code without an active OpenSpec change
- **THEN** the checker SHALL return at least a warning finding that identifies missing OpenSpec context

#### Scenario: Check includes roadmap and main specs
- **WHEN** roadmap and main spec documents exist in the repository
- **THEN** the checker SHALL include bounded references to those documents when assessing project-direction alignment

### Requirement: Governance checker uses accepted rules as authoritative governance input
The system SHALL use accepted governance rules as authoritative checker input and SHALL NOT treat pending or rejected rule drafts as enforceable rules.

#### Scenario: Accepted rule can produce a finding
- **WHEN** the current diff appears to violate an accepted governance rule
- **THEN** the checker SHALL return a finding that references the matched accepted rule and source document metadata

#### Scenario: Pending rule is not enforceable
- **WHEN** the governance knowledge layer contains a pending rule draft that matches the current diff
- **THEN** the checker SHALL NOT create a blocker finding solely from that pending rule

#### Scenario: Rejected rule is ignored
- **WHEN** the governance knowledge layer contains a rejected rule draft that matches the current diff
- **THEN** the checker SHALL NOT treat that rejected rule as active governance input

### Requirement: Governance checker returns structured conservative results
The system SHALL return structured check results with an overall status, source-linked findings, matched rules, conflicts, required tests, and recommended next action.

#### Scenario: Passing check
- **WHEN** the current diff has OpenSpec context, no accepted-rule conflicts, and adequate validation evidence
- **THEN** the checker SHALL return `status: pass` with any informational findings bounded to non-blocking notes

#### Scenario: Warning check
- **WHEN** the current diff has incomplete evidence, ambiguous roadmap alignment, or missing recommended validation
- **THEN** the checker SHALL return `status: warning` with findings that explain what needs human attention

#### Scenario: Blocked check
- **WHEN** the current diff directly contradicts an accepted governance rule or lacks required OpenSpec context for non-trivial product behavior changes
- **THEN** the checker SHALL return `status: blocked` with source-linked blocker findings and a recommended next action

#### Scenario: Result is machine-readable
- **WHEN** the checker completes
- **THEN** it SHALL produce a machine-readable result containing `status`, `findings`, `matched_rules`, `conflicts`, `required_tests`, and `recommended_next_action`

### Requirement: Governance checker remains advisory by default
The system SHALL keep governance checker results advisory by default and SHALL NOT automatically modify code, rewrite governance rules, or block CI unless a future explicit change enables that behavior.

#### Scenario: Checker does not modify code
- **WHEN** the checker finds warnings or blockers
- **THEN** it SHALL NOT modify application code or OpenSpec artifacts automatically

#### Scenario: Checker does not rewrite rules
- **WHEN** the checker finds a conflict between current work and accepted governance rules
- **THEN** it SHALL recommend human review rather than changing accepted rules automatically

#### Scenario: Checker is not a default CI gate
- **WHEN** project validation runs through the existing default release or test commands
- **THEN** governance checker failures SHALL NOT block those commands unless a future change explicitly wires the checker into CI

### Requirement: Governance checker exposes validation and test expectations
The system SHALL identify likely validation or test expectations from the diff, active OpenSpec tasks, and accepted governance rules.

#### Scenario: Code change expects tests
- **WHEN** the current diff changes application behavior and no relevant test changes or documented validation evidence are detected
- **THEN** the checker SHALL return a warning or blocker finding that identifies missing validation evidence

#### Scenario: OpenSpec tasks mention validation
- **WHEN** active OpenSpec tasks include validation or test requirements
- **THEN** the checker SHALL include those requirements in `required_tests` or findings

#### Scenario: Recommended action is actionable
- **WHEN** the checker reports missing validation evidence
- **THEN** `recommended_next_action` SHALL name a concrete next step such as adding a targeted test, running a specific validation command, or documenting an environment-limited skip
