# 2026-07-08 Update Log

## improve-real-repo-why-drift-grounding

### Implemented

- Added grounded reason metadata for product-controlled `why_search` and `drift` warning lanes.
- Added `lane_reasons` and `grounding_summary` to imported workspace core-loop evidence.
- Propagated grounding details into multi-repo live diagnosis JSON/Markdown.
- Added grounding details to random repo warning-lane reduction classified lanes and Markdown.
- Fixed real guardrail invocation drift by parsing current `agent_guardrail.py --summary` output instead of using the removed `--json` flag.
- Archived readiness evidence at `docs/evidence/readiness/2026-07-08-why-drift-grounding-smoke/`.
- Added `docs/project/why-drift-grounding.md`.

### Validation

- `python -m pytest services\engine\tests\ci\test_imported_workspace_core_loop.py services\engine\tests\ci\test_multi_repo_live_diagnosis.py services\engine\tests\ci\test_random_repo_warning_lane_reduction.py -q`: 18 tests passed.
- `openspec validate --all --strict`: 84 items passed.
- Real stack health: Web `3000`, API `3001`, Engine `8000` returned 200.
- Chrome smoke opened `/`, `/evidence`, `/review`, and API `/health`.
- `pnpm --filter @decisionatlas/web exec playwright test team-self-hosted-rehearsal.spec.ts --config playwright.config.ts --reporter=line`: 1 test passed.
- Real evidence chain regenerated for `n8n-io/n8n` and `Textualize/rich`.

### Notes

- Overall release evidence remains `warning`, not `pass`.
- `Textualize/rich` now reports grounded why/drift reasons, primarily `missing_accepted_decision_evidence`.
- This makes the next product-quality improvement measurable without hiding customer-host/template/operator-guided limitations.
