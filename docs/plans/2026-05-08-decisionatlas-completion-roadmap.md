# DecisionAtlas 后续开发路线图

日期：2026-05-08  
目标：说明距离“完整产品”还需要补哪些方向和功能。  
依据：OpenSpec 归档记录、git 历史、README 现状、release checklist、real-repo baseline、hosted preview 文档。

## 现在已经完成什么

DecisionAtlas 已经不是空白项目，也不是单点演示：

- 有 guided demo、real stack、API、web、engine。
- 有候选决策提取、人工审核、accepted decisions、why-search、timeline、drift。
- 有治理 Markdown ingest、diff checker、drift detection、agent guardrail。
- 有真实仓库 benchmark 和 hosted preview readiness 文档。
- 有 canonical release gate 和 OpenSpec 工作流。

所以后续路线不是“继续补 demo”，而是“补完整产品所需的缺口”。

## 距离完整产品还缺什么

### 1. 产品边界还不算完整

当前系统已经接近 v0.3 RC，但离“可以对外长期交付的完整产品”还差这些能力：

- full SaaS org management。
- billing。
- GitHub Marketplace / OAuth self-service 安装。
- secret vault。
- credential rotation history UI。
- 多人协作 review workflow。

这些不是当前主线最优先，但如果目标是完整产品，它们最终都得补。

### 2. 真实仓库闭环还不够稳定

现在已有 imported workspace 和 live benchmark，但仍需要把“导入后能不能真正用起来”做扎实。

还缺的方向：

- imported workspace 的信号质量更稳定。
- why-search 对真实问法的命中更稳。
- drift 的判断更清晰，能区分 evidence-limited、conversion-limited、review_required。
- 再导入同一仓库时，系统要更清楚地提示复用、增量同步、完整重跑。
- benchmark 要从“验证过”变成“持续回归标准”。

### 3. 治理知识层还需继续成熟

治理层已经能 ingest 和审核，但还没有完全成为稳定的项目知识协议。

还缺的方向：

- accepted rule 的版本管理和过期处理。
- decision / standard / postmortem / anti-pattern 的分类一致性。
- source evidence 更标准化。
- 人类决策和 AI 报告之间的闭环更清楚。
- guardrail 仍是 advisory-first，需要更清晰地嵌入开发流程。

### 4. 运营与发布成熟度还不够

当前有 release checklist，但完整产品还需要更高的可恢复性和可说明性。

还缺的方向：

- demo reset / reseed 的稳定性。
- hosted preview 的完整操作手册。
- health / smoke / recovery 的标准化证据链。
- 失败时的恢复路径和排障路径。
- local / hosted / imported 三种运行模式的边界文档。

### 5. 对外信任链还需要补齐

如果希望项目对外更像一个成熟产品，而不只是工程原型，还要补：

- 更完整的 release notes。
- 中英文文档同步。
- 更明确的 limitation disclosure。
- 更清楚的 security / support / operator 边界。
- 面向用户和面向 AI agent 的两套操作说明。

## 后续开发路线

### 第一优先级: 完成核心闭环

目标是让 DecisionAtlas 的核心价值链条真正稳定：

`导入 -> 审核 -> accepted decision -> why-search -> drift -> agent guardrail`

要做的功能：

- 提升 imported workspace 的候选质量。
- 改善 why-search 命中和证据支持。
- 把 drift 信号做得更可解释。
- 固化 benchmark，防止回退。
- 把 guardrail 变成默认开发协议的一部分。

### 第二优先级: 完成治理知识系统

目标是让项目方向、规范、历史决策可以持续变成可复用上下文。

要做的功能：

- rule versioning。
- stale / superseded 标记。
- 更好的 rule provenance。
- rule review UX。
- agent 可调用的治理摘要输出。

### 第三优先级: 完成运营交付能力

目标是让项目能稳定演示、稳定恢复、稳定发版。

要做的功能：

- demo reset / reseed 标准流程。
- hosted preview operator guide。
- recovery drill。
- release checklist 和 validation 报告联动。
- 失败分类和排障文档。

### 第四优先级: 完成平台化能力

目标是把项目从单机型产品推进到可长期运营形态。

要做的功能：

- org / billing / account 管理。
- GitHub Marketplace / OAuth self-service。
- secret management。
- collaboration workflow。
- 更完整的权限与审计。

这部分是“完整产品”里的最后一层，不应早于核心闭环和治理系统。

## 推荐开发顺序

1. 先把核心闭环做稳。
2. 再把治理知识系统做成协议。
3. 再把运营和发布能力标准化。
4. 最后做平台化扩展。

## 暂时不建议优先做的事

- billing 先行。
- 多人协作先于核心闭环。
- 默认 CI 强阻断式治理。
- 大规模 connector 扩张。
- 复杂 SaaS 后台先于 import / why / drift 的质量提升。

## 判断项目是否接近“完整”

如果以下条件同时成立，就可以认为项目已经接近完整产品：

- 新仓库导入后，下一步动作是清晰的。
- why-search 和 drift 在真实仓库上可解释。
- 同一仓库的重复导入行为可控。
- AI agent 能稳定读取治理上下文并按协议暂停。
- demo / hosted preview 可恢复。
- release / README / 中文文档 / limitation disclosure 保持一致。

## 结论

DecisionAtlas 距离“完整项目”还差的不是单一大功能，而是四个收口：

- 核心闭环要更稳。
- 治理知识要更准。
- 运营交付要更可复现。
- 平台能力要最后补齐。

如果要先抓一个主线，应该先抓“真实仓库闭环 + 治理协议落地”，这两项会决定后续所有扩展是否值得做。
