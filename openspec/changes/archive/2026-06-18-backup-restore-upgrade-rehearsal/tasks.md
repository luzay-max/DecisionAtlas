## 1. Rehearsal Evidence Contract

- [x] 1.1 Add a safe backup/restore/upgrade rehearsal example JSON template under `templates/`.
- [x] 1.2 Add a non-destructive rehearsal script that validates continuity lanes and writes JSON/Markdown evidence.
- [x] 1.3 Ensure the script preserves `operator_guided`, `known_limitation`, `not_provided`, `warning`, `blocking`, and `pass` states.

## 2. Documentation And Package Integration

- [x] 2.1 Update self-hosted operations and delivery docs to reference the rehearsal command and evidence outputs.
- [x] 2.2 Update self-hosted commercial baseline to distinguish package readiness from continuity readiness.
- [x] 2.3 Include the rehearsal template/script/evidence expectation in self-hosted package build and verification.

## 3. Tests

- [x] 3.1 Add tests for passing/operator-guided rehearsal evidence.
- [x] 3.2 Add tests for missing required lanes and invalid statuses.
- [x] 3.3 Add tests for obvious secret/token/private-key leakage blockers.
- [x] 3.4 Update package/document verification tests for the new continuity evidence lane.

## 4. Validation And Evidence

- [x] 4.1 Generate `.tmp` JSON/Markdown backup/restore/upgrade rehearsal evidence from the committed safe sample.
- [x] 4.2 Run targeted CI tests for the rehearsal script and updated package/docs verifiers.
- [x] 4.3 Run OpenSpec strict validation for the change and all specs.
- [x] 4.4 Use Browser/Chromium to render the Markdown rehearsal material and confirm readability.
- [x] 4.5 Run or reuse a random public GitHub repository evidence check as a non-sensitive live-repo validation habit.
- [x] 4.6 Run governance guardrail and record the result in the handoff.
- [x] 4.7 Record this change in the 2026-06-18 update log with commands, limitations, and generated evidence.
