## Context

The current release baseline protects the offline path: unit tests, typechecks, engine pytest, fixture validation, and Playwright smoke coverage. Real-repository validation exists as curated fixtures plus an optional `--live-real-repos` mode, but live mode currently focuses on why cases and does not produce a full repo-level readiness report.

The product has recently gained clearer imported readiness states, first-accepted-baseline semantics, stronger candidate conversion, and chunk-backed why support. Those improvements need to be exercised against real imported workspaces without making live providers, GitHub, or local workspace state part of the default release gate.

## Goals / Non-Goals

**Goals:**

- Make live real-repo validation repeatable for the curated repository set.
- Collect observed readiness, candidate, accepted baseline, why, and drift outcomes in one operator-readable report.
- Keep default offline fixture validation stable and provider-independent.
- Preserve broad-state assertions instead of exact answer text.
- Make failures actionable by distinguishing repository-signal limitations from operational failures.

**Non-Goals:**

- Do not make live real-repo validation mandatory in CI or `pre-release.ps1`.
- Do not require every curated repository to produce demo-quality answers.
- Do not add new connectors, auth UI, hosted demo infrastructure, or private repo productization.
- Do not rewrite extraction, retrieval, or drift algorithms unless the validation work reveals a small release-blocking bug in the reporting path.

## Decisions

### 1. Treat live validation as report-producing, not gate-owning

`scripts/ci/run_benchmark.py --live-real-repos` should remain operator-triggered. It can fail when expected broad outcomes are violated, but it should not be wired into default pre-release validation.

Alternative considered: add live validation to `pre-release.ps1`. Rejected because provider/network/local-workspace state would make the release gate flaky and non-reproducible.

### 2. Validate existing imported workspaces before owning fresh imports

The first implementation should query the local API for existing curated workspace slugs and report their state. It may identify missing workspaces as an explicit `missing_workspace` or operational outcome, but it should not automatically run long full imports unless a later task explicitly adds that mode.

Alternative considered: make the benchmark script import every curated repo end-to-end. Rejected for this slice because it would conflate import duration, provider reliability, GitHub limits, and product-readiness validation.

### 3. Use structured report rows

Each repository row should include at least:

- repo id, repo name, workspace slug
- observed workspace/readiness state
- candidate decision count
- accepted decision count
- screened-in artifact count when available
- why case status when cases exist
- drift case or drift-state status when cases exist
- bounded outcome and notes

The report can be JSON first, with Markdown documentation or a checked-in summary added when useful.

### 4. Reuse product readiness contracts

The script should prefer backend/API readiness fields over duplicating UI heuristics. Dashboard and search readiness behavior must remain comparable because live validation is meant to expose product outcomes, not only raw database counts.

Alternative considered: compute readiness entirely in the script from raw decisions/artifacts. Rejected because it would create another source of truth and hide product-readiness regressions.

### 5. Keep assertions broad and explainable

Validation should compare observed outcomes against expected state families from `examples/live-benchmarks/`. It should assert status families, minimum counts, citation floors, and forbidden drift outcomes. It should not assert exact answer prose or exact alert titles beyond configured patterns.

## Risks / Trade-offs

- Live data may be absent locally -> report `missing_workspace` clearly and keep offline fixture validation unaffected.
- Provider/network failures may interrupt why checks -> record operational failure separately from evidence-limited product outcomes.
- Repo state can evolve upstream -> keep expected outcomes broad and avoid exact prose assertions.
- Report generation may tempt teams to treat live validation as a release blocker -> docs must keep it as an optional confidence layer.
- Duplicate readiness logic could drift from the product -> prefer API readiness payloads and add only thin interpretation code in the benchmark script.

## Migration Plan

1. Extend fixtures only where needed to describe report expectations and allowed live outcomes.
2. Extend live benchmark mode to collect repo-level readiness and write a report.
3. Add targeted tests for report generation and fixture validation.
4. Update `docs/project/real-repository-validation-baseline.md` with the live validation workflow and report interpretation.
5. Run offline benchmark validation, then optionally run live validation against available local imported workspaces.

Rollback is straightforward: keep fixture validation and remove or disable the new live report mode without changing the default release gate.

## Open Questions

- Should the first report be checked into `docs/project/` as a dated Markdown snapshot, or generated into `.tmp/` by default with an option to save?
- Should live validation eventually support an explicit `--run-imports` mode, or should import execution stay a separate operator step?
