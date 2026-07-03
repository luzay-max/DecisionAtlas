# 2026-07-03 Update Log

## real-browser-workflow-rehearsal

### Implemented

- Added `apps/web/tests-e2e/real-browser-workflow-rehearsal.spec.ts`.
- The rehearsal starts from homepage onboarding, opens import controls like a human operator, checks a real public GitHub repository reference for `openai/openai-cookbook`, then walks demo workspace, review, why-search, drift, evidence, and team role separation.
- Added `docs/project/real-browser-workflow-rehearsal.md` with the local run command and evidence boundary.
- Added OpenSpec requirements for `real-browser-workflow-rehearsal` and updated workspace interaction, Mimo UI smoke, and live repository analysis specs.

### Validation

- `pnpm --filter @decisionatlas/web exec playwright test real-browser-workflow-rehearsal.spec.ts --config playwright.config.ts --reporter=line`: 1 passed.
- `pnpm --filter @decisionatlas/web exec playwright test mimo-ui-smoke.spec.ts team-self-hosted-rehearsal.spec.ts --config playwright.config.ts --reporter=line`: 9 passed.
- `pnpm --filter @decisionatlas/web test -- --run tests/home-page.test.tsx tests/team-management-panel.test.tsx`: 2 files passed, 3 tests passed.

### Notes

- The real GitHub repository reference is asserted in the browser flow, but import lookup is mocked for deterministic UI testing. Live import quality remains covered by benchmark/readiness evidence.
- Local proxy variables must be cleared or bypass localhost before Playwright starts smoke servers.

## project-completion-taskbook

### Implemented

- Added `docs/plans/2026-07-03-decisionatlas-completion-taskbook.md` as the current execution taskbook.
- Mapped 2026-05-08 and 2026-05-09 plan lines to `complete`, `partial`, `missing`, and `not-now` states.
- Listed next OpenSpec candidates in priority order: `imported-workspace-core-loop-rehearsal`, `multi-repo-live-diagnosis-rotation`, `release-rehearsal-one-command-evidence`, `review-audit-ux-hardening`, and `external-customer-host-rehearsal-v2`.
- Added OpenSpec requirements for maintaining the completion taskbook and making final roadmap updates reference it.

### Validation

- `openspec validate project-completion-taskbook --type change --strict`: passed.
- `openspec validate --all --strict`: passed after synchronization.

### Notes

- The taskbook does not claim final completion. It explicitly keeps real imported workspace core-loop proof and multi-repo live diagnosis as remaining high-priority work.

## imported-workspace-core-loop-rehearsal

### Implemented

- Added `scripts/ci/collect_imported_workspace_core_loop.py` to collect setup/reuse, dashboard, review, why-search, drift, and guardrail lane evidence for an imported workspace.
- Added `services/engine/tests/ci/test_imported_workspace_core_loop.py` covering clean, partial, missing workspace, and compact Markdown behavior.
- Added `apps/web/tests-e2e/imported-workspace-core-loop.spec.ts` to create or reuse a real public GitHub workspace for `pallets/flask` and walk dashboard, review, why-search, drift, and evidence pages in a browser.
- Added `docs/project/imported-workspace-core-loop-rehearsal.md` with collector and browser run commands plus evidence boundaries.
- Updated the completion taskbook to show that imported core-loop evidence exists, while multi-repo live diagnosis remains the next higher-priority gap.

### Validation

- `python -m pytest services/engine/tests/ci/test_imported_workspace_core_loop.py -q`: 4 tests passed.
- `pnpm --filter @decisionatlas/web exec playwright test imported-workspace-core-loop.spec.ts --config playwright.config.ts --reporter=line`: 1 browser test passed.
- `python scripts\ci\collect_imported_workspace_core_loop.py --repo pallets/flask --workspace-slug github-pallets-flask --why-question "why is this imported workspace interesting" --output-json .tmp\imported-workspace-core-loop-rehearsal.json --output-markdown .tmp\imported-workspace-core-loop-rehearsal.md`: generated JSON/Markdown with expected `warning` status.

### Notes

- The `pallets/flask` imported workspace browser path is real, but why-search is mocked in the browser test for deterministic UI validation.
- The collector smoke intentionally preserved warnings: review queue was empty, why-search was `evidence_limited`, drift was warning, and guardrail was `not_provided`.
- This improves core-loop evidence but does not replace the next `multi-repo-live-diagnosis-rotation` work.

