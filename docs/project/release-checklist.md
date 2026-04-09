# Release Checklist

## Product

- [ ] Demo workspace seeds correctly
- [ ] Review queue shows at least one candidate decision
- [ ] Why-search returns cited answers for seed queries
- [ ] Drift page shows at least one alert
- [ ] At least one imported workspace produces reviewable candidate decisions
- [ ] Imported why-search either returns cited accepted-decision answers or an explicit evidence-limited outcome
- [ ] Imported drift flow is understandable for the current workspace state
- [ ] Imported dashboard/search readiness shows review, why, and drift states with recommended actions
- [ ] At least one imported why answer uses chunk-backed supporting evidence without losing the accepted-decision anchor

## Local validation

- [ ] `pnpm test`
- [ ] `pnpm typecheck`
- [ ] `cd services/engine && uv run pytest -q`
- [ ] `python scripts/ci/run_benchmark.py`
- [ ] `pnpm --filter @decisionatlas/web exec playwright test`

## Documentation

- [ ] README matches the current product state
- [ ] `docs/project/quick-start.md` is accurate
- [ ] `docs/project/demo-script.md` matches current routes
- [ ] `docs/project/2026-03-27-next-phase-roadmap.md` reflects the latest shipped quality slices
- [ ] FAQ reflects actual limitations
- [ ] `docs/project/real-repository-validation-baseline.md` matches the current curated repo set and imported-workspace expectations

## Open source trust

- [ ] `LICENSE` present
- [ ] `SECURITY.md` present
- [ ] issue templates present
- [ ] PR template present
- [ ] `CODEOWNERS` present

## Known limitations communicated

- [ ] auth limitations stated
- [ ] semantic drift conservatism stated
- [ ] demo-only assumptions stated
- [ ] real imported-workspace sparsity limits stated
- [ ] public-repo-only import scope stated
- [ ] imported readiness and evidence-limited outcomes explained

## Tagging and publish

- [ ] run `powershell -ExecutionPolicy Bypass -File scripts/ci/pre-release.ps1`
- [ ] push `main`
- [ ] create release tag
- [ ] publish release notes from the latest milestone summary
