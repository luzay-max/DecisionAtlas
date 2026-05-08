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

### Requirement: Agent guardrail participates in governed hosted preview readiness
The system SHALL include the local AI-agent governance guardrail as an advisory readiness signal for governed hosted preview preparation without making guardrail results a default CI blocker.

#### Scenario: Preview readiness records guardrail status
- **WHEN** an operator prepares a governed hosted preview
- **THEN** the readiness record SHALL include the latest guardrail status, diff status, drift status, recommended actions, and any human questions when available

#### Scenario: Caution is disclosed or addressed
- **WHEN** the guardrail returns `agent_status: caution` during hosted preview preparation
- **THEN** operator guidance SHALL require the caution evidence to be addressed or explicitly disclosed in the readiness handoff before claiming the governed preview is ready

#### Scenario: Pause requires human decision before governance demo claims
- **WHEN** the guardrail returns `agent_status: pause` during hosted preview preparation
- **THEN** operator guidance SHALL require a human decision before using the guardrail result as positive governed-preview evidence

### Requirement: Guardrail preview story remains advisory
The system SHALL present agent guardrail output in governed hosted preview as advisory project governance memory rather than automatic enforcement.

#### Scenario: Demo explains advisory mode
- **WHEN** the external walkthrough shows guardrail output
- **THEN** it SHALL state that guardrail results guide agents and handoffs but do not automatically rewrite code, specs, roadmap, governance rules, or CI results

#### Scenario: Source evidence remains part of the story
- **WHEN** a guardrail status is shown or summarized during hosted preview
- **THEN** the walkthrough or handoff SHALL preserve source evidence such as findings, drift signals, matched rules, recommended actions, or source result references

### Requirement: Agent guardrail exposes opt-in enforcement preview
The system SHALL expose an opt-in governance enforcement preview derived from the existing agent guardrail result while preserving default advisory guardrail behavior.

#### Scenario: Default guardrail remains advisory
- **WHEN** a developer or AI agent runs the existing guardrail command without an enforcement preview option
- **THEN** the command SHALL preserve advisory-only semantics and SHALL NOT fail solely because the guardrail returns `caution` or `pause`

#### Scenario: Preview is explicit
- **WHEN** a developer or AI agent requests enforcement preview output
- **THEN** the result SHALL include machine-readable preview fields that identify the selected mode, whether stricter governance would block, and the reasons for that decision

#### Scenario: Preview preserves source evidence
- **WHEN** enforcement preview output reports a warning or would-block decision
- **THEN** the result SHALL preserve source evidence from findings, signals, human questions, recommended actions, or source results sufficient to explain the decision

### Requirement: Enforcement preview blocks only strong review signals
The system SHALL derive would-block preview decisions only from strong guardrail signals that already require human review.

#### Scenario: Pause would block in strict preview
- **WHEN** the guardrail result has `agent_status: pause`, a blocked diff check, or a review-required drift report
- **THEN** opt-in strict preview output SHALL report that stricter governance would block until a human decision is recorded

#### Scenario: Caution remains non-blocking
- **WHEN** the guardrail result has `agent_status: caution` without blocked diff status or review-required drift status
- **THEN** opt-in strict preview output SHALL report warning evidence without treating the result as a blocker

#### Scenario: Continue passes preview
- **WHEN** the guardrail result has `agent_status: continue`
- **THEN** opt-in strict preview output SHALL report no would-block decision and SHALL still remind users that targeted validation remains required

### Requirement: Enforcement preview supports local and report-oriented modes
The system SHALL support local strict preview and report-oriented preview output without requiring remote provider access.

#### Scenario: Local strict exit is opt-in
- **WHEN** a developer explicitly requests local strict exit behavior
- **THEN** the command MAY return a non-zero exit code only when opt-in preview output reports `would_block: true`

#### Scenario: PR annotation preview is report text
- **WHEN** a developer requests PR annotation preview output
- **THEN** the system SHALL produce local Markdown or machine-readable text suitable for a PR annotation without requiring GitHub API access

#### Scenario: Release checklist warning is report evidence
- **WHEN** a developer requests release checklist warning output
- **THEN** the system SHALL produce warning or would-block evidence that can be copied into release readiness records without modifying release gates automatically

### Requirement: Enforcement preview records false-positive override handoff
The system SHALL provide a source-linked human override handoff for false-positive preview blockers without automatically mutating project artifacts.

#### Scenario: Override prompt references evidence
- **WHEN** strict preview output reports `would_block: true`
- **THEN** the result SHALL include an override prompt or human question that references the relevant source evidence

#### Scenario: Override remains human-authored
- **WHEN** a human decides that a would-block preview result is a false positive
- **THEN** the system SHALL support recording that decision in handoff or report output and SHALL NOT automatically rewrite code, OpenSpec artifacts, roadmap documents, documentation, or accepted rules
