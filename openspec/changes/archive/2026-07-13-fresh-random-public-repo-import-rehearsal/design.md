## Context

DecisionAtlas already has a public GitHub import rehearsal, repository lookup, import-job polling, imported-workspace core-loop collector, accepted-baseline promotion, and release evidence aggregation. Existing multi-repository evidence intentionally treats a reusable workspace as valid setup, which is useful for regression testing but cannot prove that a repository selected today was freshly imported.

This change composes the existing paths into a stricter operator rehearsal. It must preserve the distinction between a fresh import and reuse, remain safe for public and private data boundaries, and report network/local-stack constraints honestly.

## Goals / Non-Goals

**Goals:**

- Select one repository from a bounded candidate pool using a recorded random seed.
- Query every considered repository before selection and require `workspace_exists=false` for the selected repository.
- Start only the existing full public GitHub import path and wait for a terminal job result.
- Feed a successful fresh workspace into the existing core-loop and browser validation paths.
- Produce customer-safe JSON and Markdown that prove selection, preflight, import, and downstream status.

**Non-Goals:**

- Deleting an existing workspace to manufacture a fresh result.
- Treating a full rerun of an existing workspace as a fresh import.
- Adding a second importer or changing the public import API.
- Storing GitHub tokens, private repository content, raw model output, or unbounded logs.
- Requiring every randomly considered repository to import successfully.

## Decisions

### Use a bounded candidate pool and recorded seed

The rehearsal accepts a JSON candidate list and optional repeated CLI repository values. It shuffles eligible candidates with a supplied or generated seed, records the ordered consideration list, and chooses the first repository whose owner-scoped lookup reports no workspace.

This is preferred to GitHub Search API discovery because it avoids a second unauthenticated rate-limited dependency and keeps runs reproducible. A direct single repository remains supported for operator-controlled external trials, but evidence records that selection mode separately.

### Enforce freshness before and after import

The collector performs `/imports/lookup?repo=...` for every considered candidate. Existing workspaces are skipped and recorded as `reused_not_eligible`. The selected repository is then passed through `rehearse_public_import`; only `setup.outcome=created` with a terminal `succeeded` job satisfies fresh-import evidence. A race that turns the second lookup into `reused` produces a warning and never a pass.

This is preferred to deleting database state because destructive cleanup would invalidate realistic owner-scoped behavior and could erase user data.

### Compose existing collectors in-process

After import succeeds, the new collector calls the existing imported-workspace core-loop report builder with the fresh import report as setup evidence. Accepted-baseline promotion remains an explicit follow-up when candidates exist; the collector does not silently accept decisions.

This keeps review governance intact and avoids duplicating dashboard, review, Why Search, Drift, and guardrail probing logic.

### Keep public access independent from optional global credentials

Public workspaces may use a configured global `GITHUB_TOKEN` for rate limits. The engine validates that client before artifact import and retries anonymously only when GitHub returns 401 or 403. Explicit token-backed private workspaces continue to use their owner-scoped token, and installation-backed access retains its configured path.

This prevents a stale global credential from turning a publicly reachable repository into a 401 import failure while still using a valid operator-provided token. Anonymous retry is restricted to public workspaces so private or installation authorization failures remain visible.

### Retry transient GitHub server responses

The existing GitHub request retry budget now covers 502, 503, and 504 responses in addition to connection/read interruptions. Each request retries at most the configured number of attempts with the same bounded backoff; 4xx repository and authorization responses still fail fast.

This prevents a single GitHub gateway interruption during document fetch from rolling back hundreds of already fetched artifacts while keeping invalid repository and permission errors explicit.

### Separate machine evidence from browser evidence

The collector writes bounded JSON and Markdown before browser validation. Browser/Chrome/Computer evidence is attached in the dated readiness entry and referenced by the project update log. The final release bundle must preserve any warning or operator-guided state instead of overriding it with a browser pass.

## Risks / Trade-offs

- [Candidate pool is exhausted because every repository already exists] -> Return `not_provided`/warning with every lookup outcome and require a new candidate pool; never delete workspaces.
- [GitHub or the local stack fails during import] -> Preserve provider/local-stack classification and the selected repository without claiming full-chain success.
- [Large repository import exceeds the bounded timeout] -> Preserve the job id and latest state so the operator can resume observation; do not start a duplicate import.
- [Fresh repository produces no useful decisions] -> Treat import as real but core-loop quality as evidence-limited; do not promote weak candidates automatically.
- [Randomness makes regressions hard to compare] -> Persist the seed, candidate pool digest, selected repository, and ordered consideration list.
- [Public global token is stale] -> Retry once with anonymous access only after 401/403; preserve explicit private and installation authorization failures.

## Migration Plan

1. Add the new collector and unit tests without changing existing CLI defaults.
2. Run it against the current real stack with a candidate pool containing repositories not used by existing readiness entries.
3. Complete browser validation and archive the evidence under a dated readiness-history entry.
4. Roll back by removing the new standalone collector and spec; no schema or persisted product data migration is required.

## Open Questions

- Whether a future release gate should require a fresh import on every release or only on scheduled/external rehearsals will be decided after several dated runs establish cost and reliability.
- Candidate-pool maintenance remains operator-owned until real customer trials show that GitHub Search API discovery is worth the additional dependency.
