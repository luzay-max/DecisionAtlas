## Context

Existing release-related collectors are useful but fragmented:

- `collect_release_evidence.py` summarizes core release readiness.
- `collect_readiness_evidence_history.py` archives dated/versioned evidence.
- `collect_real_repo_benchmark_trend.py` summarizes benchmark trend evidence.
- `collect_multi_repo_live_diagnosis.py` diagnoses real public repository setup/core-loop status.
- External install, hosted readiness, handoff, and audit collectors already produce JSON/Markdown evidence in their own lanes.

The product now needs an operator-facing entry point that can run a release rehearsal consistently before handoff or customer delivery.

## Goals / Non-Goals

**Goals:**

- Provide one Python CLI that can orchestrate the release evidence bundle.
- Reuse existing collectors and input files rather than duplicating evidence logic.
- Produce compact JSON and Markdown suitable for release handoff.
- Allow optional inputs; missing evidence becomes `not_provided` or `operator_guided`, not a crash.
- Exit non-zero only when a blocking status is produced.

**Non-Goals:**

- Do not add new product APIs.
- Do not run expensive browser tests by default.
- Do not require private repo credentials or model provider tokens.
- Do not replace individual lane collectors.

## Decisions

1. Use a lightweight Python orchestrator.
   - Rationale: existing evidence collectors are Python CLIs and are already testable.
   - Alternative: shell script. Rejected because structured status aggregation is easier in Python.

2. Prefer consuming existing evidence files, with opt-in live collection flags.
   - Rationale: release rehearsals should be repeatable and fast, while still allowing fresh diagnosis when desired.

3. Preserve mixed outcomes in the top-level bundle.
   - Rationale: a release with missing benchmark or guardrail evidence should be visible as warning, not hidden.

## Status Model

- `pass`: all provided lanes are clean enough.
- `warning`: at least one lane is missing, operator-guided, or non-clean but not blocking.
- `blocking`: at least one lane reports a local stack, provider, command, or explicit blocking failure.

## Risks / Trade-offs

- Running all live collectors can be slow. Mitigation: make live lanes opt-in and support input JSON paths.
- Evidence schemas may evolve. Mitigation: aggregate only stable top-level fields: status, summary, file path, and recommended follow-up.
- Operators may misread warning as failure. Mitigation: Markdown explains warning and next actions.
