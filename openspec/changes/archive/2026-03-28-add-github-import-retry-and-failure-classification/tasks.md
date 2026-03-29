## 1. GitHub Transport Retry

- [x] 1.1 Add bounded retry behavior inside `GitHubClient` for transient transport errors such as TLS EOF, connect failures, read failures, and short read timeouts.
- [x] 1.2 Ensure non-retryable repository errors such as malformed repo input and repository access failures still fail fast.

## 2. Failure Classification

- [x] 2.1 Extend import failure classification to distinguish at least `network_failure`, `invalid_repository`, `repository_access_failure`, `provider_failure`, and generic analysis execution failure.
- [x] 2.2 Preserve those classifications in import job summaries so the UI can explain whether retrying is likely to help.

## 3. Validation

- [x] 3.1 Add engine tests for retry success and retry exhaustion on GitHub transport failures.
- [x] 3.2 Add regression coverage for repository-origin failures that should not retry.
- [x] 3.3 Run the affected engine and API test suites after retry and failure-classification changes land.
