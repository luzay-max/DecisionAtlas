# DecisionAtlas 下一阶段总计划

日期：2026-04-29  
当前基线：阶段 7 AI Agent Governance Integration 完成后的本地工作区（上一提交基线 `main` @ `dc8e00c`，阶段 7 待提交）  
状态：v0.3 RC 已封存，阶段 4 Markdown Governance Ingest MVP、阶段 5 Governance Diff Checker、阶段 6 Governance Drift Detection、阶段 7 AI Agent Governance Integration 均已完成；阶段 8 为下一阶段

## 当前状态判断

DecisionAtlas 已经完成从 demo hardening 到 v0.3 平台化基线的主要推进，并已经完成阶段 0、阶段 1、阶段 2、阶段 3、阶段 4、阶段 5、阶段 6、阶段 7 的计划实施。

当前已成立的能力包括：

- guided demo 主链路：dashboard、review、why-search、timeline、drift。
- 真实仓库导入与 imported workspace readiness。
- 候选决策提取、人工 review、accepted decision 基线。
- why-search 基于 accepted decisions 和 source refs 做保守回答。
- timeline 和 drift 围绕 accepted decisions 展示历史和变化信号。
- login、local bootstrap session、owner scope、role gate。
- GitHub App installation / sync operation 的 operator/admin 基础。
- private repo token-backed access 的 operator/admin 基础。
- hosted preview readiness、real stack validation、release notes、quick start、operator guide 等文档基线。

当前 OpenSpec 状态：

```text
active changes: 0 after archiving integrate-ai-agent-governance-guardrails
```

当前 Git 状态：

```text
main has stage 4, stage 5, and stage 6 governance work committed locally; stage 7 governance guardrail work is implemented and archived in the working tree
latest committed baseline: dc8e00c feat: add governance drift detection
local branch state: main...origin/main [ahead 3]
release tag: v0.3.0-rc.1 exists locally
```

关键缺口：

- 真实 Postgres/Redis stack 和外部 hosted preview 仍需要在具备环境时重跑确认。
- 真实仓库决策质量和 why-search 检索质量已经完成一轮收紧，但仍需要继续通过真实仓库验证效果。
- Workspace 复用与增量同步已完成产品化：重复仓库分析会先暴露已有 workspace、增量同步、完整重跑和 active import 状态。
- AI governance knowledge layer 的阶段 4 第一刀已经完成：Markdown 治理知识层已具备可导入、可分类、可审核、可引用的 accepted rules 基础。
- 阶段 5 Governance Diff Checker 已完成：当前 git diff 可以对照 OpenSpec、roadmap、main specs、accepted governance rules 和验证期望输出保守、可解释、机器可读的治理检查结果；默认仍是 advisory，不做 CI 阻断或自动改写规则。
- 阶段 6 Governance Drift Detection 已完成：系统已具备本地 governance drift report，可跨 roadmap、main specs、archived changes、accepted rules、update logs、postmortems 和当前 diff 输出 `clean` / `watch` / `drift_detected` / `review_required` 的长期治理漂移信号。
- 阶段 7 AI Agent Governance Integration 已完成：系统已具备 `scripts/governance/agent_guardrail.py` 本地入口，可把 diff check 与 drift report 聚合成 `continue` / `caution` / `pause` 的 agent-facing advisory summary。

因此，下一阶段不应继续零散加功能。主线应从：

```text
v0.3 平台化能力补齐
```

切换到：

```text
v0.3 RC 封存 + v0.4 产品价值深化
```

阶段 3 已完成：已有 lookup / import job / sync provenance / imported readiness 能力已经被产品化为明确的重复仓库分析入口。阶段 4 也已完成：Markdown Governance Ingest MVP 已经启动 AI 可调用治理知识层的第一刀。阶段 5 已完成：Governance Diff Checker 已能让当前 git diff 对照 OpenSpec、roadmap、accepted governance rules 和历史错误总结输出保守、可解释的治理检查结果。阶段 6 已完成：Governance Drift Detection 已能发现项目方向、规范和历史人工决策之间的长期漂移。阶段 7 已完成：阶段 5/6 的治理检查能力已经被封装为 AI agent 可调用、可解释、可暂停的本地 advisory guardrail。下一阶段应进入阶段 8，把治理能力从“本地可调用”推进到“开发流程可稳定使用、可审计、可复现”。

