## ADDED Requirements

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
