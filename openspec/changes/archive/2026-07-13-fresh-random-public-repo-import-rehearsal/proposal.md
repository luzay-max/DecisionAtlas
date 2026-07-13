## Why

Current real-repository evidence can reuse previously imported workspaces, so it proves downstream review/why/drift behavior but does not prove that a newly selected public GitHub repository can complete a fresh import and full product loop. A bounded clean-import rehearsal is needed now to distinguish real end-to-end readiness from reuse-only evidence.

## What Changes

- Add a fresh public-repository rehearsal that selects an eligible repository not already present in the current owner scope.
- Require preflight evidence proving the selected repository has no reusable workspace before import starts.
- Run the normal public GitHub import path, wait for bounded completion, and preserve repository, workspace, job, and outcome evidence.
- Feed a successful fresh workspace into review, accepted-baseline, Why Search, Drift, guardrail, browser, and release-evidence validation.
- Emit JSON and Markdown with explicit `fresh_import`, `reused`, `operator_guided`, `warning`, or `blocking` outcomes and honest limitations.
- Keep credentials, raw private source, and unbounded provider logs out of durable evidence.

## Capabilities

### New Capabilities

- `fresh-public-repo-import-rehearsal`: Defines random eligible repository selection, no-reuse preflight proof, fresh import completion, downstream core-loop validation, and bounded evidence.

### Modified Capabilities

- `live-repository-analysis`: Public imports validate an optional global GitHub token and retry anonymously only for public-access 401/403 responses; explicit owner-scoped private and installation access remain unchanged.
- github-import-retry: Transient GitHub 502/503/504 responses receive the same bounded retry treatment as transport interruptions.
- `readiness-evidence-history`: Fresh public-repository import rehearsal JSON/Markdown becomes a first-class durable evidence family with index and trend visibility.

## Impact

- Adds CI/operator automation under `scripts/ci/` and focused pytest coverage under `services/engine/tests/ci/`.
- Reuses existing public GitHub import, repository lookup, imported-workspace core-loop, accepted-baseline, full-chain, readiness-history, and browser surfaces without changing public APIs.
- Produces temporary and durable readiness evidence plus project log/taskbook updates.
- Depends on a running real local stack and GitHub availability for live rehearsal; those external conditions remain explicitly classified rather than hidden.