## 总体目标

下一阶段目标分两层：

1. 把当前 v0.3 成果固定成可回退、可验证、可演示的 release-candidate 版本点。
2. 在此基础上启动 v0.4 主线，重点提升真实仓库决策价值和 AI 可调用治理能力。

原则：

- 先封存版本点，再继续做大改动。
- 后续每一刀都必须有 OpenSpec change。
- 不做泛化 SaaS 扩张，优先做真实仓库决策质量。
- 保持 why-search 和 drift 的保守可信边界。
- AI governance layer 先做单项目本地 MVP，不直接做企业治理平台。

## 阶段 0：封存 v0.3 RC

建议 change：

```text
finalize-v0-3-rc-tag-and-validation
```

### 目标

把当前 `main` 封存为明确的 v0.3 release-candidate 版本点，避免后续 v0.4 工作缺少稳定基线。

### 范围

- 运行 canonical release gate。
- 运行 OpenSpec strict validation。
- 确认 Playwright demo smoke / local full-chain 检查结果。
- 确认 release notes、quick start、deployment、FAQ、hosted preview readiness 文档与当前状态一致。
- 打 tag：

```text
v0.3.0-rc.1
```

- 推送 tag 到远端。
- 更新更新日志或 release checklist，记录 tag commit 和验证命令。

### 非目标

- 不改 extraction 逻辑。
- 不改 why-search 排序。
- 不新增 governance 功能。
- 不新增 hosted infra 自动化。

### 验收标准

- `scripts/ci/pre-release.ps1` 通过。
- `openspec validate --all --strict` 通过。
- `v0.3.0-rc.1` tag 存在于本地和远端。
- release 文档中的 tag readiness 与实际 Git 状态一致。

## 阶段 1：真实仓库决策信号质量

建议 change：

```text
improve-real-repo-decision-signal-quality
```

### 目标

提升真实仓库导入后 candidate decisions 的可用性，让 reviewer 更容易建立第一个可信 accepted baseline。

### 当前问题

- 部分候选决策偏 thin。
- source refs 和 quote preview 的质量决定后续 why-search / drift 是否可信。
- artifact provenance 已有基础，但 review 页面仍需要更明确地帮助用户判断强弱。
- extraction 不能只追求产出数量，必须优先保证候选决策有实际决策价值。

### 范围

- 更明确地区分 strong / partial / thin candidate。
- Review card 展示更直接的质量信号：
  - source ref count
  - previewable quote count
  - artifact provenance
  - confidence bucket
  - extraction family
- 对明显 low-value candidate 提供诊断，而不是与强候选混在一起。
- 更新真实仓库质量报告。
- 增加 fixture 或单测，覆盖 candidate quality label。

### 非目标

- 不重写整个 extraction pipeline。
- 不引入多人 review。
- 不把单个仓库特例硬编码进产品。

### 验收标准

- Reviewer 能在列表页判断候选决策强弱。
- Thin candidate 不会被误包装成强结果。
- 至少一个 curated repo fixture 能验证 strong / partial / thin 分布。

## 阶段 2：Why Search 检索质量

建议 change：

```text
improve-imported-why-retrieval-quality
```

### 目标

让 imported workspace 中的 why-search 在用户问法变化时仍能命中正确 accepted decision，并用更丰富证据支持回答。

### 当前问题

- Query rewrite 目前较弱，主要是 lower-case 和 whitespace normalize。
- Hybrid retrieval 中 full-text 权重偏主导，语义检索贡献不足。
- artifact chunk index 已经存在，但主 why-search 仍主要依赖 accepted decision 本身。
- 回答仍应保守，不能变成自由生成。

