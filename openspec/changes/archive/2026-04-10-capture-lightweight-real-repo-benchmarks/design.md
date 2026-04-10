## Context

DecisionAtlas has recently shifted from proving the imported-repository lane can work to preserving a release-quality baseline. Several important improvements were validated with real repositories such as `browser-use/browser-use` and `n8n-io/n8n`, but those checks are partly encoded as prose and partly as ad hoc manual smoke tests.

The repository already has:

- `examples/live-benchmarks/repositories.json` for curated repo-level expectations
- `scripts/ci/run_benchmark.py` for fixture validation and optional live why checks
- `docs/project/real-repository-validation-baseline.md` for narrative expectations

This change should connect those pieces into a small fixed benchmark surface, not create a full evaluation platform.

## Goals / Non-Goals

**Goals:**

- Capture a small set of real-repo benchmark cases in fixtures.
- Validate fixture shape in fast CI-safe mode.
- Support optional live benchmark execution against an already-running local stack and already-existing imported workspaces.
- Cover the highest-value regression risks:
  - focused imported why answers stay grounded and cited
  - structured chunk evidence remains useful
  - drift does not reintroduce known false positives
  - conversion-limited imports remain explicitly represented

**Non-Goals:**

- Automatically importing large public repositories in CI.
- Building a scoring dashboard or benchmark service.
- Calling live LLM providers during default benchmark validation.
- Replacing unit or e2e tests.
- Turning benchmark failures into absolute product-quality claims across arbitrary repositories.

## Decisions

### Keep the benchmark fixture-based

The benchmark should live in `examples/live-benchmarks/` as explicit JSON fixtures rather than being inferred from docs or database state.

Rationale:

- fixtures are reviewable in git
- expectations can stay small and intentional
- CI can validate shape without network access

Alternative considered: encode all expectations only in markdown. That is useful for explanation but too easy to drift away from runnable validation.

### Separate repo-level expectations from case-level expectations

Repository entries should continue to describe broad import/readiness expectations, while new case fixtures should describe focused why and drift checks.

Rationale:

- repo-level outcomes and why/drift cases have different lifecycles
- `n8n` conversion-limited behavior is not the same kind of check as a `browser-use` why question
- case-level checks can be added gradually without rewriting repo-level baselines

### Default validation stays offline and fast

`run_benchmark.py` should validate fixture schema by default. Optional live checks can require flags and a running local API.

Rationale:

- pre-release should remain reliable
- CI should not depend on GitHub, live providers, or local imported workspace state
- live validation is still useful for manual release smoke

### Use bounded outcome labels instead of brittle exact-answer matching

Live why checks should assert status, minimum citations, and a small set of expected terms. Drift checks should assert broad alert categories or absence of known noisy strong signals.

Rationale:

- exact prose can legitimately change
- citation count and key terms better reflect the user-visible contract
- drift semantics are intentionally conservative, so the benchmark should protect broad behavior, not exact card wording

## Risks / Trade-offs

- Fixture drift → Keep the fixture set small and update it only when a product contract changes.
- False confidence → Treat the benchmark as a release smoke aid, not as complete quality measurement.
- Live benchmark flakiness → Keep live execution optional and require pre-existing workspaces rather than importing during the benchmark.
- Overfitting to `browser-use` → Include a mix of strong, sparse, and conversion-limited repositories, but keep the first implementation small.
