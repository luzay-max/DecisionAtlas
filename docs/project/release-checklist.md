# Release Checklist

## Canonical release baseline

- [x] run `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/ci/pre-release.ps1`
- [x] record the validated commit hash or final tag target verification command
- [x] identify intended tag, for example `v0.3.0-rc.1`

This is the canonical local release baseline validation path for the current branch. It covers:

- workspace tests and typechecks
- engine pytest
- offline benchmark fixture validation
- AI-agent governance guardrail interface availability, including optional enforcement preview text
- Playwright smoke coverage

Run individual commands only when debugging a failure from the canonical script.

## Default governance development protocol

- [ ] run `python scripts/governance/agent_guardrail.py --protocol-status --summary` before non-trivial implementation
- [ ] run `python scripts/governance/agent_guardrail.py --protocol-status --summary` after targeted validation and before claiming completion
- [ ] record any `caution` or `pause` evidence in the implementation, archive, commit, or readiness handoff

The protocol status is local workflow evidence for developers and AI agents. It reports active OpenSpec context, guardrail status, diff status, drift status, required tests, recommended actions, human questions, and handoff guidance.

This protocol does not replace the canonical release baseline command. It remains advisory by default and is separate from optional `--enforcement-preview` or `--strict-exit` behavior.

## Release evidence bundle

- [ ] generate a release evidence bundle after running the relevant validation commands
- [ ] attach or reference both `.tmp/release-evidence.json` and `.tmp/release-evidence.md` in release, PR, archive, or hosted-preview handoff notes
- [ ] disclose any `warning`, `caution`, `pause`, missing optional input, or real-repo benchmark blocker before claiming clean readiness

Default local evidence command after a normal release review:

```powershell
python scripts/ci/collect_release_evidence.py `
  --pre-release-status passed `
  --openspec-status passed `
  --offline-benchmark-status passed `
  --guardrail-status caution
```

Evidence command with explicit real-repo benchmark comparison output:

```powershell
python scripts/ci/collect_release_evidence.py `
  --pre-release-status passed `
  --openspec-status passed `
  --offline-benchmark-status passed `
  --guardrail-report .tmp/agent-guardrail.json `
  --benchmark-comparison-report .tmp/real-repo-benchmark-comparison.json
```

Required gates:

- canonical pre-release baseline: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/ci/pre-release.ps1`
- OpenSpec strict validation: `openspec validate --all --strict`
- offline benchmark fixture validation: `python scripts/ci/run_benchmark.py`

Advisory confidence signals:

- governance guardrail status or JSON report
- targeted test summary
- real-repo benchmark comparison JSON

The evidence bundle is local and non-mutating. It does not create tags, push commits, publish releases, archive OpenSpec changes, or run live/network-heavy benchmark checks by default. Optional evidence must be supplied through explicit paths; missing optional evidence is recorded instead of treated as a hidden pass.

## Readiness evidence history

- [ ] after generating release, hosted readiness, or benchmark comparison evidence, archive selected artifacts into durable readiness history when they represent a release, preview, or meaningful validation checkpoint
- [ ] review `docs/evidence/readiness/index.md` and `docs/evidence/readiness/trend.md` before claiming readiness trend improvement
- [ ] disclose `warning`, `blocking`, `operator_guided`, `known_limitation`, and `not_provided` states instead of converting them into pass

Example archive command:

```powershell
python scripts/ci/collect_readiness_evidence_history.py archive `
  --label v0-3-rc1 `
  --version-label v0.3.0-rc.1 `
  --commit <commit> `
  --release-evidence-json .tmp/release-evidence.json `
  --release-evidence-markdown .tmp/release-evidence.md `
  --hosted-readiness-json .tmp/hosted-operator-readiness.json `
  --hosted-readiness-markdown .tmp/hosted-operator-readiness.md `
  --benchmark-comparison-json .tmp/live-real-repo-comparison-2026-05-08.json `
  --benchmark-comparison-markdown .tmp/live-real-repo-comparison-2026-05-08.md
