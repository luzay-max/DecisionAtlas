## ADDED Requirements

### Requirement: Agent guardrail supports default local development protocol
The system SHALL define a default local development protocol that uses the AI-agent governance guardrail for non-trivial AI-assisted and developer-driven changes.

#### Scenario: Protocol runs before implementation
- **WHEN** a developer or AI agent starts a non-trivial change that may affect application behavior, specs, roadmap, governance documents, validation expectations, or project direction
- **THEN** the default protocol SHALL instruct the actor to run a governance preflight before implementation begins

#### Scenario: Protocol runs after implementation
- **WHEN** implementation work is complete enough to claim readiness
- **THEN** the default protocol SHALL instruct the actor to run targeted validation and governance postflight before reporting completion

#### Scenario: Protocol runs before archive or commit
- **WHEN** a developer or AI agent prepares to archive an OpenSpec change or commit completed work
- **THEN** the default protocol SHALL instruct the actor to run the governance guardrail and include any `caution` or `pause` evidence in the handoff

### Requirement: Development protocol exposes compact governance status
The system SHALL provide a compact local status surface for the default development protocol.

#### Scenario: Status includes OpenSpec context
- **WHEN** the protocol status is requested from the repository root
- **THEN** the result SHALL include active OpenSpec change context or explicitly state that no active change is present

#### Scenario: Status includes guardrail result
- **WHEN** the protocol status is requested from the repository root
- **THEN** the result SHALL include the current guardrail status, diff status, drift status, recommended actions, required tests, and human questions when available

#### Scenario: Status includes handoff guidance
- **WHEN** the protocol status is requested from the repository root
- **THEN** the result SHALL include concise handoff guidance suitable for AI final responses, commit notes, or implementation summaries

### Requirement: Development protocol preserves advisory semantics
The system SHALL keep the default development protocol advisory and SHALL NOT convert guardrail output into default CI enforcement.

#### Scenario: Continue does not imply correctness
- **WHEN** the protocol reports `continue`
- **THEN** the handoff guidance SHALL still require targeted validation and normal review before claiming completion

#### Scenario: Caution requires disclosure or action
- **WHEN** the protocol reports `caution`
- **THEN** the handoff guidance SHALL require the actor to address or explicitly disclose recommended actions before claiming completion

#### Scenario: Pause requires human review
- **WHEN** the protocol reports `pause`
- **THEN** the handoff guidance SHALL require the actor to stop and ask for the human decision needed before continuing

#### Scenario: Protocol does not mutate project artifacts
- **WHEN** the protocol reports `caution` or `pause`
- **THEN** the system SHALL NOT automatically modify application code, OpenSpec artifacts, roadmap documents, governance documents, accepted rules, or CI configuration
