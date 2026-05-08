## ADDED Requirements

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
