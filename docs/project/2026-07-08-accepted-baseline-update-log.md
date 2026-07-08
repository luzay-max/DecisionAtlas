# 2026-07-08 Accepted Baseline Update Log

## improve-real-repo-accepted-decision-baseline

### Implemented

- Added accepted-decision baseline measurement to imported workspace core-loop evidence.
- Added accepted baseline status, strength, candidate count, accepted count, and bounded sample titles.
- Added baseline status/counts to why/drift grounding evidence.
- Propagated baseline summaries into multi-repo live diagnosis JSON/Markdown.
- Added baseline details to warning-lane reduction classified lanes and Markdown.
- Archived readiness evidence at `docs/evidence/readiness/2026-07-08-accepted-decision-baseline-smoke/`.
- Added `docs/project/accepted-decision-baseline.md`.

### Validation

- `python -m pytest services\engine\tests\ci\test_imported_workspace_core_loop.py services\engine\tests\ci\test_multi_repo_live_diagnosis.py services\engine\tests\ci\test_random_repo_warning_lane_reduction.py -q`: 19 tests passed.
- `openspec validate --all --strict`: 84 items passed before archive.
- Real stack health: Web `3000`, API `3001`, Engine `8000` returned 200.
- Chrome smoke opened `/`, `/evidence`, `/review`, and API `/health`.
- `pnpm --filter @decisionatlas/web exec playwright test team-self-hosted-rehearsal.spec.ts --config playwright.config.ts --reporter=line`: 1 test passed.
- Real evidence chain regenerated for `n8n-io/n8n` and `Textualize/rich`.

### Notes

- Release evidence remains `warning`, not `pass`.
- The important improvement is that `rich` now shows a concrete baseline gap: accepted count `0`, candidate count `35`, next action `review_candidates_into_accepted_baseline`.
- This prepares the next product step: convert selected candidates into accepted decisions through a controlled review flow rather than hiding the warning.
