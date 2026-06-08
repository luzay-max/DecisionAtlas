## 1. Package Builder

- [x] 1.1 Add a deterministic self-hosted package builder script.
- [x] 1.2 Generate package manifest JSON with identity, commit, included docs, scripts, services, URLs, commands, and support boundaries.
- [x] 1.3 Generate package README and copy only allowlisted docs, scripts, and templates.
- [x] 1.4 Ensure package builder excludes secrets, `.env`, `.tmp`, databases, logs, dependency directories, and local scratch state.

## 2. Package Verifier

- [x] 2.1 Add an offline package verifier that reads the manifest and checks required files and fields.
- [x] 2.2 Emit JSON and Markdown package-readiness evidence with `pass`, `warning`, `blocking`, `operator_guided`, `known_limitation`, and `not_provided` states.
- [x] 2.3 Classify runtime smoke, private repository token validation, live benchmark, and readiness history as explicit non-pass lanes unless evidence is provided.

## 3. Documentation and Runbooks

- [x] 3.1 Add self-hosted package guide covering package layout, setup, validation, and handoff boundaries.
- [x] 3.2 Add deployment `.env` template for self-hosted operators.
- [x] 3.3 Add first-admin/bootstrap initialization guidance.
- [x] 3.4 Add backup, restore, upgrade, and rollback runbook guidance.
- [x] 3.5 Update self-hosted readiness, delivery rehearsal, and commercial baseline docs to reference package manifest and verifier evidence.

## 4. Tests and Validation

- [x] 4.1 Add tests for package builder manifest, allowlisted files, generated README, and secret exclusions.
- [x] 4.2 Add tests for verifier pass/blocking/non-pass lane classification and Markdown output.
- [x] 4.3 Run targeted packaging tests.
- [x] 4.4 Run OpenSpec strict validation.

## 5. Real Rehearsal and Evidence

- [x] 5.1 Build a real local self-hosted package into `.tmp`.
- [x] 5.2 Verify the generated package and produce JSON/Markdown package evidence.
- [x] 5.3 Use browser/operator checks on the running real stack to confirm package docs point to currently working URLs and readiness flow.
- [x] 5.4 Record update-log evidence for generated package, verifier output, tests, and browser/operator rehearsal.

## 6. Archive and Submit

- [x] 6.1 Sync specs into main OpenSpec specs.
- [x] 6.2 Archive the OpenSpec change.
- [x] 6.3 Commit, push, and confirm CI.
