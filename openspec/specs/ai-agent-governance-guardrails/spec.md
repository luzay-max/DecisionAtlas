## Purpose
Provide a local, advisory AI-agent governance guardrail that aggregates current-diff governance checks and long-term governance drift reports into a single agent-facing result.
## Requirements
### Requirement: Agent guardrail aggregates governance signals
The system SHALL provide a local AI-agent governance guardrail that aggregates current-diff governance check results and long-term governance drift results into a single agent-facing advisory result.

#### Scenario: Aggregates diff and drift results
- **WHEN** an agent runs the governance guardrail in a repository with available governance checker and drift detector inputs
- **THEN** the guardrail SHALL include both current-diff check signals and long-term drift signals in the result

#### Scenario: Keeps source results traceable
- **WHEN** the guardrail returns an advisory result
- **THEN** the result SHALL preserve source result details or references sufficient to trace conclusions back to the diff checker and drift detector outputs

### Requirement: Agent guardrail returns conservative action status
The system SHALL normalize governance results into one of `continue`, `caution`, or `pause` for AI-agent consumption.

#### Scenario: Continue status
- **WHEN** the current-diff check passes and the drift report is clean or informational
- **THEN** the guardrail SHALL return `agent_status: continue`

#### Scenario: Caution status
- **WHEN** the current-diff check has warnings or the drift report has non-blocking watch or drift signals that do not require a human decision
- **THEN** the guardrail SHALL return `agent_status: caution`

#### Scenario: Pause status
- **WHEN** the current-diff check is blocked, the drift report requires review, an accepted-rule conflict is detected, required OpenSpec context is missing for behavior changes, an unsynced human decision is detected, or required validation evidence is missing for non-trivial implementation
- **THEN** the guardrail SHALL return `agent_status: pause`

### Requirement: Agent guardrail result is machine-readable
The system SHALL produce machine-readable output that includes agent status, evidence, required tests, human decision points, and recommended next actions.

#### Scenario: Result includes stable fields
- **WHEN** the guardrail completes
- **THEN** the result SHALL include `agent_status`, `summary`, `findings`, `signals`, `matched_rules`, `required_tests`, `human_decisions_needed`, `recommended_next_actions`, and `source_results`

#### Scenario: Recommended actions are actionable
- **WHEN** the guardrail reports caution or pause
- **THEN** `recommended_next_actions` SHALL identify concrete next steps such as updating OpenSpec context, adding validation evidence, asking for human decision, or syncing governance documentation

### Requirement: Agent guardrail remains advisory by default
The system SHALL keep AI-agent governance guardrails advisory by default and SHALL NOT automatically modify code, specs, roadmap documents, governance documents, accepted rules, or CI outcomes.

#### Scenario: Guardrail does not modify project files
- **WHEN** the guardrail finds caution or pause conditions
- **THEN** it SHALL NOT modify application code, OpenSpec artifacts, roadmap documents, governance documents, or accepted governance rules automatically

#### Scenario: Guardrail does not block CI by default
- **WHEN** project validation runs through existing default test or release commands
- **THEN** guardrail caution or pause results SHALL NOT fail those commands unless a future explicit change wires the guardrail into CI

### Requirement: Agent guardrail documents AI usage protocol
The system SHALL document how AI agents should run and interpret the governance guardrail before or after implementation.

#### Scenario: Documentation explains when to run
- **WHEN** an AI agent or developer reads the guardrail documentation
- **THEN** the documentation SHALL explain when to run the guardrail before implementation, after implementation, and before committing or archiving an OpenSpec change

#### Scenario: Documentation explains pause behavior
- **WHEN** the guardrail returns `agent_status: pause`
- **THEN** the documentation SHALL instruct the AI agent to stop and request human review instead of silently resolving governance conflicts

### Requirement: Agent guardrail participates in local development workflow
The system SHALL define governance guardrail checkpoints for developers and AI agents during local OpenSpec-driven development.

#### Scenario: Guardrail runs before implementation
- **WHEN** a developer or AI agent begins a non-trivial change that may affect code, specs, roadmap, governance documents, validation expectations, or project direction
- **THEN** the workflow SHALL instruct them to run the agent governance guardrail before implementation begins

#### Scenario: Guardrail runs after implementation
- **WHEN** implementation work is complete enough to claim the change is ready
- **THEN** the workflow SHALL instruct the developer or AI agent to run targeted validation and the agent governance guardrail before reporting completion

#### Scenario: Guardrail runs before archive and commit
- **WHEN** a developer or AI agent prepares to archive an OpenSpec change or commit completed work
- **THEN** the workflow SHALL instruct them to run the agent governance guardrail and include any `caution` or `pause` evidence in the handoff

### Requirement: Agent guardrail pause remains a human decision signal
The system SHALL keep `agent_status: pause` as an advisory signal that requires human review rather than automatic remediation or enforcement.

#### Scenario: Pause asks for human decision
- **WHEN** the guardrail returns `agent_status: pause`
- **THEN** the agent workflow SHALL require the agent to present the evidence and ask for the human decision needed before continuing

#### Scenario: Pause does not trigger automatic rewrites
- **WHEN** the guardrail returns `agent_status: pause`
- **THEN** the agent workflow SHALL NOT instruct the agent to silently rewrite application code, OpenSpec artifacts, roadmap documents, governance documents, or accepted rules to clear the pause

#### Scenario: Pause does not block CI by default
- **WHEN** default validation or release checks run
- **THEN** guardrail `pause` SHALL remain advisory unless a future explicit change introduces an enforcement mode

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

