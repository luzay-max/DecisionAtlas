## Why

DecisionAtlas now has a stable offline release gate and stronger imported-workspace readiness, but the optional live real-repository lane is still mostly operator memory plus prose. The next product risk is whether curated public repositories can be revalidated in a repeatable way that records observed outcomes without making flaky provider/network work part of the default CI gate.

## What Changes

- Extend live real-repo validation so it can collect and report dashboard readiness, candidate counts, accepted-baseline state, why status, and drift status for curated public repositories.
- Keep offline fixture validation as the default release gate while making live validation an explicit operator-guided confidence layer.
- Produce a durable live validation report that records each curated repository's observed outcome and bounded interpretation.
- Preserve `browser-use/browser-use` as the known why/drift regression repo and `n8n-io/n8n` as the conversion stress case.
- Avoid exact answer-text assertions; validate broad statuses, citations, counts, and bounded readiness states.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `lightweight-real-repo-benchmarks`: live mode should validate and report observed repo/readiness/why/drift outcomes, not only fixture shape.
- `real-repository-outcomes`: curated public repos should resolve to explicit bounded outcomes such as review-ready, why-ready, evidence-limited, conversion-limited, or operational failure.
- `imported-workspace-readiness-surface`: readiness contracts should remain consistent enough for live validation to compare dashboard/search/readiness behavior across imported workspaces.

## Impact

- Affected code: `scripts/ci/run_benchmark.py`, `examples/live-benchmarks/*`, engine/API endpoints used by live benchmark checks, and any small readiness-reporting helpers needed to avoid duplicated heuristics.
- Affected docs: `docs/project/real-repository-validation-baseline.md`, release/project validation guidance, and a generated or maintained live validation report.
- Dependencies: no new external service dependency in default CI; live mode continues to require an already running local stack, provider configuration, network access, and pre-existing or newly imported workspaces.
- Risk: live validation can be slow or flaky if it tries to own import execution. This change should keep live checks resumable and operator-guided rather than turning them into a hard release gate.