### 范围

- 增加技术同义词和别名 normalize。
- 调整 hybrid retrieval 权重并加入测试。
- 将 artifact chunks 作为 accepted decision 的支持证据层。
- 引入更明确的支持状态：
  - `ok`
  - `limited_support`
  - `evidence_limited`
  - `review_required`
- 增加 benchmark questions，验证等价问法能命中同一主决策。

### 非目标

- 不用自由 LLM answer 取代当前 grounded answer。
- 不允许无 accepted decision 时直接给强答案。
- 不做跨仓库通用问答。

### 验收标准

- 等价问法能稳定命中同一 accepted decision。
- chunk evidence 能增强回答支持，但不替代 accepted decision trust anchor。
- 弱证据仍返回受限状态，而不是强行回答。

## 阶段 3：Workspace 复用与增量同步产品化

建议 change：

```text
productize-workspace-reuse-and-incremental-sync
```

### 目标

降低重复导入和重复分析成本，让用户清楚知道当前仓库是否已有 workspace、是否应打开已有结果、增量同步或完整重跑。

### 当前问题

- 同一 GitHub repo 再次分析时，系统已具备一定复用能力，但 UI 仍容易让用户发起重复 full import。
- artifacts upsert 和 source ref skip 已有基础，但 indexing / extraction 仍可能重复消耗。
- 用户缺少明确选择：
  - open existing
  - incremental sync
  - full re-analysis

### 范围

- Live analysis form 检测已存在 workspace。
- 提供三种用户动作：
  - 打开已有 workspace
  - 增量同步
  - 完整重跑
- Dashboard 展示：
  - latest sync time
  - sync origin
  - running import job
  - last import summary
- 阻止或警告重复 running import。
- 更新 quick start / FAQ 中关于 repeat run 的说明。

### 非目标

- 不立即做复杂 cancel workflow。
- 不做完整 job management 控制台。
- 不做跨 owner workspace 合并。

### 验收标准

- 用户不会在不知情情况下重复 full import。
- 已存在 workspace 的下一步路径清楚。
- 增量同步和完整重跑在 UI 文案中区别明确。

## 阶段 4：Markdown Governance Ingest MVP

建议 change：

```text
prototype-governance-markdown-ingest
```

当前状态：已完成。

### 目标

启动 AI Governance Knowledge Layer 的第一刀：让用户上传或导入 Markdown 规范、路线、错误总结和人工决策，并把它们转成可审核规则草稿。

### 产品定位

这不是普通文档库，也不是普通 RAG。它的目标是让人类确认过的项目方向和规范变成 AI 可读取、可执行、可审查的治理上下文。

### 范围

- 支持 Markdown governance document ingest。
- 文档类型：
  - standard
  - coding_guideline
  - architecture_policy
  - roadmap
  - postmortem
  - checklist
  - decision_record
  - anti_pattern
  - release_policy
  - security_policy
- 抽取 rule drafts：
  - title
  - description
  - severity
  - scope
  - source document
  - rationale
  - status
- 人工 review / accept / reject 规则。
- 保存 accepted rules。
- 基础 UI 或 CLI 展示文档和规则状态。

### 非目标

- 不做完整企业权限。
- 不做复杂知识图谱 UI。
- 不自动把 AI 抽取结果升级成有效规则。
- 不接入 CI 阻断。
- 不在本阶段做 git diff 的 AI 自动裁决。

### 验收标准

- 用户能导入一组 Markdown 项目规范。
- 系统能用确定性规则抽取可审核规则草稿，不依赖 provider credential。
- 人能审核并接受规则。
- accepted rules 能被后续 checker 读取。

## 阶段 5：Governance Diff Checker

建议 change：

```text
add-governance-diff-checker
```

### 目标

让 AI 或开发者可以读取当前 git diff，对照 OpenSpec、roadmap、accepted rules 和历史错误总结，判断当前变更是否符合项目方向。

