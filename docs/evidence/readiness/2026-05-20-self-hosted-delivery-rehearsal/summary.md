# Self-Hosted Delivery Rehearsal Summary

- Entry: `2026-05-20-self-hosted-delivery-rehearsal`
- Version label: `self-hosted-rehearsal-2026-05-20`
- Commit reference: `ab248d9`
- Rehearsal date: `2026-05-20`
- Deployment mode: local/private self-hosted rehearsal
- Overall history status: `passed`

## Scope

This rehearsal validates the self-hosted delivery handoff path using existing DecisionAtlas readiness tooling. It does not validate billing, hosted multi-tenancy, Marketplace or self-service OAuth, hosted secret vault, managed hosted service operations, or runtime license enforcement.

## Environment Findings

| Lane | Status | Evidence |
| --- | --- | --- |
| API health at `http://localhost:3001/health` | `pass` | Returned `ok=true` |
| Web at `http://localhost:3000` | `pass` | `scripts/demo/health-check.ps1` |
| Engine at `http://localhost:8000/health` | `pass` | `scripts/demo/health-check.ps1` |
| Seeded demo readiness | `pass` | `.tmp/seeded-demo-readiness.json` |
| Hosted health check | `pass` | Web/API/Engine all reachable |
| Hosted guided-demo smoke | `pass` | Playwright demo smoke `1 passed` |
| Reset/reseed recovery drill | `operator_guided` | Not executed during this rehearsal |

## Validation Evidence

| Evidence | Status | Notes |
| --- | --- | --- |
| OpenSpec strict validation | `passed` | `42 passed, 0 failed` |
| Governance guardrail | `passed` | `agent_status=continue`, diff `pass`, drift `clean` |
| Canonical pre-release | `passed` | `.tmp/pre-release-rehearsal-2026-05-20.log`; engine pytest `244 passed`; Playwright smoke `1 passed` |
| Offline benchmark fixture validation | `passed` | Fixture and live benchmark case definitions loaded successfully |
| Release evidence | `passed` | Required gates and advisory evidence passed |
| Hosted/operator readiness | `pass` | Web, API, Engine, full health, smoke, and seeded demo readiness passed |
| Benchmark comparison | `passed` | `browser-use/browser-use` unchanged, regressions `0`, operational blockers `0` |
| Readiness evidence history | `passed` | This entry preserves `1` operator-guided non-required lane |

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

- `operator_guided`: reset/reseed recovery drill.
- `not_provided`: none in the archived release evidence.
- `warning`: none in the archived release evidence or readiness history entry.

## Rerun Conditions

Run the following when rechecking customer walkthrough readiness:

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

If these checks regress or recovery is rehearsed, regenerate hosted readiness evidence and archive a new readiness history entry rather than editing this entry manually.

## Recommendation

This rehearsal is usable as a self-hosted handoff proof with disclosure. The release baseline, governance guardrail, seeded demo readiness, hosted health, hosted smoke, and benchmark comparison support continued pilot preparation. The only remaining non-clean lane is the non-required reset/reseed recovery drill, which should be rehearsed before a stronger enterprise handoff claim.
