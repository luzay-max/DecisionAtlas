## 1. Fresh Import Collector

- [x] 1.1 Add bounded candidate loading, seeded ordering, owner-scoped lookup, and reuse-ineligible classification.
- [x] 1.2 Require a no-workspace preflight and a terminal `created` import before reporting `fresh_import`.
- [x] 1.3 Compose the successful fresh import with existing imported-workspace core-loop evidence without automatic review acceptance.
- [x] 1.4 Emit bounded JSON and Markdown with selection, preflight, import, downstream, limitations, and next actions.
- [x] 1.5 Prevent public workspaces from inheriting stale optional global GitHub credentials.
- [x] 1.6 Retry transient GitHub 502/503/504 responses within the existing bounded request budget.
- [x] 1.7 Add fresh public-repository rehearsal as a first-class readiness-history evidence family.

## 2. Automated Tests

- [x] 2.1 Test deterministic seeded selection and skipping of reused candidates.
- [x] 2.2 Test exhausted candidate pools and lookup/provider/local-stack failure classification.
- [x] 2.3 Test successful fresh import composition, lookup race rejection, failed job, and timeout evidence.
- [x] 2.4 Test public, installation-backed, and owner-scoped token selection boundaries.
- [x] 2.5 Test transient server response recovery, retry exhaustion, and network classification.
- [x] 2.6 Run targeted pytest and `openspec validate --all --strict`.
- [x] 2.7 Test readiness-history summary, archive copying, index, trend, and non-clean-state preservation.

## 3. Real Public Repository Rehearsal

- [x] 3.1 Select a previously unused public GitHub repository and prove `workspace_exists=false` before import.
- [x] 3.2 Run the real full import to terminal state and collect fresh-import plus core-loop evidence.
- [x] 3.3 Use Browser, Chrome, and Computer interaction where available to validate import progress, review, Why Search, Drift, and workspace navigation as a human user.
- [x] 3.4 Generate full-chain, guardrail, warning-reduction, and readiness-history evidence without hiding non-pass lanes.

## 4. Records And Closure

- [x] 4.1 Add the real outcome, limitations, screenshots, and commands to the project update log and completion taskbook.
- [x] 4.2 Archive readiness evidence, archive the OpenSpec change, rerun strict validation, and commit only scoped files.