### 范围

- 新增本地检查入口，例如：

```text
decisionatlas governance check
```

- 输入：
  - current git diff
  - active OpenSpec change
  - main specs
  - roadmap
  - accepted governance rules
  - recent update logs
- 输出：
  - status: pass / warning / blocked
  - findings
  - matched rules
  - conflicting rules
  - required tests
  - recommended next action

### 非目标

- 不自动修改代码。
- 不自动覆盖人类规则。
- 不默认阻断 CI。
- 不替代 code review。

### 验收标准

- 对一个真实 git diff 能输出结构化治理检查结果。
- 能识别缺少 OpenSpec change、偏离 roadmap、缺少测试、重复历史错误等问题。
- blocker / warning / note 分级明确。

## 阶段 6：Governance Drift Detection

建议 change：

```text
add-governance-drift-detection
```

### 目标

把规范偏离、路线偏离、过期规则误用纳入 DecisionAtlas 的 drift 模型。

### 范围

- 检查 specs 与实现是否逐渐不一致。
- 检查 roadmap 与实际提交方向是否偏离。
- 检查 deprecated / superseded rules 是否仍被引用。
- 检查历史错误总结中提到的问题是否重复出现。
- 输出 drift report。

### 非目标

- 不做全自动修复。
- 不做复杂组织审计。
- 不做生产级 compliance 平台。

### 验收标准

- 能生成一份 governance drift report。
- 能指出冲突来源、影响范围和建议人工决策点。
- 人类新决策可以反向更新规则状态。

当前状态：已完成。

## 阶段 7：AI Agent Governance Integration

建议 change：

```text
integrate-ai-agent-governance-guardrails
```

### 目标

把阶段 5 的 Governance Diff Checker 和阶段 6 的 Governance Drift Detection 封装成 AI agent 可调用的开发护栏，让 AI 在改代码前后都能自查是否符合 OpenSpec、roadmap、accepted governance rules、历史错误总结和总方向。

### 产品定位

阶段 7 不是把 AI 变成自动裁判，而是把人类确认过的项目方向变成 agent 工作流中的显式上下文。AI 可以报告、建议、暂停并要求人工决策，但不能自动覆盖人类规则或替代 review。

### 范围

- 增加 agent-facing governance runbook，定义 AI 在开发前、开发中、开发后如何调用：
  - `scripts/governance/check.py`
  - `scripts/governance/drift_report.py`
- 定义标准化输出摘要：
  - current diff compliance
  - roadmap/spec alignment
  - accepted-rule conflicts
  - repeated historical issue signals
  - missing tests or validation evidence
  - human decision required
- 增加一个本地组合命令或脚本，聚合 diff check 和 drift report 的核心结果。
- 明确 agent pause rules：
  - blocker finding
  - `review_required`
  - accepted rule conflict
  - unsynced human decision
  - missing OpenSpec for behavior change
- 增加 fixtures / tests，验证组合输出不会在 clean 情况下误报为阻断。
- 更新开发文档，说明这仍是 advisory workflow，不是 CI blocking。

### 非目标

- 不接入自动 CI 阻断。
- 不自动修改代码。
- 不自动更新 specs 或 accepted rules。
- 不接入外部 LLM provider 作为唯一判断来源。
- 不做完整企业治理平台或多团队权限治理。

### 验收标准

- AI agent 可以通过一个稳定入口获得当前 change 的治理摘要。
- clean 情况下输出可继续开发的建议。
- blocker / `review_required` 情况下输出明确暂停原因和人工决策点。
- 输出必须包含 source-linked evidence，而不是只有自然语言判断。
- 现有 pre-release gate 不受影响。

当前状态：已完成。实现入口为 `scripts/governance/agent_guardrail.py`，主 spec 为 `openspec/specs/ai-agent-governance-guardrails/spec.md`，归档 change 为 `openspec/changes/archive/2026-05-06-integrate-ai-agent-governance-guardrails/`。

