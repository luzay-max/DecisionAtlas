# 2026-07-13 Sparse Repository Decision Conversion Update

## 目标

在不降低 source quote、source ref、confidence 和人工审阅门槛的前提下，提高 sparse real repository 从导入 artifact 到 review candidate 的转换可观测性与有界恢复能力。

## 实现

- Candidate extraction 增加 zero-candidate sparse recovery，仅在正常 extraction 没有创建 candidate 时触发。
- recovery 从未完成 full extraction、没有既有 source ref 的高信号 artifact 中确定性选择。
- 最多选择 4 个 artifact，并优先覆盖不同 extraction family。
- recovered 输出复用原有 parser、grounded quote、source-ref、confidence 和 `candidate` review state。
- provider timeout、400、invalid JSON、missing fields、ungrounded quote 和 `null_decision` 均作为非致命 reason 保存。
- import summary、fresh rehearsal 和 readiness history 增加 sparse status、skip reason、attempts、families、rejections 与 recovered count。
- 正常 extraction 已产生 candidate 时返回 `skipped/candidate_present`，不会增加额外模型调用。

## 自动化验证

- extractor + import + fresh evidence + readiness integration：49 passed。
- 完整 engine pytest：376 passed。
- OpenSpec strict：85/85。
- 新覆盖包括 grounded recovery、已有 candidate 跳过、disabled budget、no eligible evidence、family-diverse budget、null、ungrounded quote 和 provider timeout。

## 真实模型与仓库验证

运行环境：

- `LLM_PROVIDER_MODE=openai_compatible`
- `LLM_MODEL=deepseek-v4-pro`
- API key 仅保存在被 Git 忽略的本地 `.env`，未进入证据或提交。

Fresh 随机仓库：

- 候选池：`jazzband/pip-tools`、`hynek/structlog`，两者预检均 `workspace_exists=false`。
- 固定随机种子：`20260713-sparse-01`。
- 选中：`jazzband/pip-tools`。
- fresh job：`bced56f9-a8da-418a-bc43-36c0fc39e061`。
- 导入：1207 artifacts。
- 模型调用证据：80 screening；49 completed extraction；36 screened-in；13 normal recovery。
- 结果：28 grounded candidates。正常阶段已有 candidate，因此 sparse lane 为 `skipped/candidate_present`，0 sparse model attempts。
- 人工接受：`Remove support for Python 3.8`，accepted baseline 从 0 提升到 1。
- Why Search：pass，2 citations，引用 GitHub PR #2279。
- Drift：重新评估后 clean，0 alerts。

Sparse 分支补充验证：

- workspace：`github-python-trio-sniffio`。
- incremental reanalysis job：`80feea76-2a28-4193-8e2e-1352b4d58965`。
- 正常 screening：4/4 screened-out，0 candidate。
- sparse recovery：4 eligible、4 model attempts、4 `null_decision`、0 recovered candidate。
- job 保持 succeeded，outcome 为 `insufficient_evidence`，没有制造无依据 candidate。

## Chrome 人类流程

- 打开 fresh pip-tools dashboard。
- 进入 Review，检查多条 grounded refs、provenance、问题、选择和权衡。
- 手动接受一条候选。
- 提交 Why Search 问题并验证 2 条引用。
- 运行 Drift，验证 clean / 0 alerts。
- 使用 DOM-CUA 电脑式点击返回 dashboard。
- 浏览器日志只有 React DevTools/Fast Refresh 信息，无 error。

## 证据

`docs/evidence/readiness/2026-07-13-sparse-repo-decision-conversion-rehearsal/`

该目录包含 readiness entry、fresh rehearsal、conversion comparison、sniffio sparse job、post-review core loop 和 Chrome screenshots。

## 结论与边界

- 相比 sniffio fresh baseline，candidate delta 为 +28，accepted delta 为 +1，Why 从 evidence-limited 变为 pass。
- 这不是受控因果实验，因为两个 repository profile 不同。
- pip-tools 的 28 candidates 全部经过 parser salvage，页面顶部候选置信度为 0.55；数量提升同时带来了审阅负担，下一步必须优化 candidate precision/ranking。
- dashboard 显示大量重复 `repeated_postmortem_issue` finding，属于新的 P0 交互与治理噪声问题。
- readiness 仍为 warning、0 blockers；外部客户主机证据仍未由真实非本人环境替换。
