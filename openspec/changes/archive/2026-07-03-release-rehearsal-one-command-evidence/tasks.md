## 1. Release Rehearsal Collector

- [x] 1.1 Add a one-command release rehearsal script with JSON and Markdown outputs.
- [x] 1.2 Support consuming existing release, hosted/readiness, benchmark trend, multi-repo diagnosis, and guardrail evidence files.
- [x] 1.3 Support opt-in live multi-repo diagnosis while keeping missing optional lanes non-fatal.
- [x] 1.4 Preserve pass/warning/blocking aggregation and recommended follow-up.

## 2. Documentation And Specs

- [x] 2.1 Document the release rehearsal command and evidence boundary.
- [x] 2.2 Update the completion taskbook and 2026-07-03 update log.
- [x] 2.3 Sync OpenSpec main specs with the new requirements.

## 3. Validation

- [x] 3.1 Add targeted tests for missing inputs, warning/blocking aggregation, Markdown output, and live-diagnosis invocation plumbing.
- [x] 3.2 Run targeted Python tests.
- [x] 3.3 Run a smoke release rehearsal using current `.tmp` or operator-guided inputs.
- [x] 3.4 Run OpenSpec strict validation for the change and all specs.
