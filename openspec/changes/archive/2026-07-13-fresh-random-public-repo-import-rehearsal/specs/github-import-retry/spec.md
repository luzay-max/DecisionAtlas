## MODIFIED Requirements

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