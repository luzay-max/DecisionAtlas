## ADDED Requirements

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

