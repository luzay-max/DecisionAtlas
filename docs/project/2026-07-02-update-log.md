# 2026-07-02 Update Log

## streamline-workspace-interaction-flow

### Implemented

- Added a current/target interaction-flow plan at `docs/plans/2026-07-02-decisionatlas-interaction-flow-optimization-plan.md`.
- Added role-aware homepage next actions for admin, reviewer, viewer, and operator workflows.
- Made repository import a visible guided flow on the homepage while keeping execution controls in the admin/advanced area.
- Split global operations and workspace workflow navigation more clearly in the sidebar.
- Added active workspace context banners to dashboard, review, search, timeline, drift, and decision detail pages.
- Strengthened decision detail as the cross-view object hub with next actions back to review, search, timeline, drift, and evidence.
- Reframed Evidence Center around release/operator questions: guardrail, benchmark comparison, hosted readiness, release evidence, and missing evidence next actions.
- Added/updated unit and browser smoke coverage for homepage import guidance, Evidence Center readiness flow, workspace context, and review/search-to-decision-detail continuity.

### Validation

- `pnpm --filter @decisionatlas/web test`: 20 test files passed, 78 tests passed.
- `pnpm --filter @decisionatlas/web typecheck`: passed.
- `pnpm --filter @decisionatlas/web exec playwright test mimo-ui-smoke.spec.ts --config playwright.config.ts --reporter=line`: 8 browser smoke tests passed against local engine/API/web smoke stack.
- `openspec validate streamline-workspace-interaction-flow --type change --strict`: passed.

### Notes

- Browser smoke required clearing local proxy environment variables for localhost checks because `all_proxy=http://127.0.0.1:7890` caused false 502/connection failures against local services.
- Playwright selectors were scoped to real `main` content to avoid matching Next streaming hidden payload markup.

## external-self-hosted-install-evidence

### Implemented

- Added `templates/external-self-hosted-install-evidence.example.json` for operator-filled evidence from a clean VM, another machine, or customer-controlled host.
- Added `scripts/ci/collect_external_self_hosted_install_evidence.py` to generate sanitized JSON/Markdown evidence from explicit input only.
- Classified external evidence lanes as `passed`, `warning`, `operator_guided`, `not_provided`, or `blocked`; missing or unsafe required proof does not become pass.
- Added redaction blocking for token-like values, `.env` secret assignments, private key markers, raw backup markers, and raw private repository snippet markers.
- Integrated external install evidence into clean install rehearsal, team handoff report, Code Decision Audit report, self-hosted package verification, and package builder assets.
- Added `docs/project/external-self-hosted-install-evidence.md` and updated self-hosted package, delivery rehearsal, handoff, audit, and commercial baseline docs to separate local clean install from customer-host proof.

### Validation

- `python -m pytest services/engine/tests/ci/test_external_self_hosted_install_evidence.py services/engine/tests/ci/test_team_handoff_report.py services/engine/tests/ci/test_code_decision_audit_report.py services/engine/tests/ci/test_self_hosted_package.py services/engine/tests/ci/test_clean_self_hosted_install_rehearsal.py -q`: 22 tests passed.
- `python scripts\ci\collect_external_self_hosted_install_evidence.py --input-json templates\external-self-hosted-install-evidence.example.json --output-json .tmp\external-self-hosted-install-evidence.json --output-markdown .tmp\external-self-hosted-install-evidence.md`: generated JSON/Markdown with expected `warning` status for template/operator-guided lanes.
- `openspec validate external-self-hosted-install-evidence --type change --strict`: passed.
- `openspec validate --all --strict`: 68 items passed, 0 failed.

### Notes

- Template collector output is intentionally `warning` until actual external startup, health, browser smoke, repository import, and readiness evidence are filled by an operator.
- Customer-facing material must not claim external/customer-host install proof from package verification or local clean install rehearsal alone.
