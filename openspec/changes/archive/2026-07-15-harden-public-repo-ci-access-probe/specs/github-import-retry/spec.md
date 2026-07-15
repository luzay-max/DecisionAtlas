## MODIFIED Requirements

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
