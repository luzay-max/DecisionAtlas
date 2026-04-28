## ADDED Requirements

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
