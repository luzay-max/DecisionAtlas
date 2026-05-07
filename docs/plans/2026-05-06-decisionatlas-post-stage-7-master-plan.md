# DecisionAtlas Post-Stage-7 Master Development Plan

日期：2026-05-06  
当前基线：阶段 7 AI Agent Governance Integration、治理文档同步和真实栈 migration 修复已提交；最新提交基线为 `5447d26 docs: refresh project guidance docs`  
状态：进入阶段 8，重点从“能力已存在”转向“流程稳定、演示可复现、真实价值可度量”

## 当前状态

DecisionAtlas 当前已经完成 v0.3 到 AI-native governance memory 的关键基础层：

- Guided demo 主链路：home、workspace dashboard、review、why-search、timeline、drift。
- Real repository lane：lookup/import、workspace reuse、incremental sync、imported readiness。
- Review / accepted decision baseline：候选决策进入人工审阅，accepted decisions 成为 why-search 和 drift 的 trust anchor。
- Why-search：基于 accepted decisions 和 source refs 做保守、有引用的回答。
- Timeline / drift：围绕 accepted decisions 展示历史记忆和变化信号。
- Auth / owner scope / role gate：本地 bootstrap session、scope surface、admin/reviewer 边界。
- GitHub App / private repo operator path：已有基础绑定和访问源能力。
- Governance Markdown ingest：人类 Markdown 规范、路线、错误总结、人工决策可导入、分类、审核、引用。
- Governance diff checker：当前 git diff 可对照 OpenSpec、roadmap、accepted rules、验证期望输出结构化结果。
- Governance drift detector：长期发现 specs、roadmap、archived changes、accepted rules、postmortems 与当前 diff 之间的漂移。
- AI agent governance guardrail：AI 可调用本地入口，获得 `continue` / `caution` / `pause` 的 advisory summary。

当前不要继续盲目扩功能。下一步主线应是：

```text
让治理能力进入稳定开发流程，让 demo 和真实栈可复现，让真实仓库价值可持续验证。
```

## 总体原则

- 每一刀继续使用 OpenSpec change。
- 治理检查先 advisory，不默认 CI 阻断。
- AI 可以建议和暂停，但不能自动覆盖人类规则。
- 真实仓库价值优先于 SaaS 外壳扩张。
- 先修复可复现性，再做更深自动化。
- 每个阶段都要有明确命令、预期结果和失败处理。

## 阶段 8：Governance Workflow Hardening And Demo Reset Reliability

建议 change：

```text
harden-governance-workflow-and-demo-reset
```

### 目标

把阶段 7 的 agent guardrail 变成日常开发流程中可稳定使用的检查点，并解决真实栈 demo 状态复现问题。

### 为什么现在做

今天的全链路检查显示主链路可用，但 review queue 当前为空，页面提示 seed 演示队列本应有候选。这不是启动故障，而是演示状态已经被先前运行消费。对产品演示来说，这会造成不稳定体验。

同时真实栈 migration 因 Alembic revision ID 超过 32 字符失败，说明本地启动链路还需要更硬的防回归约束。

### 范围

- 增加或整理 demo reset/reseed 脚本，恢复：
  - demo workspace
  - candidate review queue
  - accepted decisions
  - why-search demo answer
  - timeline
  - drift alert
- 更新 real-stack troubleshooting，记录 Alembic revision ID 长度约束。
- 把 agent guardrail 的运行节点写入开发 runbook：
  - implementation 前
  - implementation 后
  - archive 前
  - commit 前
- 增加一个本地状态汇总命令或文档流程，输出：
  - active OpenSpec changes
  - agent guardrail status
  - required validation
  - human decision needed
- 保证 `pause` 仍是人工决策信号，不是自动阻断。

### 验收标准

- 从已运行过的真实栈状态可以恢复到稳定 guided demo。
- `start-real-stack.bat` 在 clean 或已迁移数据库上都能启动。
- migration revision ID 长度测试存在并通过。
- AI/developer 能按文档知道何时运行 `scripts/governance/agent_guardrail.py`。

## 阶段 9：Agent Workflow Integration

建议 change：

```text
integrate-governance-guardrail-into-agent-workflow
```

### 目标

把本地 guardrail 从“可手动运行脚本”推进到“AI agent 工作协议的一部分”。

### 范围

- 定义 Codex / OpenCode / Claude 等 agent 使用 DecisionAtlas governance guardrail 的标准提示和执行协议。
- 产出机器可读和人类可读两种摘要：
  - `agent_status`
  - source-linked evidence
  - required tests
  - human decisions
  - recommended next actions
- 增加 PR / commit message 可复用的 governance summary 格式。
- 让 agent 在 `pause` 时输出明确“需要人决定什么”，而不是继续猜。

### 非目标

- 不直接接 CI hard gate。
- 不做 GitHub App PR bot。
- 不自动写 specs 或 accepted rules。

### 验收标准

- agent 能在一次实现前后稳定调用 guardrail。
- `pause` 场景能给出具体人工决策点。
- `caution` 场景能给出可执行后续动作。

## 阶段 10：Governance Knowledge Quality Loop

建议 change：

```text
improve-governance-knowledge-quality-loop
```

### 目标

