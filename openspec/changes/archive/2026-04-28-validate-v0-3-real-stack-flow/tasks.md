## 1. Validation Inventory

- [x] 1.1 Identify the exact v0.3 RC commit and current working-tree baseline before running the matrix.
- [x] 1.2 Inventory current supported commands for demo stack, real stack, hosted health/smoke, reset/reseed, import, auth/scope, GitHub App binding, private repo binding, and pre-release validation.
- [x] 1.3 Create the initial `docs/project/v0-3-real-stack-validation-report.md` with matrix columns for lane, command/action, observed result, status, known limitation, and follow-up.

## 2. Deterministic Local Validation

- [x] 2.1 Run or verify the seeded demo lane: demo workspace, review path, why path, drift path, and reset/reseed behavior where applicable.
- [x] 2.2 Run or verify the real local stack startup with Postgres/Redis, migrations, seed behavior, API health, engine health, and web access.
- [x] 2.3 Run or verify the public repository import lane: lookup, import, dashboard readiness, and workspace reuse or sync behavior.
- [x] 2.4 Run the canonical release gate with `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ci\pre-release.ps1`.

## 3. Platform Flow Validation

- [x] 3.1 Validate session recovery and owner scope switching behavior in the current product.
- [x] 3.2 Validate role-gated product actions for reviewer/admin boundaries without expanding the role model.
- [x] 3.3 Validate GitHub App binding surface behavior, access-source label visibility, and any provider-dependent limitations.
- [x] 3.4 Validate private repository access binding surface behavior, token non-echo behavior, access-source status visibility, and any credential-dependent limitations.

## 4. Report and Fixes

- [x] 4.1 Record all observed results in the validation report with `pass`, `blocking`, `non-blocking`, or `known limitation` status.
- [x] 4.2 Fix only blocking issues that prevent the v0.3 RC baseline from being truthfully validated, then rerun the affected checks.
- [x] 4.3 Record deferred follow-up items under the correct next roadmap area without implementing unrelated feature expansion.
- [x] 4.4 Update release-facing docs if validation reveals command drift, lane-boundary ambiguity, or unsupported instructions.

## 5. Final Checks

- [x] 5.1 Validate the new and modified OpenSpec specs for this change.
- [x] 5.2 Confirm there are no active unrelated changes mixed into the validation work.
- [x] 5.3 Summarize whether v0.3 is ready for the next planned phase or blocked by specific findings.
