## Context

The real-repository lane now supports workspace reuse, incremental sync, extraction, why-search, and drift. The remaining stability gap is earlier in the pipeline: a single transient GitHub transport failure can still fail an entire import during artifact collection. Existing failure categories are also too coarse, so users see generic analysis failure language even when the likely remedy is simply retrying after a network interruption.

## Goals / Non-Goals

**Goals:**
- Retry transient GitHub transport failures a small number of times before failing an import.
- Keep retry logic local to the GitHub client so callers do not duplicate transport policy.
- Introduce clearer import failure categories, including at least network-origin and repository-origin failures.
- Preserve deterministic failure behavior for non-retryable errors such as invalid repository input or 4xx repository access problems.

**Non-Goals:**
- Add import cancel/resume behavior.
- Continue partially imported runs after individual document failures.
- Add provider retry logic.
- Redesign the imported workspace dashboard beyond clearer failure classification.

## Decisions

### Retry at the GitHub client request boundary
Retry policy belongs in `GitHubClient` because that is where transport errors and HTTP responses are observed consistently. This keeps import orchestration simple and avoids scattering retry logic across importer call sites.

Alternative considered:
- Retry entire importer stages.
  Rejected because it is coarser, risks repeating more work than necessary, and makes failure accounting harder.

### Retry only transient transport failures
Only network-like failures should retry: TLS EOF, connect/read errors, and short read timeouts. Repository validation or access problems should fail immediately.

Alternative considered:
- Retry all non-200 responses.
  Rejected because 4xx repository errors are usually deterministic and retries only add delay.

### Classify failures for user actionability
Failure categories should map to likely operator actions:
- `network_failure`: retry later
- `invalid_repository`: fix repo input
- `repository_access_failure`: check existence/public access/rate limiting
- `provider_failure`: inspect model/provider path
- `analysis_execution_failed`: fallback for uncategorized failures

Alternative considered:
- Keep low-level categories like `ssl_failure` or `connect_failure` user-visible.
  Rejected for first pass because product guidance is stronger with fewer high-signal categories.

## Risks / Trade-offs

- **Retries can slightly slow deterministic failures** → Only retry transient transport failures and keep retry count low.
- **Some transport failures may still be non-transient** → Preserve final failure with clear `network_failure` classification after retry budget is exhausted.
- **Repository access failures can mix causes (404, 403, rate limit)** → Group them first under repository access semantics; finer distinctions can come later if needed.
- **No partial-import continuation means one persistent GitHub request failure still fails the job** → Accept this for now to keep scope focused on transport resilience, not job recovery architecture.
