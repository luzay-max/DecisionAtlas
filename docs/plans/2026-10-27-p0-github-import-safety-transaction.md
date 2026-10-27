# P0 — GitHub raw download credential isolation and import rollback

**Date:** 2026-10-27  
**Base:** main @ `465223b5a7dd75a885fc0391a62e09fc369f4a36` (after Phase E / PR #25)  
**Status:** Draft PR; CI #251 passed at `a62341c8` before follow-up raw-media hardening. New-head CI pending. Do not merge automatically.

## Scope
1. Restrict GitHub Contents API `download_url` fallback to HTTPS `raw.githubusercontent.com` paths belonging to the requested repository. Reject unexpected ports, credentials, fragments, query strings, malformed paths, untrusted hosts, and redirects.
2. Prefer authenticated same-origin GitHub Contents API `raw` media for non-base64 Markdown, including private repositories. Fail on same-origin API redirects; if a proxy ignores raw media, retain the allowlisted public raw URL fallback without Authorization/Cookie or client-level auth.
3. Prevent the import progress callback from committing the transaction before the importer has passed its Markdown integrity checks. A failure after progress notification must roll back the partially written Artifacts.
4. Add offline tests for private authenticated raw-media fallback, credential isolation, allowlist rejection, both redirect paths, and progress-before-failure rollback.

## Trade-off / operational note
- Import-phase progress is accumulated transactionally and becomes durable/visible at the import commit rather than being published in real time. Preserving incremental progress with strict atomicity requires a separate out-of-transaction telemetry channel, deferred to a later PR.
- This PR does not change the extraction-phase progress reporter, production API semantics, database schema, source review state, or model behavior.

## Acceptance criteria
- [x] First-head Windows CI #251 passed; raw download credential isolation and import rollback tests passed at `a62341c8`.
- [ ] Re-run mocked private raw-media and redirect tests on the updated head; only `api.github.com` may receive private credentials.
- [ ] Verify an untrusted public download URL or a redirect is refused without cross-host credential forwarding.
- [ ] Verify import failure after a progress callback leaves zero partial Artifacts.
- [ ] Full GitHub Actions CI passes on the **final** PR head.
- [ ] Diff reviewed before considering merge.

## Validation boundary
No local host, private data, live tokens, or paid model calls are required or used for these tests. Mocked/CI tests do **not** establish the later real public-import or external environment acceptance gate.
