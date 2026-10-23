# 离线决策证据回归：首批实现

基线：包含 PR #19 的 `main@cccdf08`。对应 [PR #11](https://github.com/luzay-max/DecisionAtlas/pull/11) 的 T0–T3 首批基础设施；不是整个计划完成声明。

## 运行

在仓库根目录运行（只依赖 Python 3.11+ 标准库，不需要密钥或网络）：

```sh
python scripts/eval/offline_decision_evidence.py
```

默认生成 `artifacts/offline-evidence/report.json` 和 `report.md`。可通过 `--fixtures` 指定规则用例、`--output` 指定目录。CI 运行相同命令并上传两种报告。退出码：0 表示合成规则预期全部匹配，1 表示预期不匹配，2 表示输入无效。故意构造的负例被正确拦截也属于回归通过；它的证据诊断仍为 `fail`。

## 本批内容

- 新增独立、无副作用的 `app/extractor/evidence.py`。检查必需文本、已知占位句、引用重复、HTTPS URL 格式（包括非法、越界及空端口）、固定 blob SHA、精确 quote / 可选字符区间（零起点、右端不包含）、快照 SHA-256，以及 PR 合并状态。
- 13 个明确标为 synthetic 的规则用例，包含完整引用、伪造引用、错误区间、缺失字段、重复引用、快照不一致和已合并/未合并对照。每条用例记录**完整的逐字段状态及原因预期**；额外增加的成功、失败或缺失检查都会触发回归失败，即使该用例原本就是 `fail`。
- 读取现有[历史审核 JSON](2026-10-21-pallets-click-eight-candidate-independent-audit.json)，复用 `pallets/click@2247b35ea1c47c727d7a06e51fa280e12a863ff6` 的 8 条 FakeProvider 候选字段及源定位，不改写历史记录。7 reject / 1 uncertain 是当时的 AI 辅助初判，单独保留；当前占位字段诊断 8 条均 fail，两者衡量的不是同一事项。
- JSON 包含逐字段 `pass/fail/not_evaluated`、原因、样本数和 provider 分组。Markdown 展示逐条摘要。输出不含运行时间或绝对路径，重复运行稳定。
- 新模块暂未接入生产提取/审核流程，不改变现有候选或 accepted 状态、数据库及 API。

## 解释边界及剩余工作

URL 格式检查不会联网验证可访问性。固定 blob URL 仅验证 URL 与所给 SHA 一致；快照哈希仅检查本地内容完整性，不证明它来自该 URL。精确文字匹配也不证明该文字支持候选结论。PR `merged` 是输入中记录的状态，不会实时查询；合并不等于用户采纳决策。

所有结果均 `automatic_acceptance=false`、`review_required=true`；语义支持恒为 `not_evaluated`。这套规则不能给任意自然语言结论自动判真，未命中已知占位词也不代表内容有效。

历史审核包没有导出精确 SourceRef.quote/span 或完整源正文，本批不补造；引用验证保持 `not_evaluated`。原始完整候选/引用导出、#2559/#2562 的不可变 API 快照与内容证据仍需补齐，因此 **T0–T3 完整验收仍未完成**。#2559 关闭未合并、#2562 已合并的历史观察见原审核 JSON 第 6 项，本批合成合并状态对照不能替代真实来源快照验收。

非作者人工审核（T4）仍为 `not_run`，真实模型准确率为 `not_evaluated`。不会用 FakeProvider 或合成用例通过率冒充真实模型准确率，也不解除企业安全门禁。
