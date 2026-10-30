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


## Stage A / A01 independent security review (2026-10-30)

**Fixed baseline:** `main@8aa461f5`. **Existing implementation PR:** #26 (Draft; base main), no parallel duplicate feature PR. The existing [CI #268](https://github.com/luzay-max/DecisionAtlas/actions/runs/40988302629) passed at `782de863` before this review amendment, but that CI is historical.

| Review control | Evidence and result | Remaining limit |
| --- | --- | --- |
| API credential isolation | HTTPX mock tests verify authenticated GitHub Contents API raw-media fallback, public raw download `Authorization`/`Cookie` removal and override of client-level auth. | Does not prove behavior against a real private GitHub repository. |
| Redirects and untrusted origin | Existing tests refuse API or public-raw redirect and untrusted host before outbound GET. | Provider-controlled Contents JSON is treated as untrusted source metadata. |
| **NEW: exact source file identity** | The raw download URL must identify the exact requested repo **and** file path. Previously only the repo prefix was verified, allowing a misleading URL within the same repository to be indexed as another file. | Ref/branch is not pinned; SHA capture and source snapshot strategy require separate review (#35/F06b). |
| **NEW: percent-encoded path evasion** | Reject decoded traversal, encoded slashes/backslashes, nested percent escapes and empty path components; allow ordinary percent-encoded spaces in file names. Mock HTTPX tests assert rejected URL does not issue public cross-origin request. | Unusual filenames containing literal percent signs fail closed in this rare fallback, rather than silently misidentifying evidence. |
| Import transaction | Existing `test_run_github_import_rolls_back_partial_artifacts_on_failure` flushes an Artifact, invokes progress, forces import failure and asserts no committed Artifact remains. | Import-phase progress is not externally durable until success. `on_progress` still contains a pause-wait loop while Artifacts may hold SQLite's writer lock: **NOT solved by #26**; the additional safety checkpoints in Draft #35 require separate review. |
| Validation | Offline mocked HTTPX + file-backed SQLite and current-head full CI are required. No live token, private repo, or paid LLM authorization granted. | Maintainership review and explicit merge authorization still outstanding. |

**A01 conclusion:** Security follow-up submitted to existing Draft #26. Mark **review in progress**, not `Done` or merged. A02's integration/rebase depends on explicit A01 approval and #26 entering `main`; leave #35, #30 and #31 untouched until then.
