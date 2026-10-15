## MODIFIED Requirements

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
