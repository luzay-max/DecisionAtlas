## MODIFIED Requirements

### Requirement: Imported workspace readiness is surfaced as a structured product summary
The system SHALL expose imported-workspace readiness as a compact structured summary that explains what the workspace is ready for now, why it is in that state, which actions are recommended next, whether the workspace has already established its first accepted-decision baseline, access-source label and authorization state for private repositories, and enough stable status fields for operator-guided live validation to compare dashboard and search behavior without duplicating UI heuristics.

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

#### Scenario: Private workspace surfaces access-source state
- **WHEN** an imported workspace is bound to a token-backed private repository access source
- **THEN** the product SHALL display the access-source label, authorization status, and authorization detail when available without exposing raw credential material

#### Scenario: Live validation can read readiness without UI scraping
- **WHEN** an operator-guided live validation command evaluates an imported workspace
- **THEN** it SHALL be able to use structured readiness fields from product APIs instead of scraping rendered UI text or reimplementing separate readiness heuristics
