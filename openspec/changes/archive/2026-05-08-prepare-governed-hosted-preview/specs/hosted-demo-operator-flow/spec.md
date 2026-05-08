## ADDED Requirements

### Requirement: Hosted preview includes governed readiness checks
The system SHALL define governed hosted preview readiness checks that cover the stable demo lane, governance demo lane, guardrail advisory state, recovery path, and optional real-repository credibility evidence without making those checks part of the default release gate.

#### Scenario: Governed checklist names required and optional lanes
- **WHEN** an operator prepares a governed hosted preview
- **THEN** the readiness checklist SHALL distinguish required stable guided-demo checks from optional governance, imported repository, GitHub App, private repository, and real-repository benchmark checks

#### Scenario: Governance smoke is part of operator readiness
- **WHEN** the checklist includes the governance lane
- **THEN** it SHALL identify the commands or product surfaces used to verify governance Markdown ingest, rule draft review, accepted-rule visibility, and agent guardrail summary behavior

#### Scenario: Readiness classification remains bounded
- **WHEN** an operator records governed hosted preview readiness
- **THEN** each lane SHALL be classified as pass, blocking, non-blocking, known limitation, or operator-guided rather than hidden behind a single readiness score

### Requirement: Hosted preview documents governed recovery and handoff
The system SHALL document how operators recover the stable demo lane and how they record governance guardrail evidence before externally demonstrating the governed preview.

#### Scenario: Recovery remains scoped to stable demo
- **WHEN** hosted preview recovery guidance mentions reset or reseed
- **THEN** it SHALL state that default recovery restores `demo-workspace` and does not implicitly delete imported workspaces or governance history

#### Scenario: Guardrail evidence is recorded before handoff
- **WHEN** an operator runs the agent governance guardrail before a governed hosted preview
- **THEN** the readiness record SHALL include the guardrail status and any caution or pause evidence that affects the preview

#### Scenario: Blocking readiness stops public walkthrough
- **WHEN** governed readiness finds a blocking issue in web, API, engine, seeded demo data, or walkthrough smoke
- **THEN** the operator guidance SHALL identify that the external public walkthrough should not proceed until the issue is resolved or explicitly excluded
