# Real Repo Core Loop Quality

日期：2026-07-04

## 目的

本轮 `improve-real-repo-core-loop-quality` 解决的是真实随机仓库 release evidence 里“产品可修 warning 过粗”的问题。

目标不是把 warning 强行变成 pass，而是：

- 修正 release rehearsal 对 benchmark comparison 的误判。
- 给 imported workspace core-loop lane 增加 action category。
- 让 multi-repo diagnosis 区分 product-controlled、operator/setup、external、not-provided、blocking。
- 让 warning-lane reduction 去重 release/full-chain 的聚合 lane，避免重复统计同一个产品问题。

## 本次真实证据

真实仓库：

- `n8n-io/n8n`
- `Textualize/rich`

输出 evidence：

- `.tmp/multi-repo-live-diagnosis.json`
- `.tmp/release-rehearsal-evidence.json`
- `.tmp/full-chain-random-repo-release-rehearsal.json`
- `.tmp/real-external-host-trial-evidence.json`
- `.tmp/random-repo-warning-lane-reduction.json`
- `docs/evidence/readiness/2026-07-04-real-repo-core-loop-quality-smoke/`

## 结果

最新 warning-lane reduction：

- 状态：`warning`
- 阻塞：`0`
- 产品可修：`1`
- 人工/host/聚合上下文：`11`
- 外部依赖：`0`
- 缺失输入：`0`

对比上一轮：

- 上一轮 product-controlled：`3`
- 本轮 product-controlled：`1`

真实改善：

- `benchmark_comparison` 不再因缺顶层 status 被误报为 `unknown`。
- release/full-chain 的 multi-repo 聚合 lane 不再重复统计同一个产品问题。
- 剩余产品问题集中在 `rich` 的 why/drift 核心闭环质量，需要后续单独优化。

## 验证

- `python -m pytest services\engine\tests\ci\test_release_rehearsal_evidence.py services\engine\tests\ci\test_imported_workspace_core_loop.py services\engine\tests\ci\test_multi_repo_live_diagnosis.py services\engine\tests\ci\test_random_repo_warning_lane_reduction.py -q`
- 结果：`22 passed`
- Chrome browser smoke：系统 Chrome 打开 `/`、`/evidence`、`/review`、`/health` 均返回 200。
- Playwright E2E：`team-self-hosted-rehearsal.spec.ts` 1 passed。

## 后续判断

下一步不应该再做“归因层”本身，而应该针对剩余真实产品问题继续做：

- `improve-real-repo-why-drift-grounding`

目标是让 `rich` 的 why answer 和 drift evidence 从 warning 进入可解释的 pass/limited-support 边界。
