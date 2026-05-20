## ADDED Requirements

### Requirement: Self-hosted delivery rehearsal is repeatable
The system SHALL define a repeatable self-hosted delivery rehearsal that an operator can run before claiming customer handoff readiness.

#### Scenario: Operator starts a rehearsal
- **WHEN** an operator prepares a self-hosted delivery rehearsal
- **THEN** the rehearsal guidance SHALL identify the rehearsal label, target deployment mode, relevant commit or version label, evidence output paths, and required validation commands.

#### Scenario: Rehearsal uses existing baseline commands
- **WHEN** the rehearsal describes validation steps
- **THEN** it SHALL reference existing startup, health, OpenSpec strict validation, governance guardrail, release evidence, hosted/operator readiness, benchmark comparison, and readiness history commands where applicable.

### Requirement: Rehearsal evidence preserves non-clean states
The system SHALL preserve non-clean evidence states during self-hosted delivery rehearsal reporting.

#### Scenario: Evidence is not clean pass
- **WHEN** a rehearsal produces `warning`, `blocking`, `operator_guided`, `known_limitation`, or `not_provided` evidence
- **THEN** the rehearsal summary SHALL disclose that state
- **AND** it SHALL NOT present the affected lane as pass.

#### Scenario: Live inputs are absent
- **WHEN** hosted URLs, provider credentials, private repository credentials, or live benchmark inputs are unavailable
- **THEN** the rehearsal SHALL record an explicit operator-guided, known-limitation, not-provided, or blocking state with the rerun condition.

### Requirement: Rehearsal creates customer-readable handoff evidence
The system SHALL produce or require a customer/operator-readable rehearsal summary for self-hosted delivery.

#### Scenario: Rehearsal summary is prepared
- **WHEN** a rehearsal is completed or paused
- **THEN** the summary SHALL list tested scope, deployment mode, commands run, generated evidence artifacts, archived readiness history entry, limitations, and recommended next actions.

#### Scenario: Paid pilot handoff is prepared
- **WHEN** the rehearsal is used for a paid pilot or customer evaluation
- **THEN** the handoff SHALL reference the Code Decision Audit template or an equivalent report
- **AND** it SHALL include evidence statuses, drift/why-search readiness, benchmark comparison status, and limitations.

### Requirement: Rehearsal excludes premature SaaS commitments
The system SHALL keep self-hosted delivery rehearsal scope aligned with the self-hosted commercial baseline.

#### Scenario: Scope is documented
- **WHEN** the rehearsal describes product readiness
- **THEN** it SHALL state that billing, hosted multi-tenancy, Marketplace or self-service OAuth, hosted secret vault, managed hosted service operations, and runtime license enforcement are not validated by this rehearsal.
