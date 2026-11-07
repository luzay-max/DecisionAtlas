# DecisionAtlas · GitHub 开源框架借鉴与证据优先改进计划表

> **日期**：2026-10-22  
> **状态**：PROPOSED / Ready for review（本文为计划，不代表已实施）  
> **初始基线**：`main@93bbacd378a8d24e1230d70d3cde3e3a7c719a06`；**同步主线**：`main@9bc32ce739db0bebeaeb928c6fc979dca34fe005`；[合并后主线 CI #39728035244](https://github.com/luzay-max/DecisionAtlas/actions/runs/39728035244) 已通过。  
> **方向**：现有自托管技术栈不重写；先修复证据可信度和评价门禁，再验证时序关系、检索和代码影响。  
> **边界**：本 PR **仅新增规划文档**。不安装框架、不改生产逻辑、不上传私有代码/Token、不调用付费 AI、不部署、不合并。

## 1. 为什么先做证据评测，而不是直接引入新框架

现有实现已经具备：
- Next.js 15 / React 19 前端，Fastify API，FastAPI + SQLAlchemy Engine。
- `services/engine/app/extractor/parser.py` 中的候选 JSON 字段归一化，`pipeline.py` 中的候选提取与 SourceRef 持久化。
- `services/engine/app/retrieval/hybrid.py` 中的全文 + 向量加权检索，`retrieval/answering.py` 中的证据引用及回答构造。
- 人工审核、Why Search、Drift、演示截图 CI 和基础安全控制。

仍有**质量证明缺口**：2026-10-21 对 `pallets/click` 的 8 条 **FakeProvider** 候选做了 AI 助手证据核查，结果为 **0 接受、7 拒绝、1 不确定**。8/8 URL 能访问，但固定占位 `problem/chosen_option/tradeoffs` 不足以说明工程决策。此结果**不是非作者人类验收，也不是 DeepSeek 或其他真实 LLM 的准确率**。参见[审核报告](../validation/2026-10-21-pallets-click-eight-candidate-independent-audit.md)。

因此应先建立一个确定性、离线、可解释的评测基线，解决“证据 URL 存在，却不支持决策结论”的问题。现有真实仓库来源与 Mock/Fake 提取必须分别统计。

## 2. 框架学习与采用决策

| GitHub 项目 | 优先级 | 借鉴点 | 首轮采用方式 | 暂不做的事情 |
| --- | --- | --- | --- | --- |
| [DeepEval](https://github.com/confident-ai/deepeval) / [promptfoo](https://github.com/promptfoo/promptfoo) | P0 | 测试用例、失败原因、回归门禁、评测报告 | 学习评测流程；先自建**离线规则**与人工标注格式 | 不引入自动 LLM Judge，不无授权发送提示词或源码 |
| [Pydantic AI](https://github.com/pydantic/pydantic-ai) | P0 | 类型化结构化输出、错误处理、边界约束 | 强化现有解析后的**语义字段验证** | 不替换既有 `OpenAICompatibleProvider`，不接入复杂 Agent |
| [Graphiti](https://github.com/getzep/graphiti) | P1 | 时间有效性、被替代关系、溯源 | 先用当前 SQLAlchemy 建小型关系原型 | 暂不部署 Neo4j 或迁移数据库 |
| [LightRAG](https://github.com/HKUDS/LightRAG) | P1 | 多路检索、关系辅助召回、增量一致性 | 与现有 `hybrid_search` 做受控对照 | 不整体替换索引和向量库 |
| [GitNexus](https://github.com/abhigyanpatwari/GitNexus) | P2 | 代码符号、依赖/影响关系 | 研究 Tree-sitter/AST 小范围 PoC | 不直接引入整套服务、MCP 或不明确的依赖许可 |
| [TanStack Query](https://github.com/TanStack/query) / [shadcn/ui](https://github.com/shadcn-ui/ui) | P2 | 请求状态、一致交互、可访问组件 | 仅在高频页面出现实际问题时局部验证 | 不再次进行无收益的全站 UI 重写 |
| [DSPy](https://github.com/stanfordnlp/dspy) | 研究预留 | 基于标注集的 prompt/program 优化 | 待人工金标准存在后再设计成本受限的独立实验 | 不自动触发付费优化或多模型评审 |
| [Microsoft GraphRAG](https://github.com/microsoft/graphrag) / [LangGraph](https://github.com/langchain-ai/langgraph) | 暂缓 | 图谱检索/复杂流程编排 | 阅读设计，不进入近期交付范围 | 不因流行而提高索引成本或重构稳定链路 |

> 引入任何实际第三方依赖前，单独核查**固定版本、维护状态、许可证、安装体积、隐私与自托管开销**；“值得学”不等于“建议安装”。

## 3. 可执行计划表（按依赖顺序，不是固定日历承诺）

| ID | 优先 | 预计工作量* | 交付任务 | 主要落点（拟） | 明确验收证据 | 前置/状态 |
| --- | --- | --- | --- | --- | --- | --- |
| T0 | P0 | 0.5 天 | 冻结评测口径与输入集：固定 `pallets/click` SHA、审阅来源类型与原始 JSON | `docs/validation/`、`tests/fixtures/` | fixture 附 SHA、来源 URL、Fake/real 标签、标注人状态；无私有数据 | 待实施 |
| T1 | P0 | 1–2 天 | 构建正负合成样本与真实来源观察集，收录 #2559 未合并、#2562 已合并对照 | `services/engine/tests/fixtures/` | 有可复现的 accepted/rejected/uncertain 合成样本；8 条原始候选保留“AI 辅助初判”标签而非人类金标准 | T0 / 待实施 |
| T2 | P0 | 2–3 天 | 离线证据门禁：占位字段、缺少必需字段、来源引用/精确片段、重复引用、PR 状态校验 | `extractor/parser.py` 周边新校验模块和测试 | 对占位候选拒绝“已证实”；未合并提案不能因 URL 可访问被自动采纳；无法证明语义支持时返回 **uncertain/review_required** | T1 / 待实施 |
| T3 | P0 | 1–2 天 | 输出逐条 JSON + Markdown 回归报告，记录 `pass/fail/not_evaluated`、理由和样本分母 | `scripts/eval/`、`docs/validation/` | 同一 fixture 重跑结果稳定；CI 不需要 API Key 和外网 LLM；失败用非零退出码 | T2 / 待实施 |
| T4 | P0 | 1–2 天 | 增加独立人工复核表；隔离 AI 助手初判与最终人工标注 | `docs/validation/` | 可由非作者填写 decision quality、quote validity、accepted-state evidence 与 reviewer/time；无人签名保持 `not_run` | T1 / 待实施 |
| T5 | P1 | 2–3 天 | 结构化提取语义规则：已合并 ≠ 方案自动被人类采纳；拒绝/不确定理由可审计 | Engine 提取与审核边界 | 负例不误转 trusted；不改变现有对外状态语义，变更伴随迁移/兼容测试 | T2–T4 / 待实施 |
| T6 | P1 | 3–5 天 | 时间关系原型：`supersedes` / `supported_by` / `impacts` 和有效时间 | SQLAlchemy / Timeline / Drift | 旧决策保留历史、被替代后默认检索不误当现行；迁移与逆向兼容可测 | T5 / 待实施 |
| T7 | P1 | 2–4 天 | LightRAG 式检索**对照实验**：现有 hybrid vs 引用优先/关系增强候选 | `retrieval/hybrid.py` 附近独立试验代码 | 同一查询集报告覆盖率、可信引用率、拒答率、p50/p95 延迟；无证据不硬编 | T3–T4 / 待实施 |
| T8 | P2 | 3–5 天 | GitNexus 思路代码影响小试点：选定语言 + 1 个公开仓库 | 独立只读 AST 原型 | 代码符号/文件影响有固定 SHA 可追溯，误关联可识别；不开全仓实时索引 | T3、T6 / 待评估 |
| T9 | P2 | 1–3 天 | 高价值 UI 局部反馈改进：证据级别、源链接、失败恢复 | Review / Search 页面 | 浏览器交互和截图验证，移动端/无障碍无回归；仅修真实观察到的问题 | T3 / 待评估 |
| T10 | P2 | 研究任务 | DSPy 等真实模型优化实验设计 | 实验方案，不改默认流程 | 明确模型、单次最大请求数、成本上限、人工标签与退出条件；**单独审批后才可运行** | T4 / 未授权 |

\* 工作量为**单人纯工程工时的粗略估计**，不包括 CI 排队、真人审核、真实模型预算或生产部署，不代表完成承诺。所有任务都应拆成小型独立 PR；**本计划 PR 不交付 T0–T10 的实现**。

## 4. 第一实施 PR（T0–T3）的详细验收清单

- [ ] 固定无密钥、无付费网络请求的评测入口（例如 `python scripts/eval/offline_decision_evidence.py --fixtures ... --output ...`；文件名为拟议）。
- [ ] `FakeProvider` 结果明确标为 `provider_kind=fake`，不可与 live LLM 结果汇总成模型“准确率”。
- [ ] 所有引用必须关联不可变来源定位（固定 Git SHA/PR 编号、URL、可验证 quote/span）；原始审核包缺少精确 span 时明确 `not_evaluated`，不补造 span。
- [ ] 逐字段检测占位内容/空问题/空选择；`problem/chosen_option/tradeoffs` 任一失真都不得“自动接受”。
- [ ] `pallets/click#2559` 的关闭未合并状态与 `#2562` 的已合并状态可区分；**merged 仅代表源码合并，不代表用户已完成决策人工审核**。
- [ ] 规则不能单靠关键字重合认定“证据支持选择方案”；不能自动判断的语义对应标 `review_required`，等待人类核验。
- [ ] 报告有字段级判定、错误类别、样本数与分母，支持 `pass/fail/unknown/not_run`，禁止无标注样本计算虚假准确率。
- [ ] 合成正负样本及真实公开来源观察集均有重复运行测试；不存在实际 API Key 依赖。
- [ ] 最新提交的完整现有 CI 通过；新增离线评估在 Windows/GitHub Actions 可重复运行。
- [ ] 任何人类标注门禁必须由真实复核人员提交证据；AI 助手审核可作参考，不冒称独立人类签名。

## 5. 测量口径与退出条件

| 指标 | 分子 / 分母 | 当前情况 | P0 目标 |
| --- | --- | --- | --- |
| 来源存在率 | 可访问来源 URL 数 / 抽查 URL 总数 | 旧包 8/8 可打开；**不代表引用支持内容** | 明确区分 URL、固定 SHA、quote/span 三层验证 |
| 字段完整性 | 合格字段完整候选 / 实际候选 | 旧包 0/8 可被当作完整决策资产 | 合成负例全部被门禁拦截；真实集先报告不评假成功 |
| 引用位置验证率 | 引用定位可核实数 / 引用待核实总数 | 旧审核包未导出完整 source span，不能计算 | 自动校验可得数据，缺失数据显式 `not_evaluated` |
| 采纳状态误判 | 被错误归为已采纳的已知负例数 | 无严谨基线 | 已知负例 **0 误采纳**（仅限定义好的测试集） |
| 人工一致性 | 同一候选两名独立复核者一致数 / 双审样本数 | 未运行 | 建立可填写模板；出现分歧保留 `uncertain`，不臆测准确率 |
| Why / Drift 质量 | 真实问题正确且可引用数 / 人工标注问题数 | 尚未人工验证 | 仅在 T4 人工金标准完成后另行设通过阈值 |

**Go（进入 P1）**：T0–T4 完成；新增离线 CI 绿；已知占位与未合并源负例全部被拒绝自动采纳；报告无伪造分母，且人工标注状态清晰。  
**Caution**：离线规则通过但独立人类复核尚未完成——可以继续安全性/性能开发，**不得宣称真实模型准确率或客户可用性已达标**。  
**No-go**：引用伪造、跨 workspace 误用、无法说明采纳状态、CI 依赖付费模型或把 `not_run` 输出成 `pass`。

## 6. 推进节奏（建议，而非排期承诺）

| 波次 | 工作包 | 交付检查点 | 进入下一波的条件 |
| --- | --- | --- | --- |
| **W1 · 可信基线** | T0–T1 | 可追溯公开样本、离线正负例、明确标注人状态 | 来源及字段定义冻结 |
| **W2 · 自动门禁** | T2–T3 | 确定性证据核查、CI JSON/Markdown 报告 | 已知负例不被自动接受 |
| **W3 · 人工复核** | T4–T5 | 非作者复核模板与语义校验设计 | 标注缺口与争议被明确记录 |
| **W4+ · 按收益选择** | T6–T9 | 时序、检索对照、代码影响或 UI 的小型 PoC | 前一阶段质量收益可证明；不强推全部项目 |

## 7. 风险与变更控制

1. **数据安全**：所有 CI fixture 只能来自公开仓库或合成示例，严禁把私有源码、GitHub Token、Cookie、个人账户信息提交到公共仓库或上传 Artifact。
2. **费用控制**：默认免费、离线；`DeepEval` 的 LLM Judge、DSPy 自动优化、DeepSeek 等真实模型请求，必须先由维护者明确批准供应商、费用上限、调用次数与 Key 管理方式。
3. **技术负担**：优先借鉴实现方法，避免整套安装 Graphiti/GraphRAG/LangGraph 或增加独立图数据库；如 PoC 有收益再单独提出迁移 RFC。
4. **兼容性**：不破坏既有 `SourceRef`、审核状态、owner scope、安全迁移与旧数据读取路径；新语义必须有迁移或兼容测试。
5. **人工验收**：无需支付的 AI 规则可以辅助初审，但不替代人的“这是真实已采纳工程决定”的签字判断。
6. **管理方式**：每波独立小 PR，附 before/after 指标、CI 链接和可回滚说明；未经明确批准不合并或部署。

## 8. 下一步建议

**紧接此计划 PR 的第一个代码 PR：只实施 T0–T3 的离线证据评估基础。** 它应以 `pallets/click` 的 FakeProvider 审核包和 #2559/#2562 对照为固定回归材料，不引入付费 AI 或新图谱框架。待该评估可信，再考虑时序关系、混合检索和代码影响链路。

参考材料：
- [2026-10-21 安全收口与真实仓库验证计划](2026-10-21-security-hardening-and-real-repo-validation-plan.md)
- [2026-10-21 八条公开候选核查](../validation/2026-10-21-pallets-click-eight-candidate-independent-audit.md)
- [DecisionAtlas DeepSeek 免费模拟说明](../validation/2026-10-21-deepseek-adapter-dry-run.md)