提升 Markdown governance documents 到 accepted rules 的质量，让规则既能给人看，也能给 AI 稳定调用。

### 范围

- 改进 rule draft 抽取质量：
  - 降低普通描述被误抽成规则。
  - 更好识别 severity / scope / rationale。
  - 区分 standard、postmortem、decision、anti-pattern。
- Review UI 增加：
  - source excerpt preview
  - accept/reject rationale
  - accepted rule list filtering
  - stale / superseded 标记准备
- 增加 fixture 覆盖 Markdown 标准、错误总结、人工决策。

### 非目标

- 不做完整知识图谱 UI。
- 不自动 accept 规则。
- 不接企业权限。

### 验收标准

- 用户能快速判断一条规则草稿是否值得接受。
- accepted rules 对 diff checker / guardrail 的影响可追溯。
- rejected/pending rules 不会被误当作 authoritative input。

## 阶段 11：Real Repository Value Benchmark

建议 change：

```text
build-real-repository-value-benchmark
```

### 目标

用固定真实仓库集衡量 DecisionAtlas 的核心价值，而不是只靠 demo 感觉。

### 范围

- 定义 curated repo set：
  - 小型 Python repo
  - 中型 TypeScript repo
  - 文档丰富 repo
  - issue/PR 决策明显 repo
- 记录指标：
  - import success
  - artifact count
  - candidate count
  - strong/partial/thin distribution
  - accepted decision baseline quality
  - why-search hit quality
  - drift signal usefulness
- 输出 benchmark report。

### 非目标

- 不把 live benchmark 放入默认 CI。
- 不硬编码仓库特例到产品逻辑。
- 不追求候选数量最大化。

### 验收标准

- 每个 curated repo 有可复查结果。
- 能说明当前版本对真实仓库的价值和限制。
- 后续 extraction / retrieval 优化有量化参照。

## 阶段 12：Hosted Preview And Operator Readiness

建议 change：

```text
prepare-governed-hosted-preview
```

### 目标

把当前本地可用的能力整理成可外部演示、可恢复、边界清楚的 hosted preview。

### 范围

- Hosted preview readiness checklist。
- Demo reset runbook。
- Operator guide：
  - health check
  - reseed
  - governance guardrail smoke
  - known limitations
- 外部演示脚本：
  - guided demo
  - governance markdown ingest
  - agent guardrail summary
  - why-search / drift
- 明确当前不是生产 SaaS：
  - 无 billing
  - 无完整 org admin
  - 无 secret vault
  - governance checker 不默认阻断 CI

### 验收标准

- 外部演示前 10 分钟内可完成 readiness checklist。
- 出现状态污染时能恢复 demo。
- 演示不会误导用户认为这是完整生产 SaaS。

## 阶段 13：Optional Governance Enforcement Preview

建议 change：

```text
prototype-governance-enforcement-preview
```

### 目标

在 advisory guardrail 稳定后，探索“可选 enforcement preview”，但仍不默认阻断主线开发。

### 范围

- 增加 opt-in mode：
  - local strict mode
  - PR annotation mode
  - release checklist warning mode
- 只对明确 blocker / review_required 做强提示。
- 所有 enforcement 结果必须保留 source evidence。

### 非目标

- 不默认启用。
- 不替代 human review。
- 不自动修改代码或规则。

### 验收标准

- 用户能选择是否启用 stricter guardrail。
- 默认开发流程仍保持 advisory。
- false positive 可以被人类决策覆盖并记录。

## 推荐执行顺序

```text
8. harden-governance-workflow-and-demo-reset
9. integrate-governance-guardrail-into-agent-workflow
10. improve-governance-knowledge-quality-loop
11. build-real-repository-value-benchmark
12. prepare-governed-hosted-preview
13. prototype-governance-enforcement-preview
```

## 暂缓事项

短期继续暂缓：

- billing。
- 完整 SaaS 多租户后台。
- GitHub Marketplace 自助安装完整闭环。
- secret vault。
- 多人协作 review workflow。
- 大规模 connector 扩展。
- 默认 CI 阻断式治理 enforcement。

原因：

- 当前最核心的产品差异化是“AI-native project governance memory”，不是 SaaS 外壳。
- 规则质量、demo 可复现性、真实仓库价值验证，比平台扩张更紧急。
- 如果太早做 enforcement 或企业权限，会在规则质量尚未稳定时放大误报成本。

## 当前最近行动建议

下一条最建议启动：

```text
harden-governance-workflow-and-demo-reset
```

理由：

- 今天已确认真实栈能启动、主链路可跑，但 demo review queue 会受历史状态影响。
- 阶段 7 guardrail 已经可调用，但还需要进入稳定开发协议。
- migration revision 长度问题刚暴露，适合纳入阶段 8 的启动硬化。
- 先把“可复现、可恢复、可检查”补齐，再做更深 agent workflow 集成。

## 成功判断

后续成功不看新增页面数量，而看：

- demo 能稳定复现。
- real stack 能稳定启动。
- AI agent 开发前后会运行治理检查。
- `pause` 能清楚告诉人类要决策什么。
- accepted governance rules 对代码变更有真实约束力，但不会误变成黑箱裁判。
- 真实仓库 benchmark 能证明 DecisionAtlas 不是只在 seed demo 中成立。
