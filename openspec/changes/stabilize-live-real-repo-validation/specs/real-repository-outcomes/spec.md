## MODIFIED Requirements

### Requirement: Imported workspaces expose real-analysis readiness
The system SHALL summarize imported-workspace readiness so users and validation operators can tell whether a real repository run is ready for review, has established an initial accepted-decision baseline, is ready for grounded why usage, is still evidence-limited, is blocked by low-yield extraction conversion, has failed operationally, or is better handled by reusing existing workspace state instead of blindly rerunning analysis, SHALL expose that readiness in a richer product-facing form that includes recommended actions and explicit downstream readiness for why and drift, and SHALL reserve `conversion_limited` for runs that still produce no reviewable candidate decisions after the refined candidate-conversion path has been attempted.

#### Scenario: Imported workspace is ready for review
- **WHEN** a live analysis run completes and the imported workspace contains reviewable candidate decisions but no accepted imported decisions yet
- **THEN** the workspace read model SHALL identify that the strongest next action is to review those candidate decisions and establish the first accepted baseline

#### Scenario: Imported workspace establishes a first accepted baseline
- **WHEN** an imported workspace accepts its first imported decision after review
- **THEN** the workspace read model SHALL stop treating the workspace as review-only progress and SHALL surface that an accepted baseline now exists for grounded downstream use

#### Scenario: Imported workspace is evidence-limited
- **WHEN** a live analysis run completes without enough accepted or candidate decisions to support meaningful downstream usage and the run did not show significant screened-in extraction loss
- **THEN** the workspace read model SHALL report that the workspace is evidence-limited and SHALL provide a next-step explanation rather than implying the run is fully ready

#### Scenario: Imported workspace is conversion-limited
- **WHEN** a live analysis run completes after many screened-in or full extraction attempts, the refined conversion path has been exhausted, and the workspace still yields no reviewable candidate decisions
- **THEN** the workspace read model SHALL expose that the workspace is conversion-limited and SHALL explain that extraction quality, not only repository evidence coverage, limited the result

#### Scenario: Existing imported workspace offers reuse actions
- **WHEN** a repository already has an imported workspace with prior import history
- **THEN** the product SHALL be able to present open-existing, incremental-sync, and full-rerun choices rather than forcing another blind full analysis

#### Scenario: Imported workspace is ready for why-search
- **WHEN** an imported workspace has accepted decisions with question-level grounding support
- **THEN** the readiness surface SHALL identify why-search as available and SHALL expose whether drift is also ready, stale, or still unevaluated

#### Scenario: Imported workspace provides bounded recommended actions
- **WHEN** the product renders an imported workspace in dashboard or search
- **THEN** it SHALL be able to use a backend-provided primary next action and secondary recommended actions rather than inventing different local readiness flows

#### Scenario: Improved candidate conversion moves workspace out of conversion-limited
- **WHEN** a repository previously prone to conversion-limited outcomes now produces at least one reviewable candidate through the refined conversion path
- **THEN** the workspace readiness SHALL move to `review_ready` instead of continuing to report `conversion_limited`

#### Scenario: Live validation classifies curated repositories into bounded outcomes
- **WHEN** an operator validates a curated public repository through the live real-repo validation flow
- **THEN** the observed outcome SHALL be classified into an explicit state family such as `review_ready`, `why_ready`, `evidence_limited`, `conversion_limited`, `analysis_failed`, `missing_workspace`, or `operational_failure`

#### Scenario: Live validation distinguishes product limitations from operational failures
- **WHEN** live validation cannot complete a why, drift, dashboard, or workspace request because of API availability, provider configuration, network, or missing workspace state
- **THEN** the result SHALL identify the failure as operational rather than presenting it as evidence-limited repository signal
