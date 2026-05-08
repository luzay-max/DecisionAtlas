## 1. Existing Operator Flow Review

- [x] 1.1 Review hosted operator guide, hosted preview readiness docs, release checklist, release evidence command, health/smoke scripts, reset/reseed scripts, and seeded demo readiness checks.
- [x] 1.2 Define the hosted readiness lane model and classify lanes as required public walkthrough, recovery, advisory governance, optional imported proof, release evidence, or known limitation.
- [x] 1.3 Confirm the command location, default output paths, and supported explicit input paths/statuses for hosted readiness artifacts.

## 2. Hosted Readiness Model

- [x] 2.1 Add a small hosted readiness data model with schema version, generation metadata, lane classifications, blockers, warnings, missing inputs, recommended next actions, and source paths.
- [x] 2.2 Implement normalization for `pass`, `blocking`, `non_blocking`, `known_limitation`, `operator_guided`, `not_provided`, and `warning` statuses.
- [x] 2.3 Implement stop/go calculation so core hosted service or seeded public walkthrough blockers stop the external public walkthrough.
- [x] 2.4 Ensure optional governance, imported, private access, benchmark, and release evidence lanes remain separate from stable public walkthrough readiness.

## 3. Collector CLI

- [x] 3.1 Implement a local hosted readiness command under `scripts/demo/` or `scripts/ci/`.
- [x] 3.2 Add explicit CLI options for hosted URLs, health/smoke status or report paths, seeded readiness status or report path, recovery drill status, guardrail report path, release evidence path, and real-repo benchmark evidence path.
- [x] 3.3 Handle missing hosted URLs and optional reports as operator-guided, known-limitation, or not-provided evidence rather than clean pass.
- [x] 3.4 Validate invalid provided report paths with clear warnings and non-clean lane classification.
- [x] 3.5 Keep readiness generation local and non-mutating: no reset, reseed, import, live benchmark, tag, push, publish, or archive actions by default.

## 4. Output Generation

- [x] 4.1 Write hosted readiness output as machine-readable JSON.
- [x] 4.2 Generate an operator-readable Markdown handoff that mirrors JSON lane status, blockers, limitations, warnings, missing inputs, recommended next actions, and source paths.
- [x] 4.3 Include rerun commands and recovery scope notes in the Markdown handoff.
- [x] 4.4 Ensure output explicitly states that hosted readiness does not replace the canonical release gate.

## 5. Documentation

- [x] 5.1 Update hosted demo operator guide with the hosted readiness command, stop/go rules, and recovery evidence requirements.
- [x] 5.2 Update hosted preview readiness docs with the readiness artifact workflow and interpretation guidance.
- [x] 5.3 Add examples for normal external preview preparation and local rehearsal when hosted URLs are unavailable.
- [x] 5.4 Document that default reset/reseed remains scoped to `demo-workspace` and does not delete imported workspaces or governance history.

## 6. Tests and Validation

- [x] 6.1 Add unit tests for hosted readiness status normalization and stop/go calculation.
- [x] 6.2 Add tests for missing hosted URL handling, missing optional report handling, and invalid provided report paths.
- [x] 6.3 Add tests that Markdown output discloses blockers, known limitations, operator-guided lanes, recovery scope, and release gate separation.
- [x] 6.4 Run targeted hosted readiness tests.
- [x] 6.5 Run relevant release evidence and seeded demo readiness tests affected by this change.
- [x] 6.6 Run `openspec validate hosted-operator-delivery-readiness --type change --strict`.
