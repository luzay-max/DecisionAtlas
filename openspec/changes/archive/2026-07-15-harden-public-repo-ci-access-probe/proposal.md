## Why

GitHub Actions proved that a public repository can be misclassified as private when the shared runner hits GitHub API rate limits or transient provider responses. The import preflight must verify public reachability through a bounded non-API probe before asking for private credentials.

## What Changes

- Add a bounded Git smart-HTTP public reachability probe when repository metadata lookup fails.
- Keep 404/private outcomes distinct from API rate-limit, provider, and network failures.
- Allow verified public repositories to continue when the metadata API alone is unavailable.
- Add deterministic tests for public fallback, private rejection, and provider failure classification.
- Re-run the failed Playwright real-repository workflow and GitHub Actions.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- github-import-retry: Transient or rate-limited metadata preflight can use a bounded public repository fallback instead of failing as a repository-origin error.
- private-repo-access-and-credential-handling: Credential-required outcomes are returned only after public reachability cannot be verified, while provider failures remain separate.

## Impact

- GitHub client public reachability probing.
- Import-job repository preflight and failure classification.
- GitHub client/import job tests.
- GitHub Actions imported workspace browser smoke reliability.
