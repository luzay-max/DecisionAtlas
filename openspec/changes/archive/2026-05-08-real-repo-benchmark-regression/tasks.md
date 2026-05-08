## 1. History Snapshot Shape

- [x] 1.1 Inspect existing live real-repo JSON and Markdown report fields in `scripts/ci/run_benchmark.py`.
- [x] 1.2 Define a compact benchmark history snapshot schema with schema version, generated date, repository rows, key metrics, why/drift summaries, limitation categories, follow-up categories, and operational error type.
- [x] 1.3 Implement snapshot extraction from an existing live real-repo validation report without preserving raw generated answer prose or local-only `.tmp` paths.
- [x] 1.4 Add deterministic validation for snapshot shape and required bounded fields.

## 2. Comparison Logic

- [x] 2.1 Add comparison helpers that match current and baseline rows by repository id.
- [x] 2.2 Classify row movement as improved, unchanged, regressed, product-limited, operationally-blocked, newly-evaluated, missing-from-current, or needs-review.
- [x] 2.3 Keep missing workspaces, API failures, provider failures, auth/session failures, and GitHub/network failures separate from product-value regressions.
- [x] 2.4 Compute trend-relevant metric deltas for candidates, accepted decisions, strong candidates, thin ratio, why-case pass count, drift-case pass count, limitation categories, and follow-up categories.
- [x] 2.5 Produce an overall comparison summary with counts for improved, unchanged, regressed, operationally blocked, new, and missing rows.

## 3. CLI And Reports

- [x] 3.1 Add explicit CLI options for writing a compact snapshot from a live report.
- [x] 3.2 Add explicit CLI options for comparing a current report or snapshot against a baseline snapshot.
- [x] 3.3 Write machine-readable comparison JSON with repository movements, metric deltas, summary counts, and release-evidence-ready fields.
- [x] 3.4 Write operator-readable Markdown comparison output that mirrors the JSON summary and lists repository-level reasons.
- [x] 3.5 Ensure default benchmark and canonical pre-release behavior remain offline and do not require live providers or imported workspaces.

## 4. Tests And Fixtures

- [x] 4.1 Add benchmark unit tests for snapshot extraction and snapshot validation.
- [x] 4.2 Add benchmark unit tests for improved, unchanged, regressed, operationally-blocked, newly-evaluated, and missing-from-current comparison classifications.
- [x] 4.3 Add benchmark unit tests for metric deltas and summary counts.
- [x] 4.4 Add Markdown comparison report tests.
- [x] 4.5 Add or update a small sanitized fixture snapshot if needed for deterministic regression tests.

## 5. Documentation And Validation

- [x] 5.1 Update real-repository validation docs with the operator workflow for writing snapshots and comparing current benchmark results against a baseline.
- [x] 5.2 Document how to interpret product regressions versus operational blockers.
- [x] 5.3 Document that this change prepares release evidence input but does not yet automate release evidence aggregation.
- [x] 5.4 Run targeted benchmark/eval tests.
- [x] 5.5 Run offline benchmark validation.
- [x] 5.6 Run `openspec validate --all --strict`.
- [x] 5.7 Run `python scripts/governance/agent_guardrail.py --protocol-status --summary` and record any caution or pause evidence in the implementation handoff.
