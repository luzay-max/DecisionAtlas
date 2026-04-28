# DecisionAtlas Release Notes: v0.3.0-rc.1

Status: release-candidate preparation  
Intended tag: `v0.3.0-rc.1`  
Baseline code commit before release-doc updates: `76d63ff`

## What changed since v0.2.2

- Platform foundation is now product-visible:
  - local/bootstrap session recovery
  - owner scope switching
  - role-gated product actions for imported workspace operations
- GitHub App installation binding is now an admin/operator product flow:
  - admins can bind a repository to an installation-backed access source
  - workspace and lookup surfaces can display GitHub App access-source labels
  - full Marketplace/OAuth self-service installation is still out of scope
- Private repository access binding is now an admin/operator product flow:
  - admins can bind token-backed private access inside the current owner scope
  - submitted token material is not echoed in the product result
  - full secret vault and rotation history are still out of scope
- Hosted demo operation is clearer:
  - health, smoke, reset, and reseed scripts exist for operator-guided demo confidence
  - local real/demo stack entry points have been cleaned up
  - removed obsolete early scripts: `scripts/dev/up.ps1`, `scripts/dev/prepare-demo.ps1`, and `scripts/ci/run_demo_smoke.ps1`
- Hosted preview readiness is tracked as a post-RC confidence layer:
  - `docs/project/hosted-preview-readiness.md` defines the pre-demo checklist
  - `docs/project/v0-3-hosted-preview-readiness-report.md` records hosted-preview readiness evidence and limitations
  - hosted checks do not replace the canonical local release gate
- Imported workspace quality work remains part of the baseline:
  - bounded readiness states
  - review quality improvements
  - accepted-decision anchored why answers
  - conservative drift behavior

## Canonical validation

Run the release baseline gate from the repository root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ci\pre-release.ps1
```

This covers:

- workspace tests and typechecks
- engine pytest
- offline benchmark fixture validation
- Playwright smoke coverage

Validation result for this release candidate:

- Passed on 2026-04-28 09:29 +08:00 with exit code `0`.
- Workspace validation passed: API tests `25 passed`, web tests `55 passed`, API/web typecheck passed.
- Engine pytest passed: `162 passed`.
- Offline benchmark fixture validation passed for benchmark queries, live-repo fixtures, and real-repo why/drift fixtures.
- Playwright smoke passed: `1 passed`.
- No release-blocking validation mismatch was found.

## Supported scope

- stable seeded guided demo workspace
- public GitHub repository import into imported workspaces
- imported readiness states for review, why, drift, evidence-limited, and conversion-limited outcomes
- candidate review and first accepted baseline workflow
- citation-first why answers with support grading
- chunk-backed supporting evidence behind accepted decisions
- rule-first and conservative semantic drift evaluation
- offline fixture-backed real-repo benchmark validation
- local/bootstrap session recovery
- owner scope switching and role-gated product actions
- GitHub App installation binding as an admin/operator flow
- token-backed private repository access binding as an admin/operator flow
- hosted demo health, smoke, reset, and reseed operator checks

## Known limitations

- v0.3.0-rc.1 is not a final production SaaS release.
- Full SaaS organization management is not included.
- Billing is not included.
- GitHub Marketplace/OAuth self-service installation is not included.
- Secret vault behavior and credential rotation history UI are not included.
- Multi-user collaborative review workflow is not included.
- Hosted preview readiness is a post-RC confidence layer for a running hosted environment, not a production SaaS claim.
- Live real-repo validation remains operator-guided and provider/network dependent.
- Imported workspaces can still be sparse depending on repository signal quality.
- Semantic drift remains conservative and intentionally narrow.
- Drift is manually evaluated, not a continuous watcher.

## Tag readiness

- Intended tag: `v0.3.0-rc.1`
- Baseline code commit before release-doc updates: `76d63ff`
- Validated release-doc working tree: pre-release validation passed on 2026-04-28 09:29 +08:00.
- Final tag target: the release commit that includes these notes and the archived OpenSpec change.
- Pre-tag condition: no active OpenSpec changes and a clean working tree after the release commit.
- Tag status: not created yet; create only after explicit release confirmation.

Suggested tag commands after the final release commit is created and checked:

```powershell
git rev-parse --short HEAD
git tag v0.3.0-rc.1 HEAD
git push origin v0.3.0-rc.1
```
