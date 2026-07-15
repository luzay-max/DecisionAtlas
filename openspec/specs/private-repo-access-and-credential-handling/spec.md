## Purpose
Define owner-scoped private repository access and credential handling requirements.
## Requirements
### Requirement: Owner-scoped access sources can authorize private repository import
The system SHALL require private repository import to resolve through an owner-scoped authorized access source instead of assuming anonymous global access.

#### Scenario: Authorized source allows private repository import
- **WHEN** the current owner scope has an authorized access source that can reach a target private repository
- **THEN** the platform SHALL allow import of that repository within the current owner scope

#### Scenario: Missing source blocks private repository import
- **WHEN** the current owner scope has no authorized access source for a target private repository
- **THEN** the platform SHALL block import and report that private-repository access setup is required

### Requirement: Credential-bearing access sources are referenced separately from workspaces
The system SHALL store private-repository access through reusable owner-scoped access-source records and SHALL bind workspaces to those records without storing raw credential material on the workspace.

#### Scenario: Workspace binds to access-source reference
- **WHEN** a private repository import succeeds
- **THEN** the resulting workspace SHALL record which owner-scoped access source it is bound to

#### Scenario: Credential rotation does not redefine workspace identity
- **WHEN** the credential material behind an access source is rotated or refreshed
- **THEN** the platform SHALL preserve workspace identity while updating the bound source state

### Requirement: Private repository failures are reported as authorization outcomes
The system SHALL distinguish private-repository authorization failures from generic repository-not-found, rate-limit, provider, or network failures and SHALL NOT request credentials solely because repository metadata was temporarily unavailable.

#### Scenario: Unauthorized source yields explicit failure class
- **WHEN** the current owner scope attempts to import a private repository through an invalid or unauthorized source
- **THEN** the platform SHALL report an authorization-specific failure outcome rather than collapsing it into a generic repository failure

#### Scenario: Credential-required outcome is exposed before blind import
- **WHEN** live analysis targets a private repository with no authorized source in the current owner scope and anonymous public reachability cannot be verified
- **THEN** the platform SHALL return a credential-required outcome before starting a blind import job

#### Scenario: Public repository survives metadata rate limit
- **WHEN** metadata lookup is rate-limited or transiently forbidden but a bounded anonymous probe verifies public reachability
- **THEN** the platform SHALL continue the public import and SHALL NOT report credential-required

#### Scenario: Indeterminate provider failure stays operational
- **WHEN** neither metadata nor the bounded public probe can determine access because of provider or network failure
- **THEN** the platform SHALL return provider or network failure rather than instructing the user to configure private credentials

### Requirement: Product-managed private access sources avoid raw credential exposure
The system SHALL allow product-managed private repository access setup while keeping raw credential material out of workspace records and product result surfaces.

#### Scenario: Private access source is created from product setup
- **WHEN** an admin submits private repository access credentials through the product
- **THEN** the platform SHALL create or update the owner-scoped access-source record and bind the workspace to that source without storing raw credential material on the workspace

#### Scenario: Product result omits submitted credential
- **WHEN** private access setup returns a workspace or access-source result
- **THEN** the result SHALL include source label and authorization state but SHALL NOT include the submitted token value

#### Scenario: Rebinding preserves source status semantics
- **WHEN** an admin rebinds a repository to an existing token-backed source reference
- **THEN** the platform SHALL preserve the access-source status model so workspace surfaces can still report authorized, missing, or unauthorized source state

### Requirement: Token-backed access failures have stable operational categories
The system SHALL classify token-backed private repository access failures into stable operational categories that callers can distinguish without parsing raw provider errors.

#### Scenario: Missing token-backed source is classified
- **WHEN** a private repository import or lookup requires a token-backed access source but none exists in the current owner scope
- **THEN** the system SHALL return a credential-required or missing-source outcome rather than starting a blind public import

#### Scenario: Unauthorized token-backed source is classified
- **WHEN** a bound token-backed access source is expired, revoked, lacks repository permission, or is otherwise rejected by GitHub
- **THEN** the system SHALL return an authorization-specific outcome and SHALL NOT collapse it into a generic network failure

#### Scenario: Repository absence remains distinguishable
- **WHEN** the repository cannot be found even with the selected access source
- **THEN** the system SHALL distinguish repository-not-found from missing credentials or revoked credentials

#### Scenario: Provider failure remains distinguishable
- **WHEN** GitHub or the network fails before authorization can be determined
- **THEN** the system SHALL report a provider or network failure outcome separately from credential-required and unauthorized outcomes

### Requirement: Token material remains write-only in product flows
The system SHALL treat private repository tokens as write-only credential material after submission.

#### Scenario: Binding response omits token material
- **WHEN** an admin submits a token-backed private access binding request
- **THEN** the response SHALL include bounded access-source identity and authorization state but SHALL NOT include the submitted token value

#### Scenario: Workspace summaries omit token material
- **WHEN** a workspace, lookup, readiness, or review-adjacent summary references a token-backed access source
- **THEN** the summary SHALL include access-source label and status without exposing raw credential material

#### Scenario: Failure detail is bounded
- **WHEN** a token-backed operation fails
- **THEN** the system SHALL expose only bounded operational detail suitable for users and operators rather than raw provider payloads or credential values