```

Regenerate history summaries without archiving a new entry:

```powershell
python scripts/ci/collect_readiness_evidence_history.py summarize
```

`.tmp` remains scratch output. Durable readiness history requires explicit archive command inputs and must not include secrets, private repository contents, raw model output, or unnecessary local-only logs.

## Self-hosted commercial readiness

- [ ] review [Self-Hosted Commercial Baseline](self-hosted-commercial-baseline.md) before customer evaluation or private deployment handoff
- [ ] run [Self-Hosted Readiness Checklist](self-hosted-readiness-checklist.md) for Community, Team Self-hosted, or Enterprise Self-hosted packaging
- [ ] run or reference [Self-Hosted Delivery Rehearsal](self-hosted-delivery-rehearsal.md) before customer-facing self-hosted readiness claims
- [ ] prepare [Code Decision Audit Template](code-decision-audit-template.md) when the release or evaluation is used as a paid pilot/customer handoff
- [ ] disclose deferred capabilities: billing, full SaaS org management, hosted multi-tenancy, Marketplace/self-service OAuth, hosted secret vault, permanent buyout licensing, and hosted managed service operations
- [ ] disclose that product/support tier boundaries do not imply runtime license enforcement in the current baseline
- [ ] preserve `warning`, `blocking`, `operator_guided`, `known_limitation`, and `not_provided` states in customer-facing evidence

Latest self-hosted delivery rehearsal:

- Entry: `docs/evidence/readiness/2026-05-20-self-hosted-delivery-rehearsal/`
- Summary: `docs/evidence/readiness/2026-05-20-self-hosted-delivery-rehearsal/summary.md`
- Status: `passed`
- Release evidence: required gates and advisory evidence passed
- Hosted readiness: `pass`; Web/API/Engine/full health/smoke/seeded demo readiness passed, reset/reseed recovery remains operator-guided
- Benchmark comparison: passed with 0 regressions and 0 operational blockers

Latest v0.3 RC pre-tag validation:

- Intended tag: `v0.3.0-rc.1`
- OpenSpec strict validation: 2026-04-29 09:32 +08:00, `34 passed, 0 failed`
- Canonical release gate: 2026-04-29 09:32 +08:00, passed with exit code `0`
- Workspace tests: API `25 passed`, web `58 passed`
- Engine pytest: `167 passed`
- Playwright smoke: `1 passed`
- Final tag target verification after tagging: `git rev-parse --short v0.3.0-rc.1`

Latest post-stage-7 documentation and governance validation:

- OpenSpec strict validation: 2026-05-06, `37 passed, 0 failed`
- Governance guardrail tests: include summary output coverage for workflow checkpoints
- AI-agent governance guardrail interface availability: `continue` on a clean working tree; enforcement preview returned `pass`
- Governance stage 5/6/7 tests: `19 passed`
- Seeded demo recovery tests: verify readiness detection, consumed review queue reset, and imported workspace preservation
- Migration revision-length/schema tests: include `tests/db/test_migrations.py`
- Real Postgres `alembic upgrade head`: passed after shortening revision `0008_governance_ingest`
- Real stack startup: default startup is non-destructive; use `scripts/dev/start-real-stack.ps1 -ResetSeededDemo` when the seeded guided demo lane must be restored before startup
- Playwright smoke against running real stack: `1 passed`

## Mandatory product baseline

- [ ] Local/bootstrap session recovery works in the supported local stack path
- [ ] Owner scope is visible in product navigation
- [ ] Role gates distinguish admin/reviewer/viewer product actions
- [ ] Demo workspace seeds correctly
- [ ] Seeded demo readiness check reports accepted decisions, candidate queue, source refs, timeline-ready history, and open drift alert state
- [ ] Seeded demo reset restores consumed review/demo state without deleting imported workspaces
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
- [ ] Governance Markdown ingest is documented as a human-reviewed rules flow
- [ ] AI-agent governance guardrail returns advisory `continue` / `caution` / `pause`
- [ ] Governance guardrail is documented as non-blocking by default
- [ ] Default governance development protocol status reports OpenSpec context, guardrail status, required tests, recommended actions, human questions, and handoff guidance
- [ ] Optional governance enforcement preview, if used, is recorded as advisory evidence and not treated as the default release gate

## Mandatory documentation baseline

- [ ] README matches the current product state
- [ ] `README_zh-CN.md` mirrors README workflow guidance
- [ ] `docs/project/quick-start.md` is accurate
- [ ] `docs/project/quick-start_zh-CN.md` mirrors quick-start guidance
- [ ] `docs/project/governance-agent-guardrail.md` documents agent usage and pause behavior
- [ ] `docs/project/governance-agent-guardrail.md` documents the default local governance development protocol
- [ ] quick start/deployment/operator docs distinguish non-destructive seed, reset, reseed, and explicit `-ResetSeededDemo`
- [ ] `docs/project/demo-script.md` matches current routes
- [ ] `docs/plans/2026-04-27-decisionatlas-v0-3-next-roadmap.md` reflects the current next route
- [ ] `docs/plans/2026-05-06-decisionatlas-post-stage-7-master-plan.md` records the current post-stage-7 route
- [ ] `docs/project/2026-05-06-update-log.md` records the latest stage 7, migration, and real-stack validation evidence
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
- [ ] optionally run `python scripts/ci/run_benchmark.py --live-real-repos --repo-id browser-use` and inspect both `.tmp/live-real-repo-validation-report.json` and `.tmp/live-real-repo-validation-report.md`
- [ ] summarize or attach dated live reports when they support a release decision; do not commit default `.tmp/` reports as durable evidence

These checks improve release confidence but are not part of the default offline release gate because they depend on live providers, network conditions, and existing imported workspace state.

## Optional governed hosted preview readiness

- [ ] hosted health check result recorded for web/API/engine, or explicitly marked operator-guided / known limitation when no hosted URLs are supplied
- [ ] hosted guided-demo smoke result recorded for `demo-workspace`
- [ ] seeded demo readiness or reset/reseed recovery result recorded
- [ ] `/governance` walkthrough checked if the preview includes governance Markdown ingest or rule review
- [ ] `python scripts/governance/agent_guardrail.py --summary` result recorded, including any `caution` or `pause` evidence
- [ ] optional `python scripts/governance/agent_guardrail.py --enforcement-preview release-checklist --summary` result recorded with source evidence and any human override note if used
- [ ] optional live real-repository value report summarized or attached externally if used as preview evidence
- [ ] preview notes state this is not production SaaS and does not include billing, full org admin, secret vault, marketplace self-service, multiplayer review, or default governance enforcement

These checks are governed hosted-preview confidence evidence. They do not replace the canonical local release baseline and must not be treated as default CI enforcement.

Optional enforcement preview output is warning/report oriented by default. Do not treat `--enforcement-preview` or `--strict-exit` as part of the canonical release baseline unless a future explicit OpenSpec change changes the release gate.

## Tagging and publish

- [ ] push `main`
- [ ] create release tag `v0.3.0-rc.1` only after the release commit is clean
- [ ] push release tag `v0.3.0-rc.1`
- [ ] verify local and remote tag state
- [ ] publish release notes from the latest milestone summary
