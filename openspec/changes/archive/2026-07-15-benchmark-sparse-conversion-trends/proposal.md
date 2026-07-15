## Why

DecisionAtlas 已经能够对固定真实仓库生成 benchmark comparison 和 trend movement，但当前证据只回答“仓库整体是否回归”，无法回答 sparse conversion 是否真的变好。没有统一的 normal/sparse attempt、candidate/recovered yield、rejection reason、耗时和 provider mode，release evidence 很容易把一次成功演练误读成持续质量提升。

现在需要把 sparse conversion 从一次性诊断结果变成可重复、可比较、可审计的多仓库趋势证据，同时保留 zero-candidate、provider failure 和 operator-guided 状态，不用平均数掩盖失败。

## What Changes

- Extend live benchmark snapshot rows with bounded sparse-conversion metrics and provider/runtime metadata.
- Define profile-aware expectations for small sparse、medium decision-rich、docs-heavy and stress repositories in the fixed trend pool.
- Compare sparse metrics between baseline and current runs with explicit movement, rejection-reason deltas, and coverage status.
- Extend the coverage rehearsal to generate sparse trend JSON/Markdown and include its status in the release-facing bundle.
- Preserve missing, zero-candidate, provider-failure, product-limited, and operator-guided outcomes as visible non-clean states.
- Add deterministic offline fixtures and focused tests, then validate the same pipeline against fresh public repositories in a real local-stack rehearsal.

## Capabilities

### New Capabilities
- `sparse-conversion-benchmark-trends`: Bounded sparse conversion metrics, profile-aware comparison, and release-safe trend evidence.

### Modified Capabilities
- `real-repo-benchmark-trend-pool`: Add explicit repository profile and sparse-conversion expectation metadata used by comparison and coverage validation.
- `real-repo-benchmark-coverage-rehearsal`: Include sparse metrics in current snapshots, comparisons, trend artifacts, and top-level summaries.
- `release-rehearsal-one-command-evidence`: Preserve sparse trend status and follow-up in the release rehearsal lane when supplied.

## Impact

- `scripts/ci/run_benchmark.py` and `scripts/ci/collect_real_repo_benchmark_trend.py` snapshot and comparison schemas.
- `scripts/ci/rehearse_real_repo_benchmark_coverage.py` and fixed pool data under `examples/live-benchmarks/`.
- Engine import summary serialization where sparse/recovery counters are already produced.
- CI/evidence tests, readiness evidence output, taskbook, update log, and the next-development plan.
- No public API breaking change; all new fields are bounded and optional for legacy snapshots.
