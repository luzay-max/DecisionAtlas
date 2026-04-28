## ADDED Requirements

### Requirement: Benchmarks capture candidate value quality
The lightweight real-repository benchmark set SHALL capture candidate value quality expectations and observations without relying on exact generated prose.

#### Scenario: Fixture expresses candidate quality expectations
- **WHEN** a curated repository fixture is used to protect review quality
- **THEN** it SHALL be able to express expectations such as minimum strong candidates, maximum thin-candidate pressure, or required provenance/source-ref availability

#### Scenario: Live report includes candidate quality summary
- **WHEN** an operator runs live real-repo validation
- **THEN** the report SHALL summarize candidate quality observations and identify low-value candidate patterns as follow-up work when they appear

#### Scenario: Offline benchmark remains deterministic
- **WHEN** default validation runs without live services
- **THEN** it SHALL validate candidate-quality fixture shape without requiring GitHub, model providers, or existing imported workspaces
