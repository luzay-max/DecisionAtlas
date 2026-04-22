## MODIFIED Requirements

### Requirement: Live analysis reports honest outcomes
The system SHALL distinguish successful analysis, insufficient evidence, operational failure, imported-workspace readiness, existing-workspace reuse state, clearer import failure classes, and owner-aware repository access context so users can interpret live-analysis results correctly and know the strongest next action, and SHALL expose imported-workspace readiness in a form that product surfaces can reuse consistently after the import completes.

#### Scenario: Thin repository yields insufficient evidence
- **WHEN** a live analysis job completes but produces few or no candidate decisions because the repository lacks enough decision evidence
- **THEN** the system SHALL surface that outcome as insufficient evidence rather than implying the pipeline failed

#### Scenario: Review-ready workspace yields actionable outcome
- **WHEN** a live analysis job completes and the imported workspace contains reviewable candidate decisions
- **THEN** the system SHALL expose enough outcome context for the product to recommend review as the next action

#### Scenario: Runtime failure yields explicit failure context
- **WHEN** a live analysis job fails because of provider, network, or import execution errors
- **THEN** the system SHALL expose a failure summary that identifies the failing stage and broad failure category

#### Scenario: Existing repository is looked up before rerun
- **WHEN** the user enters a repository that already maps to an imported workspace inside the current owner scope
- **THEN** the live-analysis entry flow SHALL expose that reuse state before starting another import job

#### Scenario: Existing workspace from another owner scope is not leaked
- **WHEN** a repository already has an imported workspace in some other owner scope
- **THEN** the live-analysis entry flow SHALL NOT expose that other scope's workspace as reusable state for the current actor

#### Scenario: Network failure is distinguishable from repository failure
- **WHEN** a live analysis import fails while calling GitHub
- **THEN** the system SHALL distinguish retryable-or-exhausted network failures from invalid repository or repository access failures in the resulting failure category

#### Scenario: Imported readiness remains reusable after analysis
- **WHEN** a live analysis run completes and later dashboard or search surfaces load that imported workspace
- **THEN** the system SHALL provide the same imported readiness guidance rather than leaving each surface to infer its own next-step interpretation

#### Scenario: Private repository import requires access source context
- **WHEN** a live analysis request targets a private repository
- **THEN** the platform model SHALL require that the request resolve through an owner-authorized repository access source rather than assuming anonymous global import access

#### Scenario: Public repository import can still use bounded anonymous access
- **WHEN** a live analysis request targets a public repository and no owner-scoped credential source is required
- **THEN** the platform model SHALL still allow that request to resolve through a public-access source without collapsing workspace ownership into a global shared object

#### Scenario: Installation-backed repository reports reusable import context
- **WHEN** a live analysis request targets a repository that is already bound to a GitHub App-backed imported workspace in the current owner scope
- **THEN** the product-facing outcome SHALL report that installation-backed reuse state instead of implying only a fresh manual import path exists

#### Scenario: Private repository without authorized source reports credential-required outcome
- **WHEN** a live analysis request targets a private repository that the current owner scope cannot reach through any authorized access source
- **THEN** the product-facing outcome SHALL report that credential setup is required instead of implying a generic repository failure

#### Scenario: Private repository with invalid source reports authorization failure
- **WHEN** a live analysis request targets a private repository through an expired, revoked, or otherwise invalid owner-scoped source
- **THEN** the product-facing outcome SHALL report an authorization-specific failure class rather than collapsing the result into a generic network error

#### Scenario: Live analysis is resolved inside the authenticated owner's scope
- **WHEN** an authenticated actor starts live analysis
- **THEN** the repository lookup and resulting reuse/import actions SHALL be resolved inside that actor's current owner scope rather than through a global anonymous context