## 阶段 8：Governance Workflow Hardening And Demo Reset Reliability

建议 change：

```text
harden-governance-workflow-and-demo-reset
```

### 目标

把阶段 7 的本地 AI governance guardrail 从“可调用”推进到“开发流程中稳定可用”，同时修复真实栈演示中发现的 demo review queue 可重复性问题。

### 产品定位

阶段 8 不是扩大治理平台范围，而是补齐可复现性和操作边界：开发者、AI agent、operator 都能明确知道什么时候运行检查、如何处理 `caution` / `pause`、如何把 demo 数据重置到稳定演示状态。

### 范围

- 增加一条标准化开发前/开发后 governance guardrail 使用说明，明确 OpenSpec apply、archive、commit 前的检查节点。
- 补一个 lightweight runbook 或脚本，输出当前治理状态、active changes、agent guardrail status、required actions。
- 处理 demo workspace 在真实 Postgres 下 review queue 已被消费后无法稳定复演的问题：
  - 明确 reset / reseed 命令。
  - 或新增 demo reset 脚本，恢复候选队列、accepted baseline、why-search、timeline、drift 的预期演示状态。
- 修复并记录 Alembic revision ID 长度约束，防止 Postgres `alembic_version.version_num varchar(32)` 再次失败。
- 更新 quick start / operator guide / troubleshooting 中的真实栈启动和 demo reset 注意事项。

### 非目标

- 不把 governance guardrail 接入默认 CI 阻断。
- 不自动修改 specs、roadmap 或 accepted rules。
- 不做完整 PR bot。
- 不做完整企业级 audit log。

### 验收标准

- 真实栈从 clean Postgres/Redis 状态可启动。
- demo reset 后 review queue、why-search、timeline、drift 均回到稳定 guided demo 状态。
- `python scripts/governance/agent_guardrail.py --summary` 可作为开发者/AI agent 的明确检查入口。
- migration revision ID 长度有测试保护。
- 文档说明清楚：哪些检查是 advisory，哪些情况需要人工决策。

## 推荐执行顺序

```text
0. finalize-v0-3-rc-tag-and-validation
1. improve-real-repo-decision-signal-quality
2. improve-imported-why-retrieval-quality
3. productize-workspace-reuse-and-incremental-sync
4. prototype-governance-markdown-ingest
5. add-governance-diff-checker
6. add-governance-drift-detection
7. integrate-ai-agent-governance-guardrails
8. harden-governance-workflow-and-demo-reset
```

## 暂缓事项

短期不建议做：

- billing。
- 完整 SaaS 多租户管理台。
- GitHub Marketplace 完整 OAuth。
- secret vault。
- 多人协作 review workflow。
- 新 connector 大扩展。
- 自动 CI 阻断式 governance enforcement。
- 大规模权限模型重构。

原因：

- 当前产品最需要证明的是真实仓库决策价值，而不是 SaaS 包装完整度。
- 治理知识层应先以单项目、本地、可审核的 MVP 形态落地。
- 如果太早做完整平台，会稀释 DecisionAtlas 的核心差异化。

## 成功判断

下一阶段成功不以“页面更多”衡量，而以以下结果衡量：

- v0.3 有明确 tag，可回退、可演示、可验证。
- 真实仓库导入后能更快产出可信 accepted decision。
- why-search 对真实仓库问题更有用，且不牺牲证据边界。
- 重复导入成本和用户困惑下降。
- Markdown 项目规范能变成 AI 可读取、可审核的规则。
- AI 能基于项目规则判断当前变更是否偏离方向。
- AI agent 能在开发前后调用治理检查入口，并在需要人工决策时明确暂停。
- 真实栈 demo 能重复 reset / reseed，避免审阅队列状态污染影响演示。
- migration / startup 失败能被测试或 runbook 提前捕获。

最终方向：

```text
DecisionAtlas 从“工程决策记忆系统”
升级为“AI-native project governance memory”。
```
