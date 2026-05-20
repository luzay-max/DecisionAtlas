# Self-Hosted Delivery Rehearsal Summary

- Entry: `2026-05-20-self-hosted-delivery-rehearsal`
- Version label: `self-hosted-rehearsal-2026-05-20`
- Commit reference: `ab248d9`
- Rehearsal date: `2026-05-20`
- Deployment mode: local/private self-hosted rehearsal
- Overall history status: `warning`

## Scope

This rehearsal validates the self-hosted delivery handoff path using existing DecisionAtlas readiness tooling. It does not validate billing, hosted multi-tenancy, Marketplace or self-service OAuth, hosted secret vault, managed hosted service operations, or runtime license enforcement.

## Environment Findings

| Lane | Status | Evidence |
| --- | --- | --- |
| API health at `http://localhost:3001/health` | `pass` | Returned `ok=true` |
| Web at `http://localhost:3000` | `operator_guided` | Connection refused during probe |
| Engine at `http://localhost:8000/health` | `operator_guided` | Connection refused during probe |
| Seeded demo readiness | `pass` | `.tmp/seeded-demo-readiness.json` |
| Hosted health check | `operator_guided` | Full Web/API/Engine health check requires Web and Engine URLs |
| Hosted guided-demo smoke | `operator_guided` | Requires Web and Engine readiness |
| Reset/reseed recovery drill | `operator_guided` | Not executed during this rehearsal |

## Validation Evidence

| Evidence | Status | Notes |
| --- | --- | --- |
| OpenSpec strict validation | `passed` | `42 passed, 0 failed` |
| Governance guardrail | `passed` | `agent_status=continue`, diff `pass`, drift `clean` |
| Canonical pre-release | `passed` | `.tmp/pre-release-rehearsal-2026-05-20.log`; engine pytest `244 passed`; Playwright smoke `1 passed` |
| Offline benchmark fixture validation | `passed` | Fixture and live benchmark case definitions loaded successfully |
| Release evidence | `warning` | Required gates passed; optional `targeted_tests` evidence was `not_provided` |
| Hosted/operator readiness | `operator_guided` | API and seeded demo passed; Web, Engine, full health, smoke, and recovery remain operator-guided |
| Benchmark comparison | `passed` | `browser-use/browser-use` unchanged, regressions `0`, operational blockers `0` |
| Readiness evidence history | `warning` | This entry preserves `5` operator-guided lanes and `1` not-provided optional input |

## Archived Artifacts

| Artifact | Path |
| --- | --- |
| Entry summary | `docs/evidence/readiness/2026-05-20-self-hosted-delivery-rehearsal/entry.json` |
| Release evidence JSON | `docs/evidence/readiness/2026-05-20-self-hosted-delivery-rehearsal/release_evidence.json` |
| Release evidence Markdown | `docs/evidence/readiness/2026-05-20-self-hosted-delivery-rehearsal/release_evidence.md` |
| Hosted readiness JSON | `docs/evidence/readiness/2026-05-20-self-hosted-delivery-rehearsal/hosted_readiness.json` |
| Hosted readiness Markdown | `docs/evidence/readiness/2026-05-20-self-hosted-delivery-rehearsal/hosted_readiness.md` |
| Benchmark comparison JSON | `docs/evidence/readiness/2026-05-20-self-hosted-delivery-rehearsal/benchmark_comparison.json` |
| Benchmark comparison Markdown | `docs/evidence/readiness/2026-05-20-self-hosted-delivery-rehearsal/benchmark_comparison.md` |
| Code Decision Audit sample | `docs/evidence/readiness/2026-05-20-self-hosted-delivery-rehearsal/code-decision-audit-sample.md` |

## Non-Clean States To Preserve

- `operator_guided`: Web URL, Engine URL, full hosted health check, hosted guided-demo smoke check, reset/reseed recovery drill.
- `not_provided`: optional targeted test summary in release evidence.
- `warning`: release evidence and readiness history overall status because non-clean advisory evidence exists.

## Rerun Conditions

Run the following before claiming a clean customer walkthrough:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/demo/health-check.ps1 `
  -WebBaseUrl http://localhost:3000 `
  -ApiBaseUrl http://localhost:3001 `
  -EngineBaseUrl http://localhost:8000

powershell -NoProfile -ExecutionPolicy Bypass -File scripts/demo/smoke-check.ps1 `
  -WebBaseUrl http://localhost:3000 `
  -ApiBaseUrl http://localhost:3001 `
  -EngineBaseUrl http://localhost:8000
```

If those pass, regenerate hosted readiness evidence and archive a new readiness history entry rather than editing this one into a pass.

## Recommendation

This rehearsal is usable as a self-hosted handoff proof with disclosure. The release baseline, governance guardrail, seeded demo readiness, and benchmark comparison are strong enough to support continued pilot preparation. It is not a clean external walkthrough claim until Web, Engine, full health, smoke, and recovery lanes are rerun and archived.
