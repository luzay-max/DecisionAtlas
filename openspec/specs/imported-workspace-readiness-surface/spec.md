## Purpose
Define readiness signals for imported workspaces before users begin review.
## Requirements
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

### Requirement: Imported readiness exposes recommended actions explicitly
The system SHALL expose a primary next action and a bounded set of recommended actions for imported workspaces so product surfaces and validation tooling do not invent their own readiness routing logic, and those actions SHALL distinguish between "review candidates now" and "use the accepted baseline now".

#### Scenario: Dashboard and search share the same imported actions
- **WHEN** dashboard and search render imported readiness for the same workspace
- **THEN** they SHALL be able to use the same backend-provided recommended actions instead of diverging in local heuristics

#### Scenario: First accepted baseline changes the primary next action
- **WHEN** an imported workspace moves from candidate-only review readiness to at least one accepted imported decision
- **THEN** the imported readiness contract SHALL be able to shift the primary next action away from generic review-only guidance toward why-use or continued baseline-strengthening guidance without requiring local UI heuristics

#### Scenario: Live validation detects readiness divergence
- **WHEN** live validation observes dashboard readiness and why/search readiness for the same imported workspace
- **THEN** it SHALL report a mismatch if the surfaces disagree on accepted-baseline state, primary next action, or allowed readiness state family

### Requirement: Readiness preserves private access-source status safely
Imported-workspace readiness summaries SHALL preserve token-backed access-source state without exposing credential material.

#### Scenario: Readiness includes private source status
- **WHEN** an imported workspace is bound to a token-backed private access source
- **THEN** the readiness summary SHALL include access-source label, authorization status, and bounded detail when available

#### Scenario: Readiness omits raw private token
- **WHEN** readiness data is returned for a token-backed workspace
- **THEN** the readiness summary SHALL NOT include raw token values or other credential material

#### Scenario: Readiness uses actionable private access copy
- **WHEN** a token-backed workspace has missing, unauthorized, or provider-failure access state
- **THEN** the readiness summary SHALL expose enough bounded context for the product to recommend setup, rotation, retry, or operator investigation

### Requirement: Imported readiness includes repeat-run state and actions
Imported-workspace readiness summaries SHALL include repeat-run state and recommended actions so dashboard and validation surfaces can explain whether the workspace should be opened, synced, rerun, reviewed, or inspected.

#### Scenario: Dashboard shows active import state
- **WHEN** an imported workspace has a queued or running import job
- **THEN** the readiness/dashboard summary SHALL expose active import status, active sync origin, and the active job identifier when available

#### Scenario: Dashboard shows latest completed sync state
- **WHEN** an imported workspace has a completed import or sync
- **THEN** the readiness/dashboard summary SHALL expose latest sync origin, latest sync timestamp, and last import summary in addition to review/why readiness

#### Scenario: Recommended actions distinguish review from sync
- **WHEN** an imported workspace has candidate decisions and also repeat-run actions available
- **THEN** readiness recommended actions SHALL distinguish review-next guidance from sync or full-rerun maintenance actions

#### Scenario: Validation can compare repeat-run state without UI scraping
- **WHEN** operator-guided validation checks a workspace dashboard
- **THEN** it SHALL be able to read active import, latest sync, and recommended action state from product APIs instead of scraping rendered UI text

### Requirement: Imported readiness documents repeat-run limitations
Imported-workspace readiness surfaces SHALL explain limitations that affect repeat-run decisions without implying the workspace is fully ready.

#### Scenario: Evidence-limited workspace can still be synced
- **WHEN** an imported workspace is evidence-limited but has an available incremental sync path
- **THEN** readiness copy SHALL make clear that sync may fetch newer artifacts but does not by itself guarantee accepted decision quality

#### Scenario: Failed latest import keeps prior readiness bounded
- **WHEN** the latest import failed but older workspace data exists
- **THEN** readiness SHALL distinguish the failed latest run from any previously usable review or accepted-decision baseline

#### Scenario: Private access issue blocks sync recommendation
- **WHEN** an imported private workspace has missing or unauthorized access-source state
- **THEN** readiness SHALL recommend setup, rotation, retry, or operator investigation before presenting incremental sync as a normal available action

### Requirement: Public import readiness records setup path
Imported-workspace readiness evidence SHALL expose whether a public GitHub workspace was created, reused, unavailable, or still operator-guided during rehearsal.

#### Scenario: Public import creates workspace
- **WHEN** a public GitHub rehearsal creates an imported workspace
- **THEN** readiness evidence SHALL include the workspace slug, repository identifier, setup path, and bounded readiness state without requiring UI scraping

#### Scenario: Public import reuses workspace
- **WHEN** a public GitHub rehearsal reuses an existing imported workspace
- **THEN** readiness evidence SHALL identify the reuse path and preserve the workspace's current readiness state

#### Scenario: Public import remains incomplete
- **WHEN** a public GitHub rehearsal cannot create or find the workspace
- **THEN** readiness evidence SHALL retain a non-pass setup state with a bounded reason such as missing local service, provider failure, network failure, or operator setup required

### Requirement: Imported readiness includes Git source metadata
Imported-workspace readiness summaries SHALL include safe Git source metadata such as provider, access mode, access-source label, authorization status, and setup outcome without exposing credential material.

#### Scenario: GitHub token-backed readiness is shown
- **WHEN** a token-backed GitHub workspace readiness summary is returned
- **THEN** the summary SHALL include provider `github`, access mode `token`, authorization status, and safe detail without exposing the token

#### Scenario: Unsupported provider readiness is shown
- **WHEN** a workspace or setup attempt is associated with a recognized but unsupported provider
- **THEN** readiness SHALL expose a bounded provider limitation and next action instead of implying that analysis failed

#### Scenario: Local path readiness is shown
- **WHEN** a workspace or setup attempt is associated with local-path access
- **THEN** readiness SHALL expose safe local-path setup status without rendering sensitive server path details to users without admin role
