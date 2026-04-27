# 2026-04-24 Update Log

## Summary

Today's work moved DecisionAtlas from a stronger real-repository baseline into a more operable hosted-demo posture.

The main outcomes are:

- prepared the `v0.2.2` release baseline and documented the current branch capability boundary
- stabilized live real-repo validation so curated repositories report bounded operator-readable outcomes
- improved imported review and why-answer quality after the first accepted baseline
- added a hosted demo operator flow with health, smoke, reset, and reseed commands
- archived all active OpenSpec changes and pushed the resulting work to `main`

## Completed

### v0.2.2 release baseline

- Completed and archived `prepare-v0-2-2-release-baseline`.
- Updated release-facing documentation so README, quick start, FAQ, release notes, and checklist share the same branch baseline language.
- Confirmed the canonical release validation entrypoint remains:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ci\pre-release.ps1
```

- Kept optional live real-repo validation separate from the default offline release gate.
- Current local tag list still shows `v0.2.1`; `v0.2.2` tagging was treated as a release-operator action, not created by this session.

### Live real-repo validation

- Completed and archived `stabilize-live-real-repo-validation`.
- Extended the live validation path to report curated repository outcomes in bounded states instead of treating every missing result as a generic failure.
- Preserved offline benchmark fixture validation as the default branch gate.
- Continued using the curated repo set as the real-repo confidence surface:
  - `encode/httpx`
  - `fastapi/fastapi`
  - `Textualize/rich`
  - `n8n-io/n8n`
  - `browser-use/browser-use`

### Imported review decision quality

- Created, implemented, synced, and archived `improve-imported-review-decision-quality`.
- Improved imported review queue evidence so reviewers can judge candidates with less context switching.
- Added review surfaces for:
  - source-ref counts
  - source quotes
  - artifact provenance
  - confidence context
  - detail links
  - first-baseline guidance
- Fixed a sparse imported-review edge case so the empty queue does not overstate that the first candidate should be accepted.
- Synced resulting specs into:
  - `imported-review-decision-quality`
  - `real-repository-outcomes`
  - `source-ref-coverage`

### Imported why support quality

- Created, implemented, synced, and archived `improve-imported-why-support-quality`.
- Refined imported why primary-decision selection so focused questions prefer the accepted decision with the best rationale-thread fit rather than the nearest weak lexical neighbor.
- Kept focused why answers free of unrelated supporting context while preserving broad-question support behavior.
- Added support for stronger answer grading through bounded support bundles around one primary accepted decision.
- Added an equivalent-phrasing benchmark case for `browser-use/browser-use`.
- Synced resulting specs into:
  - `why-answer-support-grading`
  - `why-search-focus`
  - `why-search-retrieval-quality`
  - `real-repository-outcomes`
  - `lightweight-real-repo-benchmarks`

### Hosted demo operator flow

- Created, implemented, synced, and archived `prepare-hosted-demo-operator-flow`.
- Added operator-facing hosted demo guides:
  - `docs/project/hosted-demo-operator-guide.md`
  - `docs/project/hosted-demo-operator-guide_zh-CN.md`
- Added canonical hosted demo scripts:
  - `scripts/demo/health-check.ps1`
  - `scripts/demo/smoke-check.ps1`
  - `scripts/demo/reset-demo.ps1`
  - `scripts/demo/reseed-demo.ps1`
  - `scripts/demo/reset_seeded_demo.py`
- Updated Playwright config so the existing demo smoke can target an already-running hosted environment through:
  - `PLAYWRIGHT_BASE_URL`
  - `PLAYWRIGHT_SKIP_WEBSERVER=1`
- Added a bounded reset/reseed helper that targets only `demo-workspace` and does not delete imported workspaces by default.
- Updated English and Chinese deployment, quick start, FAQ, and demo script docs to point at the hosted operator path.
- Added `hosted-demo-operator-flow` as a main OpenSpec capability.

## Validation

### Imported review / why quality

- `pnpm --filter @decisionatlas/web test -- tests/review-page.test.tsx`
- `pnpm --filter @decisionatlas/web test -- tests/search-page.test.tsx`
- `python -m uv run pytest tests/retrieval/test_answering.py tests/api/test_query_api.py -q`
- `python -m uv run pytest tests/evals/test_benchmark_fixtures.py -q`
- `python scripts/ci/run_benchmark.py`

### Hosted demo operator flow

- `python -m uv run pytest tests/test_hosted_demo_operator_flow.py -q` -> `3 passed`
- `pnpm --filter @decisionatlas/web typecheck`
- PowerShell script parse checks for `scripts/demo/*.ps1`
- Local operator flow:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\dev\start-demo-stack.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\health-check.ps1 -SkipDependencyChecks
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\smoke-check.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\reset-demo.ps1 -UseLocalDemoDatabase
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\reseed-demo.ps1 -UseLocalDemoDatabase
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\dev\stop-demo-stack.ps1
```

### Full release baseline

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ci\pre-release.ps1` passed after the hosted operator flow work.
- The final full run included:
  - workspace tests and typechecks
  - engine pytest: `162 passed`
  - offline benchmark fixture validation
  - Playwright smoke: `1 passed`

## OpenSpec

Completed and archived:

- `prepare-v0-2-2-release-baseline`
- `stabilize-live-real-repo-validation`
- `improve-imported-review-decision-quality`
- `improve-imported-why-support-quality`
- `prepare-hosted-demo-operator-flow`

Current active changes:

- none

## Git / Branching

Work landed on `main` and was pushed to `origin/main`.

Today's visible commits:

- `3f7364e` `docs: prepare v0.2.2 release baseline`
- `1b77a88` `spec: plan live real repo validation`
- `b79b942` `test: stabilize live real repo validation`
- `d0d949a` `spec: archive live real repo validation`
- `dd64451` `spec: plan imported review decision quality`
- `04073e4` `feat: improve imported review evidence`
- `4e6daa8` `spec: archive imported review decision quality`
- `e795624` `feat: improve imported why support quality`
- `34fcc0b` `feat: add hosted demo operator flow`

## Current Reading of the Product

DecisionAtlas now has a cleaner staged posture:

1. The local release baseline is repeatable and documented.
2. The real-repo lane has bounded validation and better review/why quality after first acceptance.
3. The hosted demo path now has operator commands for health, smoke, reset, and reseed.
4. The next major product direction should be v0.3 platform productization rather than more demo hardening.

## Next Suggested Direction

The next planning slice should move into platform productization in this order:

1. `productize-login-and-scope-switching`
2. `productize-github-app-installation-flow`
3. `productize-private-repo-access`

Keep these as separate OpenSpec changes. The hosted demo flow is now stable enough to avoid mixing platform auth, GitHub App onboarding, and private repo setup into one large change.
