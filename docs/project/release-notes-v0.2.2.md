# DecisionAtlas Release Notes: v0.2.2

Status: release-baseline preparation  
Baseline target: current `main` after imported readiness, benchmark, smoke, and bilingual documentation updates

## What changed since v0.2.1

- Imported candidate conversion is stronger:
  - refined imported document family routing
  - bounded recovery extraction for recoverable first-pass failures
  - clearer conversion diagnostics after recovery is exhausted
- Imported workspace readiness is more explicit:
  - candidate-only `review_ready` is distinct from first accepted baseline progress
  - accepted baseline status is surfaced through dashboard/search readiness
  - why readiness is still bounded by question-level grounding
- Imported why-search remains fail-closed:
  - accepted decisions do not automatically upgrade unrelated why answers
  - weak grounding returns `evidence_limited` instead of pretending support exists
  - `limited_support` remains distinct from fully supported `ok`
- Release validation is clearer:
  - `scripts/ci/pre-release.ps1` is the canonical local release gate
  - offline real-repo benchmark fixture validation is part of the default path
  - Playwright smoke coverage matches the current stable guided demo lane
- Documentation is clearer:
  - English and Chinese README/project docs are separated
  - quick start, FAQ, demo script, and release-facing guidance now distinguish guided demo from imported real-repo validation

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

Validation result for this release baseline:

- Passed on 2026-04-24 09:11 +08:00 with exit code `0`.
- Covered `pnpm test`, `pnpm typecheck`, engine pytest (`154 passed`), offline benchmark fixture validation, and Playwright smoke coverage (`1 passed`).
- No release-blocking mismatch was found in the canonical gate.

## Supported scope

- stable seeded guided demo workspace
- public GitHub repository import into imported workspaces
- imported readiness states for review, why, drift, evidence-limited, and conversion-limited outcomes
- candidate review and first accepted baseline workflow
- citation-first why answers with support grading
- chunk-backed supporting evidence behind accepted decisions
- rule-first and conservative semantic drift evaluation
- offline fixture-backed real-repo benchmark validation

## Known limitations

- production auth and multi-user product UI are not implemented
- full GitHub App onboarding is not productized
- private repository productization is not complete
- hosted demo operator flow is still planned
- live real-repo validation remains operator-guided and provider/network dependent
- imported workspaces can still be sparse depending on repository signal quality
- semantic drift remains conservative and intentionally narrow
- drift is manually evaluated, not a continuous watcher

## Tag readiness

- Intended tag: `v0.2.2`
- Current base before release-baseline docs are committed: `main` at `615a4d4`
- Intended tag target: the release commit that includes these v0.2.2 docs, validation evidence, and OpenSpec archival state
- Working tree check before tag prep: only release-facing docs, the next-development plan, and OpenSpec change artifacts are modified or untracked; no application/runtime code changes are included
- Tag status: not created yet; create only after explicit release confirmation

Suggested tag commands after the release commit is created and checked:

```powershell
git rev-parse --short HEAD
git tag v0.2.2 HEAD
git push origin v0.2.2
```
