## MODIFIED Requirements

### Requirement: Imported workspaces expose real-analysis readiness
The system SHALL summarize imported-workspace readiness so users can tell whether a real repository run is ready for review, still evidence-limited, blocked by low-yield extraction conversion, or better handled by reusing existing workspace state instead of blindly rerunning analysis, and SHALL expose that readiness in a richer product-facing form that includes recommended actions and explicit downstream readiness for why and drift.

#### Scenario: Imported workspace is ready for review
- **WHEN** a live analysis run completes and the imported workspace contains reviewable candidate decisions
- **THEN** the workspace read model SHALL identify that the strongest next action is to review those candidate decisions

#### Scenario: Imported workspace is ready for why-search
- **WHEN** an imported workspace already has accepted decisions
- **THEN** the readiness surface SHALL identify why-search as available and SHALL expose whether drift is also ready, stale, or still unevaluated

#### Scenario: Imported workspace provides bounded recommended actions
- **WHEN** the product renders an imported workspace in dashboard or search
- **THEN** it SHALL be able to use a backend-provided primary next action and secondary recommended actions rather than inventing different local readiness flows
