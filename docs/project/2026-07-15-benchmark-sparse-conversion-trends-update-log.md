# 2026-07-15 Benchmark Sparse Conversion Trends Update Log

## 本次目标

把一次性的真实仓库验证升级为可比较的 sparse conversion 趋势证据，记录 normal/sparse 转换、模型尝试、恢复结果、拒绝原因、耗时和 provider mode。

## 实现结果

- `scripts/ci/run_benchmark.py` 新增兼容 schema v2 的 `sparse_conversion` block，并继续读取 schema v1 legacy snapshot。
- comparison 输出 bounded metric delta、yield movement、rejection reason added/removed 和 operational blocker。
- trend pool 增加四种 profile：`small_sparse`、`docs_heavy`、`medium_decision_rich`、`stress`。
- coverage rehearsal、release rehearsal、release evidence、readiness history、team handoff 和 code decision audit 传递 sparse summary。
- 输出 URL、provider label、路径和模型信息均受边界限制，不保存 token、raw model output 或原始私有内容。

## 真实验证

- provider：`openai_compatible` live LLM；embedding：`fake`。
- `drisspg/transformer_nuggets`：small_sparse，sparse recovery 1 次模型尝试，0 recovered，状态 `exhausted`，拒绝 `null_decision`。
- `harbor-framework/terminal-bench-science`：docs_heavy，123 artifacts，29 created candidates，状态 `skipped/candidate_present`。
- `sirkirby/unifi-mcp`：medium_decision_rich，154 artifacts，51 created candidates，状态 `skipped/candidate_present`。
- `LiPu-jpg/Openwrite`：stress，导入成功但无 eligible evidence，状态 `skipped/no_eligible_evidence`，保留 `evidence_limited`。
- live benchmark 4/4 通过；首次固定池比较为 4 条 `newly-evaluated`。
- 本地真实 stack Playwright browser rehearsal 1 passed，覆盖 dashboard、review 条件、Why、Drift、Evidence。

## 回归与交付证据

- focused benchmark/evidence tests：57 passed。
- engine：397 passed；API：32 passed；Web：83 passed。
- typecheck、benchmark fixture CLI、OpenSpec strict 88/88 通过。
- release rehearsal：`warning`，原因是 hosted URL/recovery 仍 `operator_guided`、guardrail 为 `caution`、optional trend comparison 未提供；无 benchmark regression 或 operational blocker。
- readiness history 已归档：`2026-07-15-benchmark-sparse-conversion-live-four-profile-rehearsal`。

## 边界与下一步

本次首次纳入四个新仓库，尚无同池历史 baseline，因此不能宣称质量趋势改善。下一刀进入 `complete-real-customer-host-trial`，优先完成独立 VM/外部服务器上的自托管交付、管理员与团队流程、恢复演练和 operator runbook。
