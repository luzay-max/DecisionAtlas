# DecisionAtlas v0.3 Hosted Preview Readiness Report

Date: 2026-04-28  
Change: `prepare-v0-3-hosted-preview`  
Baseline commit before hosted-preview docs: `fa94bec` (`Improve real repo decision quality`)  
Branch: `main`  
Validation mode: documentation/checklist readiness plus local command availability; external hosted checks are operator-guided unless a hosted URL is supplied.

## Summary

Status: ready for hosted-preview implementation, with external environment checks still operator-guided.

The current v0.3 RC baseline has deterministic release validation, real-stack validation evidence, hosted operator scripts, private access hardening, GitHub App sync operations, and candidate quality improvements. This report adds the missing hosted-preview layer: a pre-demo checklist, external walkthrough boundary, recovery drill expectations, and explicit classification for unavailable hosted checks.

No new production SaaS claim is made. The stable public walkthrough remains `demo-workspace`; imported real-repository, GitHub App, and private repository lanes are optional operator/admin demonstrations.

## Environment Assumptions

- No external hosted URL was provided in this session.
- Local scripts under `scripts/demo` are the supported operator entrypoints.
- Default release validation remains `scripts/ci/pre-release.ps1`.
- Provider keys, GitHub tokens, webhook secrets, and private repo credentials are backend-only and not required for default CI.
- `main` still has local commits that were not pushed earlier because GitHub was unreachable from this environment.

## Hosted Preview Readiness Matrix

| Lane | Command / action | Observed result | Status | Known limitation | Follow-up |
| --- | --- | --- | --- | --- | --- |
| Baseline | `git rev-parse --short HEAD` | `fa94bec` before hosted-preview docs were added. | pass | Local branch was ahead of origin because GitHub push failed earlier. | Push when network can reach GitHub. |
| Hosted checklist | Created `docs/project/hosted-preview-readiness.md` and Chinese counterpart | Checklist defines required services, environment, validation commands, recovery, walkthrough, and status categories. | pass | Checklist still needs an operator to fill actual hosted URL results. | Use this report as the first readiness record. |
| Guided public lane | Audited home/guided demo copy and demo script | Product and docs already present guided demo as stable seeded lane and advanced/imported lanes as secondary. | pass | None. | Keep this boundary during external walkthrough. |
| Demo scripts | Inspected `health-check.ps1`, `smoke-check.ps1`, `reset-demo.ps1`, `reseed-demo.ps1` | Scripts support explicit hosted URLs or local defaults; reset/reseed require `DATABASE_URL` or `-UseLocalDemoDatabase`; smoke uses `PLAYWRIGHT_SKIP_WEBSERVER=1`. | pass | No external services were available to prove a hosted run in this session. | Run against hosted URLs before public preview. |
| Local health rehearsal | `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\health-check.ps1 -SkipDependencyChecks` | Command executed and failed at web `http://127.0.0.1:3000` because no local web/API/engine stack was running. | known limitation | This confirms command behavior but cannot validate services without a running environment. | Start demo or real stack, then rerun health/smoke. |
| External health | `scripts/demo/health-check.ps1 -WebBaseUrl <hosted> -ApiBaseUrl <hosted-api> -EngineBaseUrl <hosted-engine>` | Not run because no external hosted URLs were supplied. | known limitation | Cannot mark hosted health as passed without a running hosted environment. | Run command with hosted URLs. |
| External smoke | `scripts/demo/smoke-check.ps1 -WebBaseUrl <hosted> -ApiBaseUrl <hosted-api> -EngineBaseUrl <hosted-engine>` | Not run because no external hosted URLs were supplied. | known limitation | Cannot mark hosted smoke as passed without a running hosted environment. | Run command with hosted URLs. |
| Recovery drill | `reset-demo.ps1`; `reseed-demo.ps1`; local rehearsal variants with `-UseLocalDemoDatabase` | Commands are documented; local rehearsal is safe when the local demo database exists. | operator-guided | Not rerun in this session because no running demo stack was declared. | Rehearse immediately before external preview if demo state is uncertain. |
| Release gate separation | Release-facing docs continue to point to `scripts/ci/pre-release.ps1` | Hosted preview checks are documented as post-RC confidence, not a release-gate replacement. | pass | None. | Keep hosted checks out of default CI until deterministic. |
| Optional imported/platform lanes | Hosted readiness docs frame imported repos, GitHub App sync, and private repo access as optional operator/admin lanes | External walkthrough can show them only after explaining provider, credential, and network dependency. | pass | Real credentials and providers are not available in default CI. | Validate manually per operator scope if included in demo. |

## Blocking Assessment

- Blocking product-code issues found: none.
- Blocking documentation issues found: none after adding hosted preview readiness docs.
- Blocking hosted-environment issues found: unknown; no external hosted URL was available.
- Non-blocking limitations: external health/smoke and recovery drills still require an operator-provided running environment; local health rehearsal also needs a running local stack.

## Pre-Demo Rerun Commands

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\health-check.ps1 `
  -WebBaseUrl "https://your-demo.example.com" `
  -ApiBaseUrl "https://your-api.example.com" `
  -EngineBaseUrl "https://your-engine.example.com"

powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\smoke-check.ps1 `
  -WebBaseUrl "https://your-demo.example.com" `
  -ApiBaseUrl "https://your-api.example.com" `
  -EngineBaseUrl "https://your-engine.example.com"
```

If the seeded demo state drifted:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\reset-demo.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\reseed-demo.ps1
```

## Preview Decision

The repository now has the documentation and reporting structure needed to prepare an external hosted preview. Do not claim the hosted preview is fully passed until an operator runs the hosted health and smoke commands against actual hosted URLs and records the result.
