## ADDED Requirements

### Requirement: Agent guardrail exposes workflow protocol guidance
The system SHALL expose agent-facing workflow protocol guidance in the guardrail result so agents can translate governance status into allowed and disallowed next actions.

#### Scenario: Continue protocol permits normal work with validation
- **WHEN** the guardrail returns `agent_status: continue`
- **THEN** the result SHALL instruct the agent that it may continue normal work while still running targeted validation and reporting the guardrail status in the handoff

#### Scenario: Caution protocol requires action or disclosure
- **WHEN** the guardrail returns `agent_status: caution`
- **THEN** the result SHALL instruct the agent that it may continue only after addressing or explicitly reporting recommended next actions and caution evidence

#### Scenario: Pause protocol stops implementation
- **WHEN** the guardrail returns `agent_status: pause`
- **THEN** the result SHALL instruct the agent to stop implementation and ask for human review before continuing

### Requirement: Agent guardrail identifies allowed and disallowed next actions
The system SHALL include machine-readable allowed and disallowed next actions that reflect the current guardrail status.

#### Scenario: Allowed actions are status-specific
- **WHEN** the guardrail completes
- **THEN** the result SHALL include `allowed_next_actions` values that match the current status, such as continuing with validation for `continue`, addressing or reporting advisory concerns for `caution`, and asking a human for `pause`

#### Scenario: Disallowed actions prevent unsafe self-remediation
- **WHEN** the guardrail returns `agent_status: pause`
- **THEN** the result SHALL include `disallowed_next_actions` that prevent the agent from silently rewriting code, OpenSpec artifacts, roadmap documents, governance documents, or accepted rules to clear the pause

#### Scenario: Advisory mode remains explicit
- **WHEN** the guardrail returns protocol guidance
- **THEN** the result SHALL keep advisory-only semantics explicit and SHALL NOT imply default CI enforcement

### Requirement: Agent guardrail produces concrete human questions for pause
The system SHALL produce concrete human decision questions when the guardrail requires human review and source evidence provides a decision point.

#### Scenario: Human decisions are converted to questions
- **WHEN** the guardrail result contains `human_decisions_needed`
- **THEN** the protocol guidance SHALL expose those decisions as concrete questions the agent can ask the human

#### Scenario: Pause findings produce review questions
- **WHEN** the guardrail pauses because of missing OpenSpec context, missing validation evidence, accepted-rule conflict, blocked diff check, or review-required drift
- **THEN** the protocol guidance SHALL include a human question or review prompt tied to the relevant finding or signal evidence

#### Scenario: Questions cite traceable evidence
- **WHEN** the guardrail emits human questions
- **THEN** the result SHALL preserve enough evidence references through findings, signals, or source results for the agent to explain why each question is being asked

### Requirement: Agent guardrail provides reusable handoff summary
The system SHALL provide a concise governance handoff summary that can be reused in agent final responses, PR descriptions, and commit handoffs.

#### Scenario: Handoff summary includes core fields
- **WHEN** the guardrail completes
- **THEN** the handoff summary SHALL include agent status, diff status, drift status, required tests, human questions, and recommended next actions where present

#### Scenario: Handoff summary discloses caution and pause evidence
- **WHEN** the guardrail returns `agent_status: caution` or `agent_status: pause`
- **THEN** the handoff summary SHALL include the advisory evidence or decision request instead of reporting only that tests passed

#### Scenario: Handoff summary stays machine-readable
- **WHEN** the guardrail emits the handoff summary
- **THEN** the summary SHALL be available in the machine-readable JSON result without requiring an external LLM provider
