## ADDED Requirements

### Requirement: Governance drift detector surfaces lifecycle misuse
The system SHALL surface stale or superseded governance rule reuse as advisory drift evidence that asks for human review instead of mutating rule lifecycle automatically.

#### Scenario: Superseded rule reuse produces lifecycle signal
- **WHEN** recent change context, archived change text, roadmap text, or governance documentation appears to reuse a superseded governance rule as active guidance
- **THEN** the drift detector SHALL produce a source-linked `stale_rule` or equivalent lifecycle signal that identifies the superseded rule, its replacement when known, and the human decision needed

#### Scenario: Stale rule reuse produces lifecycle signal
- **WHEN** recent context appears to reuse a stale governance rule as active guidance
- **THEN** the drift detector SHALL produce a source-linked lifecycle signal that asks whether the rule should remain stale, be restored through a new explicit decision, or be replaced by a new accepted rule

#### Scenario: Lifecycle drift remains advisory
- **WHEN** lifecycle misuse is detected
- **THEN** the drift detector SHALL NOT automatically update lifecycle status, create replacement rules, rewrite specs, or block CI by default

#### Scenario: Guardrail can ask a concrete lifecycle question
- **WHEN** lifecycle misuse causes the agent guardrail to include drift evidence
- **THEN** the resulting human question or recommended action SHALL clearly ask what to do with the stale or superseded rule rather than treating the inactive rule as authoritative enforcement input
