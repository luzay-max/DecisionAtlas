## Purpose
Define live repository analysis behavior and honest progress reporting.
## Requirements
### Requirement: Live analysis reports honest outcomes
The system SHALL distinguish successful analysis, insufficient evidence, operational failure, imported-workspace readiness, existing-workspace reuse state, clearer import failure classes, owner-aware repository access context, and product-managed private access setup so users can interpret live-analysis results correctly and know the strongest next action, SHALL expose imported-workspace readiness in a form that product surfaces can reuse consistently after the import completes, and SHALL let admin users bind a repository to a GitHub App installation-backed or token-backed access source before reuse or import.

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

#### Scenario: Admin binds installation before import action
- **WHEN** an admin has a repository and GitHub App installation id for the current owner scope
- **THEN** the live-analysis product surface SHALL allow that repository to be bound to the installation-backed access source before open, sync, or import actions continue

#### Scenario: Token-backed repository reports reusable import context
- **WHEN** a live analysis request targets a repository that is already bound to a token-backed private access source in the current owner scope
- **THEN** the product-facing outcome SHALL report that private access-source label and authorization status instead of implying only a fresh public import path exists

#### Scenario: Admin binds private access before import action
- **WHEN** an admin has a repository and token for the current owner scope
- **THEN** the live-analysis product surface SHALL allow that repository to be bound to the token-backed private access source before open, sync, or import actions continue

#### Scenario: Private repository without authorized source reports credential-required outcome
- **WHEN** a live analysis request targets a private repository that the current owner scope cannot reach through any authorized access source
- **THEN** the product-facing outcome SHALL report that credential setup is required instead of implying a generic repository failure

#### Scenario: Private repository with invalid source reports authorization failure
- **WHEN** a live analysis request targets a private repository through an expired, revoked, or otherwise invalid owner-scoped source
- **THEN** the product-facing outcome SHALL report an authorization-specific failure class rather than collapsing the result into a generic network error

#### Scenario: Live analysis is resolved inside the authenticated owner's scope
- **WHEN** an authenticated actor starts live analysis
- **THEN** the repository lookup and resulting reuse/import actions SHALL be resolved inside that actor's current owner scope rather than through a global anonymous context

### Requirement: Live analysis reports actionable private access outcomes
The live-analysis flow SHALL report private repository access outcomes in terms that identify the next useful action.

#### Scenario: Credential setup is required before import
- **WHEN** live analysis targets a private repository that has no usable owner-scoped access source
- **THEN** the outcome SHALL state that private access setup is required before import can proceed

#### Scenario: Existing token-backed source is unauthorized
- **WHEN** live analysis targets a repository bound to a token-backed access source that GitHub rejects
- **THEN** the outcome SHALL identify the access source as unauthorized, expired, revoked, or insufficiently permitted when that can be determined safely

#### Scenario: Repository-not-found is not treated as credential setup
- **WHEN** live analysis cannot find the repository using the selected access source
- **THEN** the outcome SHALL distinguish repository-not-found from credential-required setup

#### Scenario: Network failure is not treated as credential setup
- **WHEN** live analysis fails because GitHub or the network is unavailable
- **THEN** the outcome SHALL distinguish provider or network failure from missing or unauthorized credentials

### Requirement: Live analysis entry presents reuse choices before repeat import
The live-analysis entry flow SHALL present existing workspace reuse choices before starting another import when repository lookup finds a workspace in the current owner scope.

#### Scenario: Form submit finds existing workspace
- **WHEN** the user enters a repository that already maps to an imported workspace in the current owner scope
- **THEN** the live-analysis form SHALL present open-existing, incremental-sync, and full-rerun choices instead of silently starting a new full import

#### Scenario: Incremental sync starts from existing workspace
- **WHEN** the user chooses incremental sync for an existing workspace with no active import
- **THEN** the live-analysis flow SHALL start a `since_last_sync` import for that workspace and route the user to the workspace progress surface

#### Scenario: Full rerun remains intentional
- **WHEN** the user chooses full re-analysis for an existing workspace
- **THEN** the live-analysis flow SHALL label the action as a full rerun and route progress to the existing workspace rather than creating an ambiguous duplicate destination

#### Scenario: Active import changes available actions
- **WHEN** repository lookup reports a queued or running import for the existing workspace
- **THEN** the live-analysis flow SHALL guide the user to the active workspace/job and SHALL NOT present duplicate repeat-run actions as normal primary actions

### Requirement: Live analysis repeat-run copy is access-source aware
The live-analysis entry flow SHALL preserve public, GitHub App-backed, and token-backed private access context when presenting repeat-run actions.

#### Scenario: Installation-backed workspace labels sync source
- **WHEN** lookup finds an installation-backed imported workspace
- **THEN** live-analysis repeat-run copy SHALL identify the GitHub App-backed access source before offering sync or rerun actions

#### Scenario: Token-backed workspace labels private source
- **WHEN** lookup finds a token-backed private imported workspace
- **THEN** live-analysis repeat-run copy SHALL identify the private access-source status without exposing credential material

#### Scenario: Missing private access does not become repeat-run
- **WHEN** lookup determines that private access setup is required before import can proceed
- **THEN** the live-analysis entry flow SHALL show setup guidance rather than presenting open/sync/rerun actions for a workspace it cannot access

### Requirement: Public GitHub rehearsal imports or reuses workspace before benchmark
The live repository analysis flow SHALL provide an operator-guided rehearsal path that imports or reuses the expected workspace for a selected public GitHub repository before benchmark validation claims repository-level evidence.

#### Scenario: Public repository workspace is missing before rehearsal
- **WHEN** the operator starts the public GitHub rehearsal for a curated repository whose workspace does not exist in the current owner scope
- **THEN** the rehearsal SHALL attempt the normal public import path and report whether the workspace was created, remained missing, or failed for a bounded provider or local-stack reason

#### Scenario: Public repository workspace already exists
- **WHEN** the operator starts the public GitHub rehearsal for a curated repository whose workspace already exists in the current owner scope
- **THEN** the rehearsal SHALL reuse the existing workspace and report reuse instead of creating an ambiguous duplicate import

#### Scenario: Rehearsal cannot reach GitHub or local services
- **WHEN** the public GitHub rehearsal cannot reach GitHub, the API, or the engine
- **THEN** the rehearsal SHALL classify the lane as operator-guided or provider/local-stack failure rather than claiming repository analysis success
