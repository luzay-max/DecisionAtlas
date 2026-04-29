# Release Checklist

## Canonical release baseline

- [x] run `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/ci/pre-release.ps1`
- [x] record the validated commit hash or final tag target verification command
- [x] identify intended tag, for example `v0.3.0-rc.1`

This is the canonical local release baseline validation path for the current branch. It covers:

- workspace tests and typechecks
- engine pytest
- offline benchmark fixture validation
- Playwright smoke coverage

Run individual commands only when debugging a failure from the canonical script.

Latest v0.3 RC pre-tag validation:

- Intended tag: `v0.3.0-rc.1`
- OpenSpec strict validation: 2026-04-29 09:32 +08:00, `34 passed, 0 failed`
- Canonical release gate: 2026-04-29 09:32 +08:00, passed with exit code `0`
- Workspace tests: API `25 passed`, web `58 passed`
- Engine pytest: `167 passed`
- Playwright smoke: `1 passed`
- Final tag target verification after tagging: `git rev-parse --short v0.3.0-rc.1`

## Mandatory product baseline

- [ ] Local/bootstrap session recovery works in the supported local stack path
- [ ] Owner scope is visible in product navigation
- [ ] Role gates distinguish admin/reviewer/viewer product actions
- [ ] Demo workspace seeds correctly
- [ ] Review queue shows at least one candidate decision
- [ ] Why-search returns cited answers for seed queries
- [ ] Drift page shows at least one alert
- [ ] At least one imported workspace produces reviewable candidate decisions
- [ ] Imported why-search either returns cited accepted-decision answers or an explicit evidence-limited outcome
- [ ] Imported drift flow is understandable for the current workspace state
- [ ] Imported dashboard/search readiness shows review, why, and drift states with recommended actions
- [ ] At least one imported why answer uses chunk-backed supporting evidence without losing the accepted-decision anchor
- [ ] GitHub App installation binding is documented as an admin/operator flow
- [ ] Token-backed private repository access binding is documented as an admin/operator flow

## Mandatory documentation baseline

- [ ] README matches the current product state
- [ ] `docs/project/quick-start.md` is accurate
- [ ] `docs/project/demo-script.md` matches current routes
- [ ] `docs/plans/2026-04-27-decisionatlas-v0-3-next-roadmap.md` reflects the current next route
- [ ] `docs/project/release-notes-v0.3.0-rc.1.md` records shipped capabilities, validation evidence, supported scope, limitations, and tag readiness
- [ ] `docs/project/release-notes-v0.3.0-rc.1_zh-CN.md` mirrors the v0.3.0-rc.1 release summary for Chinese readers
- [ ] FAQ reflects actual limitations
- [ ] `docs/project/real-repository-validation-baseline.md` matches the current curated repo set and imported-workspace expectations

## Mandatory open source trust baseline

- [ ] `LICENSE` present
- [ ] `SECURITY.md` present
- [ ] issue templates present
- [ ] PR template present
- [ ] `CODEOWNERS` present

## Mandatory limitation disclosures

- [ ] full SaaS org-management limitation stated
- [ ] secret vault limitation stated
- [ ] GitHub Marketplace/OAuth self-service limitation stated
- [ ] multi-user collaborative review limitation stated
- [ ] semantic drift conservatism stated
- [ ] demo-only assumptions stated
- [ ] real imported-workspace sparsity limits stated
- [ ] public-repo default import path and admin/operator access-source binding scope stated
- [ ] imported readiness and evidence-limited outcomes explained

## Optional operator-guided real-repo validation

- [ ] import a curated public repository such as `browser-use/browser-use`
- [ ] confirm the imported workspace reaches a bounded state such as `review_ready`, `why_ready`, `evidence_limited`, or another explicit operator-readable outcome
- [ ] ask a focused imported why-question and confirm the answer includes citations or a bounded evidence-limited status
- [ ] run drift evaluation once and confirm the current state is understandable for the imported workspace

These checks improve release confidence but are not part of the default offline release gate because they depend on live providers, network conditions, and existing imported workspace state.

## Tagging and publish

- [ ] push `main`
- [ ] create release tag `v0.3.0-rc.1` only after the release commit is clean
- [ ] push release tag `v0.3.0-rc.1`
- [ ] verify local and remote tag state
- [ ] publish release notes from the latest milestone summary