## multi-repo-live-diagnosis-rotation

### Implemented

- Added `scripts/ci/collect_multi_repo_live_diagnosis.py` to select explicit or deterministic-random real public repositories from `examples/live-benchmarks/trend-pool.json`.
- Composed public GitHub import rehearsal with imported workspace core-loop evidence per repository.
- Added compact JSON/Markdown output with per-repo setup, review, why-search, drift, guardrail, aggregate counts, and recommended follow-up.
- Added `services/engine/tests/ci/test_multi_repo_live_diagnosis.py` for deterministic selection, unknown repo handling, mixed outcomes, and Markdown rendering.
- Added `docs/project/multi-repo-live-diagnosis-rotation.md` with operator commands and evidence boundaries.
- Updated the completion taskbook and OpenSpec main specs so the next priority moves to `release-rehearsal-one-command-evidence`.

### Validation

- `python -m pytest services/engine/tests/ci/test_multi_repo_live_diagnosis.py -q`: targeted tests pass.
- `python scripts\ci\collect_multi_repo_live_diagnosis.py --repo-id httpx --repo-id fastapi --output-json .tmp\multi-repo-live-diagnosis.json --output-markdown .tmp\multi-repo-live-diagnosis.md`: smoke diagnosis generates JSON/Markdown against real public repository metadata.
- `openspec validate multi-repo-live-diagnosis-rotation --type change --strict`: passed.
- `openspec validate --all --strict`: passed after synchronization.

### Notes

- This is diagnosis rotation evidence, not benchmark trend evidence. It answers whether selected real repositories can move through setup and core-loop diagnosis.
- Non-clean states such as `provider_failure`, `local_stack_failure`, `operator_guided`, `warning`, and `not_provided` are preserved instead of being hidden.

## release-rehearsal-one-command-evidence

### Implemented

- Added `scripts/ci/collect_release_rehearsal_evidence.py` as the one-command release rehearsal bundle collector.
- The collector discovers existing `.tmp` evidence by default and supports explicit paths for release evidence, hosted readiness, benchmark trend/comparison, multi-repo diagnosis, guardrail, and readiness history.
- Added opt-in `--run-multi-repo-diagnosis` to refresh real public repository diagnosis before bundling.
- Added `--archive-history` to copy the generated bundle into durable readiness history under `docs/evidence/readiness/`.
- Added `services/engine/tests/ci/test_release_rehearsal_evidence.py`.
- Added `docs/project/release-rehearsal-one-command-evidence.md` and synchronized OpenSpec specs.
- Updated the completion taskbook so the next priority is `review-audit-ux-hardening`.

### Validation

- `python -m pytest services/engine/tests/ci/test_release_rehearsal_evidence.py -q`: targeted tests pass.
- `python scripts\ci\collect_release_rehearsal_evidence.py --archive-history --output-json .tmp\release-rehearsal-evidence.json --output-markdown .tmp\release-rehearsal-evidence.md`: smoke rehearsal generates `.tmp` JSON/Markdown and readiness-history archive.
- `openspec validate release-rehearsal-one-command-evidence --type change --strict`: passed.
- `openspec validate --all --strict`: passed after synchronization.

### Notes

- The one-command bundle does not replace individual lane collectors. It makes the release handoff repeatable and shows missing or non-clean lanes in one place.
- Current smoke is expected to stay `warning` while optional lanes are missing or non-clean.

## review-audit-ux-hardening

### Implemented

- Added a review audit panel to show current review role, permission boundary, next action, and compact recent decision context.
- Made viewer review access explicitly read-only while still allowing authorized workspace evidence to be visible.
- Updated the self-hosted team browser rehearsal so a viewer account is assigned to `demo-workspace`, opens the review page, sees read-only guidance, and does not see review action controls.
- Relaxed candidate queue reads to viewer permission while keeping decision review mutation behind reviewer permission.
- Added `docs/project/review-audit-ux-hardening.md` and synchronized OpenSpec specs.
- Updated the completion taskbook so the next priority is external customer host rehearsal rather than more review UI hardening.

### Validation

