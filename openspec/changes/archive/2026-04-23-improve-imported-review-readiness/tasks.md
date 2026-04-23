## 1. Refine imported readiness and why contracts

- [x] 1.1 Update engine imported readiness/outcome modeling so candidate-only review progress and first accepted-baseline progress produce distinct next actions and downstream why/drift readiness.
- [x] 1.2 Update imported why support/readiness logic so a first accepted imported decision can unlock bounded why readiness only when the asked rationale thread is grounded to that accepted decision.
- [x] 1.3 Add or update engine tests that cover candidate-only review-ready workspaces, first accepted-baseline workspaces, and fail-closed why behavior when acceptance exists but grounding is still weak.

## 2. Align imported product surfaces

- [x] 2.1 Update dashboard, search, and any shared imported readiness UI to render the refined accepted-baseline milestone and recommended actions from backend-provided readiness data.
- [x] 2.2 Adjust review/why-facing copy so imported workspaces communicate the first accepted decision as the first durable product milestone without implying all downstream answers are now fully supported.
- [x] 2.3 Add or update web tests that cover candidate-only review guidance, first accepted-baseline guidance, and imported why availability after grounded acceptance.

## 3. Protect the behavior with benchmark coverage

- [x] 3.1 Extend lightweight real-repo benchmark fixtures with bounded expectations for first accepted-baseline progress and imported why readiness on curated repositories.
- [x] 3.2 Update benchmark validation so the new milestone-style expectations are checked in the default fixture-backed path.
- [x] 3.3 Run the targeted engine/web/benchmark validation loop and record which curated repositories still require operator-guided live smoke confirmation after the change lands.

## Validation Notes

- `python -m uv run pytest tests/api/test_timeline_dashboard_api.py tests/api/test_query_api.py tests/retrieval/test_answering.py tests/evals/test_benchmark_fixtures.py -q`
- `pnpm --filter @decisionatlas/web test -- tests/workspace-dashboard.test.tsx tests/search-page.test.tsx`
- `python scripts/ci/run_benchmark.py`

## Follow-up Live Smoke Confirmation

- `Textualize/rich`: confirm a first accepted imported decision still moves the workspace into the expected accepted-baseline milestone before broad why trust is implied.
- `browser-use/browser-use`: confirm the accepted-baseline milestone still preserves the stronger why/drift regression path on a known-good imported workspace.
- `n8n-io/n8n`: confirm the stress case can remain conversion-limited without falsely claiming accepted-baseline progress.
