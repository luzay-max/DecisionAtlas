## ADDED Requirements

### Requirement: Hosted operator guide supports delivery readiness handoff
Hosted operator guidance SHALL describe how to produce and use a bounded delivery readiness handoff before external preview.

#### Scenario: Guide points to readiness generation
- **WHEN** an operator reads the hosted demo operator guide
- **THEN** the guide SHALL identify the hosted readiness command or runbook flow used to generate external preview evidence.

#### Scenario: Guide explains stop/go rules
- **WHEN** the guide describes external preview preparation
- **THEN** it SHALL state that core hosted service or seeded public walkthrough blockers stop the public walkthrough unless explicitly excluded.

#### Scenario: Guide preserves lane boundaries
- **WHEN** the guide describes optional governance, imported repository, private access, or benchmark lanes
- **THEN** it SHALL keep those lanes separate from the stable `demo-workspace` public walkthrough.

### Requirement: Hosted operator recovery evidence is explicit
Hosted operator guidance SHALL require recovery status to be recorded before external preview handoff.

#### Scenario: Recovery status is recorded
- **WHEN** reset or reseed is rehearsed before external preview
- **THEN** the operator handoff SHALL record whether recovery passed, was not run, was blocked, or remains operator-guided.

#### Scenario: Recovery boundary is documented
- **WHEN** the operator handoff mentions recovery
- **THEN** it SHALL state that default reset and reseed actions are scoped to `demo-workspace` and do not implicitly delete imported workspaces.
