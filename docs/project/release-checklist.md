# Release Checklist

## Canonical release baseline

- [ ] run `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/ci/pre-release.ps1`

This is the canonical local release baseline validation path for the current branch. It covers:

- workspace tests and typechecks
- engine pytest
- offline benchmark fixture validation
- Playwright smoke coverage

Run individual commands only when debugging a failure from the canonical script.

## Mandatory product baseline

- [ ] Demo workspace seeds correctly
- [ ] Review queue shows at least one candidate decision
- [ ] Why-search returns cited answers for seed queries
- [ ] Drift page shows at least one alert
- [ ] At least one imported workspace produces reviewable candidate decisions
- [ ] Imported why-search either returns cited accepted-decision answers or an explicit evidence-limited outcome
- [ ] Imported drift flow is understandable for the current workspace state
- [ ] Imported dashboard/search readiness shows review, why, and drift states with recommended actions
- [ ] At least one imported why answer uses chunk-backed supporting evidence without losing the accepted-decision anchor

## Mandatory documentation baseline

- [ ] README matches the current product state
- [ ] `docs/project/quick-start.md` is accurate
- [ ] `docs/project/demo-script.md` matches current routes
- [ ] `docs/project/2026-03-27-next-phase-roadmap.md` reflects the latest shipped quality slices
- [ ] FAQ reflects actual limitations
- [ ] `docs/project/real-repository-validation-baseline.md` matches the current curated repo set and imported-workspace expectations

## Mandatory open source trust baseline

- [ ] `LICENSE` present
- [ ] `SECURITY.md` present
- [ ] issue templates present
- [ ] PR template present
- [ ] `CODEOWNERS` present

## Mandatory limitation disclosures

- [ ] auth limitations stated
- [ ] semantic drift conservatism stated
- [ ] demo-only assumptions stated
- [ ] real imported-workspace sparsity limits stated
- [ ] public-repo-only import scope stated
- [ ] imported readiness and evidence-limited outcomes explained

## Optional operator-guided real-repo validation

- [ ] import a curated public repository such as `browser-use/browser-use`
- [ ] confirm the imported workspace reaches a bounded state such as `review_ready`, `why_ready`, `evidence_limited`, or another explicit operator-readable outcome
- [ ] ask a focused imported why-question and confirm the answer includes citations or a bounded evidence-limited status
- [ ] run drift evaluation once and confirm the current state is understandable for the imported workspace

These checks improve release confidence but are not part of the default offline release gate because they depend on live providers, network conditions, and existing imported workspace state.

## Tagging and publish

- [ ] push `main`
- [ ] create release tag
- [ ] publish release notes from the latest milestone summary
