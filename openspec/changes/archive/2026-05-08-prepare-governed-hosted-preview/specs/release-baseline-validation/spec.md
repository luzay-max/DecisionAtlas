## ADDED Requirements

### Requirement: Governed hosted preview remains separate from release gates
The system SHALL keep governed hosted preview readiness distinct from mandatory release baseline validation and SHALL NOT require hosted URLs, live providers, real GitHub credentials, or guardrail enforcement for the default release gate.

#### Scenario: Release docs keep canonical gate primary
- **WHEN** release-facing docs mention governed hosted preview readiness
- **THEN** they SHALL continue to identify the canonical local pre-release command as the mandatory deterministic release gate

#### Scenario: Governed preview is a confidence layer
- **WHEN** readiness reports describe governance smoke, guardrail status, hosted health, hosted smoke, or live real-repository benchmark evidence
- **THEN** they SHALL classify that evidence as a post-release-candidate confidence layer rather than as a replacement for release validation

#### Scenario: Production SaaS limits remain visible
- **WHEN** governed hosted preview readiness is summarized for a milestone
- **THEN** the summary SHALL state that the preview is not a production SaaS release and does not include billing, full organization administration, secret vault, marketplace self-service, multiplayer review, or default governance enforcement
