## Why

Real repository imports can still fail because of transient GitHub transport interruptions such as TLS EOF or short-lived read/connect failures. Those failures currently look too much like generic analysis failures, which makes the product feel brittle and gives users poor guidance about whether retrying is likely to help.

## What Changes

- Add bounded transport-level retry behavior for GitHub API requests that fail with transient network or TLS errors.
- Introduce clearer import failure categories so users can distinguish network-origin failures from invalid repository input, repository access failures, provider failures, and generic execution failures.
- Surface those classifications through existing import job summaries and imported workspace failure views.
- Keep the scope limited to request transport resilience and failure semantics, without adding partial-import continuation or resumable job execution.

## Capabilities

### New Capabilities
- `github-import-retry`: Covers bounded GitHub transport retries for transient import-time request failures.

### Modified Capabilities
- `live-repository-analysis`: Live analysis failure summaries need to distinguish network-origin failures from repository, provider, and generic analysis failures.

## Impact

- Engine GitHub client transport behavior
- Import job failure classification in engine
- Import failure messaging shown through dashboard/import status surfaces
- Engine and API tests for retry behavior and failure categories
