## ADDED Requirements

### Requirement: GitHub import retries transient transport failures
The system SHALL retry GitHub import requests a bounded number of times when the failure appears transient at the transport layer.

#### Scenario: TLS or transport interruption succeeds after retry
- **WHEN** a GitHub request fails with a transient transport error such as SSL EOF, connect failure, read failure, or short read timeout
- **THEN** the system SHALL retry that request before failing the import

#### Scenario: Transport retries are exhausted
- **WHEN** the same GitHub request continues to fail with transient transport errors after the configured retry budget is exhausted
- **THEN** the system SHALL fail the import and classify it as a network-origin failure

### Requirement: Non-retryable repository failures fail fast
The system SHALL avoid retrying repository-origin errors that are unlikely to succeed on a second attempt.

#### Scenario: Invalid repository input is not retried
- **WHEN** the repository input is malformed or unsupported
- **THEN** the system SHALL fail immediately without transport retry

#### Scenario: Repository access error is not retried blindly
- **WHEN** GitHub returns a repository access error such as not found or forbidden
- **THEN** the system SHALL fail the import without transport retry and classify the result as a repository-origin failure
