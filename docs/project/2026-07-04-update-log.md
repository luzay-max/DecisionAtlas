# 2026-07-04 Update Log

## pilot-customer-trial-package

### Implemented

- Added `scripts/ci/collect_pilot_customer_trial_package.py`.
- Added a generated pilot customer trial package that composes customer-facing pilot materials with selected evidence lanes.
- The collector writes `.tmp/pilot-customer-trial-package.json`, `.tmp/pilot-customer-trial-package.md`, and a bundle directory under `.tmp/pilot-customer-trial-package/pilot-customer-trial-package/`.
- Bundle output includes `README.md`, `operator-checklist.md`, `evidence-manifest.json`, and `evidence-manifest.md`.
- Added required material checks for pilot delivery, demo, deployment checklist, FAQ, tier comparison, delivery email, commercial proposal, sales materials, private-repo template, package guide, support boundary, and real external host trial guide.
- Added evidence lanes for pilot delivery verification, commercial proposal verification, package verification, clean install rehearsal, release rehearsal, customer-host v2, real external host trial, full-chain random repo release, readiness history, private-repo evidence, and team handoff.
- Added redaction blocking for obvious token, secret assignment, private key, raw backup, or raw private repository snippet markers in operator notes.
- Added `services/engine/tests/ci/test_pilot_customer_trial_package.py`.
- Added `docs/project/pilot-customer-trial-package.md`.
- Updated completion taskbook and post-full-chain roadmap.

### Validation

- `python -m pytest services/engine/tests/ci/test_pilot_customer_trial_package.py -q`: 5 tests passed.
- `python scripts\ci\verify_pilot_customer_delivery_kit.py ...`: generated pilot delivery verification with status `pass`.
- `python scripts\ci\verify_pilot_commercial_proposal_kit.py ...`: generated commercial proposal verification with status `pass`.
- `python scripts\ci\collect_pilot_customer_trial_package.py ...`: generated JSON/Markdown and bundle directory with status `warning`.

### Notes

- Current trial package status is `warning` with 0 blocking lanes.
- This is expected because real external host trial evidence still reports template/sample boundary rather than clean customer-controlled host proof.
- The package is now ready as an operator assembly point; the next proof step is running the stack on a real external/customer-controlled machine and regenerating the evidence chain.

## reduce-random-repo-import-warning-lanes

### Implemented

- Added `scripts/ci/collect_random_repo_warning_lane_reduction.py`.
- Added deterministic classification for random repository release warning lanes: product-controlled, external dependency, operator-guided, not-provided, and blocking.
- Added JSON/Markdown output at `.tmp/random-repo-warning-lane-reduction.json` and `.tmp/random-repo-warning-lane-reduction.md`.
- Extended readiness evidence history with `random_repo_warning_lane_reduction` family.
- Archived smoke evidence at `docs/evidence/readiness/2026-07-04-random-repo-warning-lane-reduction-smoke/`.
- Added `services/engine/tests/ci/test_random_repo_warning_lane_reduction.py`.
- Added `docs/project/random-repo-warning-lane-reduction.md`.

### Validation

- `python -m pytest services\engine\tests\ci\test_random_repo_warning_lane_reduction.py -q`: 4 tests passed.
- `python scripts\ci\collect_random_repo_warning_lane_reduction.py ...`: generated warning-lane reduction evidence with status `warning`.
- `python scripts\ci\collect_readiness_evidence_history.py archive ...`: archived the new evidence family into readiness history.

### Notes

- Current warning-lane reduction status is `warning` with 0 blocking lanes.
- Real random repositories remain `n8n` and `rich`.
- Classification found 3 product-controlled lanes and 11 operator-guided/customer-host proof lanes.
- This change does not claim clean pass; it makes the remaining warning work explainable and prioritizable.

## improve-real-repo-core-loop-quality

### Implemented

- Fixed release rehearsal benchmark comparison status derivation when comparison evidence has no explicit top-level status.
- Added action categories to imported workspace core-loop lanes.
- Added multi-repo diagnosis aggregate action category counts.
- Updated warning-lane reduction to use action category counts and deduplicate release/full-chain multi-repo aggregate lanes.
- Regenerated real repo evidence for `n8n` and `rich`.
- Archived readiness evidence at `docs/evidence/readiness/2026-07-04-real-repo-core-loop-quality-smoke/`.
- Added `docs/project/real-repo-core-loop-quality.md`.

### Validation

- `python -m pytest services\engine\tests\ci\test_release_rehearsal_evidence.py services\engine\tests\ci\test_imported_workspace_core_loop.py services\engine\tests\ci\test_multi_repo_live_diagnosis.py services\engine\tests\ci\test_random_repo_warning_lane_reduction.py -q`: 22 tests passed.
- `python scripts\ci\collect_random_repo_warning_lane_reduction.py ...`: product-controlled warning lanes reduced from 3 to 1, with 0 blocking.
- System Chrome browser smoke opened `/`, `/evidence`, `/review`, and API `/health` successfully.
- `pnpm --filter @decisionatlas/web exec playwright test team-self-hosted-rehearsal.spec.ts --config playwright.config.ts --reporter=line`: 1 test passed.

### Notes

- The release remains `warning`; this is correct because customer-host proof is still template/operator-guided and `rich` still has why/drift quality work.
- The useful progress is attribution quality: false/duplicate product-controlled lanes were removed, leaving one concrete product quality target.
