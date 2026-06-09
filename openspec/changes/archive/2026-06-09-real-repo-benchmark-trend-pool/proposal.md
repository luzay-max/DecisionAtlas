## Why

DecisionAtlas 已经能运行真实仓库 benchmark、生成 snapshot/comparison，并把 comparison 进入 readiness history。但当前真实仓库验证仍偏一次性和人工选择，缺少固定仓库池与趋势汇总，难以及时发现 release 间质量回退。

## What Changes

- 新增固定真实仓库 benchmark 池配置，定义 repo id、repo 名称、角色、用途、workspace slug、期望用途和 operator setup 状态。
- 新增趋势证据生成器，从 benchmark comparison JSON 和固定仓库池生成 JSON/Markdown 趋势报告。
- 趋势报告应记录 repository coverage、movement counts、regression/operational blocker、not-provided/operator-guided 状态、推荐 follow-up。
- benchmark comparison 和 readiness history 文档需要说明固定仓库池如何用于 release evidence。
- 不要求默认 CI 执行 live imports、GitHub 网络访问、模型调用或已有本地 workspace；默认验证保持离线 deterministic。

## Capabilities

### New Capabilities
- `real-repo-benchmark-trend-pool`: 定义固定真实仓库池、趋势证据、离线验证和 release evidence 接入边界。

### Modified Capabilities
- `lightweight-real-repo-benchmarks`: benchmark 比较报告需要能引用固定仓库池并生成趋势证据。
- `readiness-evidence-history`: readiness history 需要能接收/总结 benchmark trend evidence。

## Impact

- Affected files: `scripts/ci/run_benchmark.py` adjacent tooling, `scripts/ci/` trend evidence script, `docs/project/` benchmark/release/readiness docs.
- Affected tests: 增加趋势池配置、趋势报告生成、非通过状态保留、缺失 comparison 的 pytest 覆盖。
- Affected evidence: 生成 `.tmp/real-repo-benchmark-trend.json/md` 和浏览器审阅证据。
- No database migration, API contract, or live provider dependency is required.
