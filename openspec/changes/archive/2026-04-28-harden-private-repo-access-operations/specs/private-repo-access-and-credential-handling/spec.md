## ADDED Requirements

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
