## ADDED Requirements

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
