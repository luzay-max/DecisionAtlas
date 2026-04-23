## MODIFIED Requirements

### Requirement: Imported workspace readiness is surfaced as a structured product summary
The system SHALL expose imported-workspace readiness as a compact structured summary that explains what the workspace is ready for now, why it is in that state, which actions are recommended next, and whether the workspace has already established its first accepted-decision baseline.

#### Scenario: Review-ready workspace surfaces review-first guidance
- **WHEN** an imported workspace has candidate decisions ready for screening but has not yet accepted any imported decision
- **THEN** the product SHALL present review as the strongest next action and SHALL explain that downstream why/drift trust still depends on establishing an accepted baseline

#### Scenario: First accepted baseline surfaces stronger why guidance
- **WHEN** an imported workspace has established at least one accepted imported decision
- **THEN** the product SHALL surface that milestone in the imported readiness summary and SHALL explain that grounded why usage is now possible for questions anchored to that accepted decision

#### Scenario: Why-ready workspace surfaces why and drift readiness
- **WHEN** an imported workspace already has accepted decisions with sufficient downstream grounding
- **THEN** the product SHALL present that the workspace is ready for why-search and SHALL also expose whether drift is unevaluated, stale, clean, or alerting

#### Scenario: Limited workspace surfaces operational limitations
- **WHEN** an imported workspace is evidence-limited, conversion-limited, or analysis-failed
- **THEN** the product SHALL explain that limitation directly and SHALL recommend inspection or retry actions instead of implying the workspace is fully ready

### Requirement: Imported readiness exposes recommended actions explicitly
The system SHALL expose a primary next action and a bounded set of recommended actions for imported workspaces so product surfaces do not invent their own readiness routing logic, and those actions SHALL distinguish between "review candidates now" and "use the accepted baseline now".

#### Scenario: Dashboard and search share the same imported actions
- **WHEN** dashboard and search render imported readiness for the same workspace
- **THEN** they SHALL be able to use the same backend-provided recommended actions instead of diverging in local heuristics

#### Scenario: First accepted baseline changes the primary next action
- **WHEN** an imported workspace moves from candidate-only review readiness to at least one accepted imported decision
- **THEN** the imported readiness contract SHALL be able to shift the primary next action away from generic review-only guidance toward why-use or continued baseline-strengthening guidance without requiring local UI heuristics
