## Purpose
Define retry behavior for transient GitHub import failures.
## Requirements
### Requirement: GitHub import retries transient transport failures
The system SHALL retry GitHub import requests a bounded number of times when the failure appears transient at the transport layer or as a GitHub gateway/service response.

#### Scenario: TLS or transport interruption succeeds after retry
- **WHEN** a GitHub request fails with a transient transport error such as SSL EOF, connect failure, read failure, or short read timeout
- **THEN** the system SHALL retry that request before failing the import.

#### Scenario: Transient GitHub server response succeeds after retry
- **WHEN** GitHub returns 502, 503, or 504 within the configured retry budget
- **THEN** the system SHALL retry that request with bounded backoff before failing the import.

#### Scenario: Transport or server retries are exhausted
- **WHEN** the same GitHub request continues to fail with transient transport errors or 502/503/504 responses after the configured retry budget is exhausted
- **THEN** the system SHALL fail the import and classify it as a network-origin failure.

### Requirement: Non-retryable repository failures fail fast
The system SHALL avoid blindly retrying repository-origin errors that are unlikely to succeed, while allowing a bounded anonymous public-reachability probe when metadata access alone cannot determine whether a repository is public.

#### Scenario: Invalid repository input is not retried
- **WHEN** the repository input is malformed or unsupported
- **THEN** the system SHALL fail immediately without transport retry

#### Scenario: Definitive repository access error fails fast
- **WHEN** GitHub metadata and a bounded anonymous public probe cannot reach a repository and the provider response is a definitive not-found or authorization outcome
- **THEN** the system SHALL fail the import without blind transport retry and classify the result as a repository-origin failure

#### Scenario: Rate-limited metadata falls back to public probe
- **WHEN** repository metadata returns a rate-limit, forbidden, or transient provider response for a public access source
- **THEN** the system SHALL perform a bounded anonymous public-reachability probe before classifying the repository as private or credential-required

#### Scenario: Public probe verifies repository
- **WHEN** the anonymous public probe verifies Git smart-HTTP reachability
- **THEN** preflight SHALL allow public import to continue without requesting private credentials