- `pnpm --filter @decisionatlas/web test -- --run tests/review-page.test.tsx tests/review-audit-panel.test.tsx`: 2 files passed, 10 tests passed.
- `python -m pytest tests/api/test_team_api.py tests/api/test_decisions_api.py -q` from `services/engine`: 6 tests passed.
- `PLAYWRIGHT_SKIP_WEBSERVER=1 pnpm --filter @decisionatlas/web exec playwright test team-self-hosted-rehearsal.spec.ts --config playwright.config.ts --reporter=line`: 1 browser test passed.

### Notes

- This completes the current small-team review/audit UX hardening target.
- It does not claim complete GitLab-style organization management. Richer organization administration, billing, marketplace, and hosted multi-tenant work remain out of current self-hosted scope.

## external-customer-host-rehearsal-v2

### Implemented

- Added `scripts/ci/collect_external_customer_host_rehearsal_v2.py`.
- Added sanitized operator/customer host template at `templates/external-customer-host-rehearsal-v2.example.json`.
- Extended readiness history with `external_customer_host_rehearsal_v2` as a durable evidence family.
- Added `services/engine/tests/ci/test_external_customer_host_rehearsal_v2.py` and expanded readiness history tests.
- Added `docs/project/external-customer-host-rehearsal-v2.md`.
- Generated `.tmp/external-customer-host-rehearsal-v2.json` and `.tmp/external-customer-host-rehearsal-v2.md`.
- Archived smoke evidence to `docs/evidence/readiness/2026-07-03-external-customer-host-rehearsal-v2-smoke/`.

### Validation

- `python -m pytest services/engine/tests/ci/test_external_customer_host_rehearsal_v2.py services/engine/tests/ci/test_readiness_evidence_history.py -q`: 9 tests passed.
- `python scripts\ci\collect_external_customer_host_rehearsal_v2.py ... --archive-history`: generated JSON/Markdown and readiness-history archive with status `warning`.
- `PLAYWRIGHT_SKIP_WEBSERVER=1 pnpm --filter @decisionatlas/web exec playwright test team-self-hosted-rehearsal.spec.ts --config playwright.config.ts --reporter=line`: 1 browser test passed.

### Notes

- Current smoke uses the example template and existing local evidence, so it is evidence that the v2 customer-host rehearsal pipeline works.
- It is not a claim that a real customer-controlled production host has passed clean validation. Real customer-host proof requires replacing the template with observations from an actual external machine.

## full-chain-random-repo-release-rehearsal

### Implemented

- Added `scripts/ci/collect_full_chain_random_repo_release_rehearsal.py`.
- Extended readiness history with `full_chain_random_repo_release_rehearsal` as a durable evidence family.
- Added `services/engine/tests/ci/test_full_chain_random_repo_release_rehearsal.py` and expanded readiness history tests.
- Added `docs/project/full-chain-random-repo-release-rehearsal.md`.
- Ran random real public GitHub repository diagnosis through release rehearsal with seed `7303`.
- Generated `.tmp/full-chain-random-repo-release-rehearsal.json` and `.tmp/full-chain-random-repo-release-rehearsal.md`.
- Archived full-chain evidence to `docs/evidence/readiness/2026-07-03-full-chain-random-repo-release-rehearsal-smoke/`.

### Validation

- `python -m pytest services/engine/tests/ci/test_full_chain_random_repo_release_rehearsal.py services/engine/tests/ci/test_readiness_evidence_history.py -q`: 8 tests passed.
- `python scripts\ci\collect_release_rehearsal_evidence.py --run-multi-repo-diagnosis --random-count 2 --random-seed 7303 ...`: selected `n8n` and `rich`, generated warning evidence with no blocking lanes.
- `PLAYWRIGHT_SKIP_WEBSERVER=1 pnpm --filter @decisionatlas/web exec playwright test team-self-hosted-rehearsal.spec.ts --config playwright.config.ts --reporter=line`: 1 browser test passed.
- `python scripts\ci\collect_full_chain_random_repo_release_rehearsal.py ... --archive-history`: generated JSON/Markdown and readiness-history archive with status `warning`.

### Notes

- Current random real repositories were `n8n-io/n8n` and `Textualize/rich`.
- The top-level bundle has 5 lanes: random repo diagnosis, release rehearsal, customer-host v2, browser rehearsal, and readiness history.
- Current state is `warning` with 0 blocking lanes. This is appropriate because live repo and customer-host lanes still preserve non-clean evidence instead of being treated as clean pass.
