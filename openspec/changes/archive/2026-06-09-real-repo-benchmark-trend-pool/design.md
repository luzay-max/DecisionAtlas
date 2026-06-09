## Context

DecisionAtlas already has three related pieces:

- `examples/live-benchmarks/repositories.json` defines real public repositories used by live benchmark validation.
- `scripts/ci/run_benchmark.py` can turn live reports into compact snapshots and compare snapshots.
- `scripts/ci/collect_readiness_evidence_history.py` can archive release, hosted, and benchmark comparison evidence into durable history.

The missing layer is a stable release-facing repository pool and a compact trend report that explains whether each expected real repository is represented in the latest comparison. Without that layer, a comparison can be technically valid while silently omitting important repos, and operators must manually infer whether regressions are product issues, operational blockers, or missing evidence.

## Goals / Non-Goals

**Goals:**

- Define a fixed real repository trend pool that is safe to keep in source control and does not contain private repository content or secrets.
- Generate JSON and Markdown trend evidence from a benchmark comparison JSON plus the fixed pool.
- Preserve non-clean states such as `regressed`, `operationally-blocked`, `missing-from-current`, `not_provided`, and `operator_guided`.
- Make the trend evidence usable in team handoff and readiness/release discussions.
- Keep default CI deterministic and offline.

**Non-Goals:**

- Do not run live GitHub imports by default.
- Do not call model providers, GitHub APIs, or private repositories during default validation.
- Do not replace the existing snapshot/comparison format.
- Do not make benchmark regressions hard blocking by default; the report surfaces them as release warnings for operator decision.

## Decisions

1. Add a separate fixed pool file instead of overloading `examples/live-benchmarks/repositories.json`.

   The live benchmark repository file is execution-oriented and includes broad expectations for live API validation. The trend pool is release-evidence-oriented: it records stable coverage expectations, release role, priority, and operator setup status. Keeping them separate avoids coupling live import mechanics to release trend reporting.

2. Add a new adjacent CI script instead of expanding `run_benchmark.py`.

   `run_benchmark.py` already validates fixtures, runs live checks, writes snapshots, and compares snapshots. Trend-pool coverage is a second-stage evidence summarizer. A dedicated `collect_real_repo_benchmark_trend.py` keeps responsibility narrow and makes tests easier to reason about.

3. Treat missing comparison input as evidence, not as a script crash.

   Release rehearsals sometimes run without a fresh benchmark comparison. The script should still generate JSON/Markdown with status `warning` and `not_provided` rows so the absence is visible in release evidence instead of hidden in `.tmp` state or CLI logs.

4. Preserve movement labels from the comparison rather than remapping them into generic pass/fail.

   Operators need to distinguish product regressions, operational blockers, missing current rows, product-limited outcomes, and unchanged repos. The trend report will include an overall status, but row-level movement remains the source of truth.

5. Integrate trend evidence into team handoff as an optional source.

   Handoff reports already summarize release, hosted, benchmark comparison, readiness history, package, license, import, and audit evidence. Adding benchmark trend as an optional section makes customer/operator handoff reflect fixed-pool coverage without changing existing required inputs.

## Risks / Trade-offs

- Fixed pool becomes stale -> include owner/purpose/priority/operator setup status and document review during release rehearsal.
- Comparison row IDs drift from pool IDs -> report `missing_from_current_pool` and warn instead of silently passing.
- Operators interpret warnings as blockers -> Markdown will separate warning status from explicit recommended follow-up.
- Duplicate evidence families confuse release flow -> trend evidence complements, but does not replace, benchmark comparison.

## Migration Plan

1. Add the fixed pool file and trend collector.
2. Add unit tests for clean, missing, and regressed/operationally-blocked inputs.
3. Add optional handoff summarization for benchmark trend evidence.
4. Generate `.tmp/real-repo-benchmark-trend.json` and `.tmp/real-repo-benchmark-trend.md` from current comparison evidence.
5. Archive the OpenSpec change after tests and validation pass.
