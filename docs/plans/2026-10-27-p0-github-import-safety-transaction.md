# P0 — GitHub raw download credential isolation and import rollback

**Date:** 2026-10-27  
**Base:** main @ `465223b5a7dd75a885fc0391a62e09fc369f4a36` (after Phase E / PR #25)  
**Status:** Draft PR; offline CI validation pending. Do not merge automatically.

## Scope
1. Restrict GitHub Contents API `download_url` fallback to HTTPS `raw.githubusercontent.com` paths belonging to the requested repository. Reject unexpected ports, credentials, fragments, query strings, malformed paths, untrusted hosts, and redirects.
2. On fallback requests, remove inherited Authorization and Cookie headers and explicitly bypass any client-level auth while preserving HTTPX mocked-transport testability.
3. Prevent the import progress callback from committing the transaction before the importer has passed its Markdown integrity checks. A failure after progress notification must roll back the partially written Artifacts.
4. Add offline tests for credential isolation, allowlist rejection, redirect refusal, and progress-before-failure rollback.

## Trade-off / operational note
- Import-phase progress is accumulated transactionally and becomes durable/visible at the import commit rather than being published in real time. Preserving incremental progress with strict atomicity requires a separate out-of-transaction telemetry channel, deferred to a later PR.
- This PR does not change the extraction-phase progress reporter, production API semantics, database schema, source review state, or model behavior.

## Acceptance criteria
- [ ] New mocked HTTPX tests pass; raw download receives neither Authorization nor Cookie even when the injected client has both default headers and configured auth.
- [ ] An untrusted raw URL or redirect is refused before issuing any cross-host request.
- [ ] Import failure after a progress callback leaves zero partial Artifacts while the job correctly reports failure.
- [ ] Full GitHub Actions CI passes on the final PR head.
- [ ] Diff reviewed independently before considering merge.

## Validation boundary
No local host, private data, live tokens, or paid model calls are required or used for these tests. Mocked/CI tests do **not** establish the later real public-import or external environment acceptance gate.
