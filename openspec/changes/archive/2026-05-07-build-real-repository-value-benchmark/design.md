## Context

The repository already contains a lightweight benchmark foundation:

- `examples/live-benchmarks/repositories.json` defines curated repositories and broad expectations.
- `examples/live-benchmarks/why-cases.json` defines focused imported why-search cases.
- `examples/live-benchmarks/drift-cases.json` defines focused drift false-positive cases.
- `scripts/ci/run_benchmark.py` validates fixtures offline and can run live checks against existing imported workspaces.
- `services/engine/tests/evals/test_benchmark_fixtures.py` protects fixture shape and parts of the live report evaluator.

That foundation is useful, but it still mostly answers whether the validation machinery can run. Stage 11 should make the benchmark answer a product question: whether DecisionAtlas creates reviewable, grounded, useful decision memory for real repositories, and where it currently fails.

## Goals / Non-Goals

**Goals:**

- Make the curated repository set self-describing by role and benchmark purpose.
- Produce a value-oriented report that summarizes product usefulness, product limitations, and operational blockers.
- Keep the existing machine-readable JSON report and add an operator-readable Markdown summary.
- Preserve offline fixture validation as deterministic default validation.
- Keep live real-repository benchmark execution explicit and outside default CI.
- Avoid repository-specific product logic or benchmark-only extraction/retrieval behavior.

**Non-Goals:**

- No default CI dependency on GitHub, live providers, or local imported workspaces.
- No hard-coded product special cases for curated repositories.
- No attempt to maximize candidate count as a standalone success metric.
- No new hosted infrastructure or benchmark dashboard.
- No automatic import orchestration for every curated repository in this slice.

## Decisions

1. Treat live benchmark output as value classification, not just pass/fail.

   The report should classify each repository into bounded outcome families such as `useful_now`, `reviewable_but_limited`, `conversion_limited`, `evidence_limited`, `missing_workspace`, and `operational_blocked`. This keeps a poor result useful: it can distinguish product limitation from setup/network/provider failure. The alternative was a binary benchmark pass/fail, but that hides the reason a repository is not useful yet.

2. Keep JSON as the source report and generate Markdown from the same observations.

   The existing runner already writes JSON. The Markdown report should be derived from the same row data so humans can inspect results quickly without introducing a separate interpretation path. The alternative was a manually maintained stage report, but that would drift from the machine-readable evidence.

3. Add repository roles and value expectations to fixtures.

   Each repository should declare why it belongs in the curated set, for example small Python, medium TypeScript, documentation-heavy, issue/PR decision-rich, stress, or regression. This helps later readers understand whether a failure is a broad product weakness or a known stress-case result.

4. Make usefulness metrics broad and bounded.

   Metrics should include import success, artifact and screened-in counts, candidate and accepted counts, strong/partial/thin distribution, provenance and source-ref gaps, why primary-thread match, citation support, and drift false-positive checks. They should not rely on exact generated prose or exact candidate titles except for intentionally focused regression cases.

5. Keep live execution operator-driven.

   The live benchmark should require an already running API and existing imported workspaces. Missing workspaces should be reported explicitly rather than silently importing them or failing as if the product evidence was weak. Automatic import orchestration can be considered later after hosted operator readiness is stronger.

## Risks / Trade-offs

- [Risk] Live benchmark results vary because network, GitHub, provider mode, and local state vary. Mitigation: keep offline validation deterministic and classify live failures as operational when appropriate.
- [Risk] Value labels become subjective. Mitigation: derive them from bounded observations and preserve the raw JSON evidence.
- [Risk] Benchmark pressure encourages repo-specific product logic. Mitigation: keep curated repo identities only in benchmark fixtures and report code.
- [Risk] Markdown and JSON reports diverge. Mitigation: generate both from the same in-memory report structure.
- [Risk] The curated set is too broad for routine local runs. Mitigation: keep live mode explicit and document that it is an operator validation command, not a default release gate.

## Migration Plan

- Update fixture schema additively with repository roles and value expectations.
- Extend benchmark tests to validate the new fields and report classification behavior.
- Extend `run_benchmark.py` to emit the richer JSON and Markdown report.
- Add or update documentation explaining how to run the benchmark and interpret outcome families.
- No database migration is required.

## Resolved Decisions

- Generated live Markdown reports should default to `.tmp/` so they do not become stale committed evidence. Documentation should explain the command and expected report shape instead of checking in a live sample.
- The live runner should support filtering by one or more repository ids so operators can iterate on expensive or flaky repositories without running the full curated set every time.
