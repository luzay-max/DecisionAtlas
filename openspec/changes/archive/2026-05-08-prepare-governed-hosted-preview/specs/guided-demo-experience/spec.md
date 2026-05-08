## ADDED Requirements

### Requirement: Governed hosted walkthrough has a bounded second act
The system SHALL keep the seeded guided demo as the first public walkthrough during governed hosted preview and SHALL present governance capabilities as a bounded second act after the viewer understands the core decision-memory flow.

#### Scenario: Walkthrough starts with stable guided demo
- **WHEN** an operator follows the governed hosted preview script
- **THEN** the script SHALL begin with `demo-workspace` dashboard, review, why-search, timeline, and drift before introducing governance-specific surfaces

#### Scenario: Governance second act is explicitly bounded
- **WHEN** the walkthrough transitions to governance Markdown ingest, accepted rules, or agent guardrail output
- **THEN** it SHALL explain that governance rules are human-reviewed and guardrails are advisory by default rather than automatic production enforcement

#### Scenario: Optional lanes do not interrupt the core walkthrough
- **WHEN** the walkthrough mentions live repository import, private repository access, GitHub App sync, or real-repository benchmark reports
- **THEN** it SHALL frame them as optional credibility or operator/admin lanes with provider, credential, hosted environment, and network dependencies

### Requirement: Governed preview copy preserves product boundaries
The system SHALL ensure governed hosted preview guidance does not imply production SaaS scope or default governance enforcement.

#### Scenario: Preview names production non-goals
- **WHEN** guided demo or preview docs describe the external hosted preview
- **THEN** they SHALL state that billing, full organization administration, secret vault, marketplace self-service, multiplayer review, and default CI enforcement are out of scope

#### Scenario: Caution and pause are explainable demo outcomes
- **WHEN** the demo script references guardrail `caution` or `pause`
- **THEN** it SHALL frame those statuses as evidence-backed human decision boundaries rather than hidden failures or automatic remediation requests
