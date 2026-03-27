## MODIFIED Requirements

### Requirement: Imported workspaces expose real-analysis readiness
The system SHALL summarize imported-workspace readiness so users can tell whether a real repository run is ready for review, still evidence-limited, blocked by low-yield extraction conversion, or better handled by reusing existing workspace state instead of blindly rerunning analysis.

#### Scenario: Imported workspace is ready for review
- **WHEN** a live analysis run completes and the imported workspace contains reviewable candidate decisions
- **THEN** the workspace read model SHALL identify that the strongest next action is to review those candidate decisions

#### Scenario: Imported workspace is evidence-limited
- **WHEN** a live analysis run completes without enough accepted or candidate decisions to support meaningful downstream usage and the run did not show significant screened-in extraction loss
- **THEN** the workspace read model SHALL report that the workspace is evidence-limited and SHALL provide a next-step explanation rather than implying the run is fully ready

#### Scenario: Imported workspace is conversion-limited
- **WHEN** a live analysis run completes after many screened-in or full extraction attempts but still yields no reviewable candidate decisions
- **THEN** the workspace read model SHALL expose that the workspace is conversion-limited and SHALL explain that extraction quality, not only repository evidence coverage, limited the result

#### Scenario: Existing imported workspace offers reuse actions
- **WHEN** a repository already has an imported workspace with prior import history
- **THEN** the product SHALL be able to present open-existing, incremental-sync, and full-rerun choices rather than forcing another blind full analysis
