# AI Governance Knowledge Layer 未来企划

日期：2026-04-27  
状态：未来方向，不作为当前执行计划  
来源：用户提出的产品方向整理

## 核心判断

这个方向可行，而且与 DecisionAtlas 的长期定位高度一致。

DecisionAtlas 目前已经能记录工程决策、导入真实仓库、展示 review / why / drift 等决策记忆能力。下一步可以把它扩展为一个 **AI 可读取、可执行、可审查的项目治理知识层**。

核心不是让 AI 替代人做方向判断，而是建立这样的闭环：

```text
人定义正确方向、规范、经验和边界
        ↓
DecisionAtlas 结构化保存这些决策和规则
        ↓
AI 在开发、审查、规划时读取这些规则
        ↓
AI 判断当前变更是否符合方向和规范
        ↓
发现冲突时交给人审核
        ↓
人的新决策再次进入知识层
        ↓
AI 按新决策重新修改或重新规划
```

这让 AI 不再只是“临时读代码的执行者”，而是能持续理解项目方向、规范和历史教训的协作者。

## 用户提出的方案总结

用户希望后续支持上传一系列 Markdown 文档，例如：

- 开发标准
- 开发规范
- 架构原则
- 错误总结
- 事故复盘
- 项目路线图
- 产品方向说明
- 禁止事项
- 上线检查清单
- 团队约定

这些文档不仅给人看，也应该被系统吸收，成为 AI 可读取的项目治理上下文。

目标是：

- 防止 AI 每次开发时决策漂移。
- 提高 AI 生成代码的规范性和一致性。
- 让历史错误不被重复犯。
- 让项目方向由人类优先定义，AI 按方向执行。
- 当现有规范与新需求冲突时，由人类重新审核并形成新的决策。
- 新决策可以进入 DecisionAtlas 的决策记忆与 drift 检测体系。

## 产品定位

建议定位为：

```text
AI Governance Knowledge Layer
```

中文可以称为：

```text
AI 项目治理知识层
```

它不是普通文档库，也不是普通 RAG。它的价值在于把人类确认过的方向、规范和复盘变成 AI 可执行的约束。

## 关键产品原则

### 1. 人类优先定义方向

项目的大方向、规范优先级、风险边界必须由人确认。

AI 可以建议，但不能把建议直接升级为项目真理。

### 2. AI 负责执行与对齐

AI 在每次开发、审查、规划时读取治理知识层，判断当前工作是否符合：

- 当前 roadmap
- OpenSpec specs
- 已归档 change
- 开发规范
- 架构原则
- 历史错误总结
- 当前 release 目标

### 3. 冲突必须显式暴露

当 AI 发现冲突时，不应静默选择一边，而应输出：

- 冲突规则
- 冲突来源
- 影响范围
- 建议处理方式
- 是否需要人类决策

### 4. 人类审核后形成新决策

如果人类决定修改方向或覆盖旧规范，应产生新的决策记录：

- 为什么改变
- 哪条旧规则被替代
- 新规则适用范围
- 生效时间
- 后续代码应如何调整

### 5. 规则可以被废弃或替代

规范不是永久正确的。每条规则都应支持状态：

```text
active
deprecated
superseded
experimental
```

这样可以避免 AI 被过期文档误导。

## 文档类型模型

上传的 Markdown 可以被分类为：

```text
standard              开发标准
coding_guideline      代码规范
architecture_policy   架构原则
roadmap               产品路线
postmortem            错误总结 / 事故复盘
checklist             检查清单
decision_record       人工决策记录
anti_pattern          禁止事项 / 反模式
release_policy        发布规则
security_policy       安全规范
```

每篇文档应提取出结构化元数据：

```text
title
document_type
scope
owner
status
created_at
last_updated_at
source_path
priority
```

## 规则抽取模型

系统可以从文档中抽取规则：

```text
rule_id
title
description
severity: blocker | warning | note
scope: frontend | api | engine | docs | release | all
source_document
rationale
examples
status
supersedes
superseded_by
```

示例：

```text
Rule: 每个 OpenSpec change 必须在实现前有 tasks.md
Severity: blocker
Scope: all
Source: 开发规范.md
Rationale: 防止无计划实现导致 scope creep
```

```text
Rule: Playwright smoke 不应依赖未启动的 API
Severity: blocker
Scope: web / ci
Source: 错误总结.md
Rationale: GitHub Actions 曾因 ECONNREFUSED 失败
```

```text
Rule: 当前 v0.3 阶段不做 billing 和完整 SaaS 多租户
Severity: warning
Scope: roadmap
Source: v0.3 后续路线规划
Rationale: 当前目标是 release candidate 和 hosted preview
```

## AI 调用场景

### 1. 开发前规划检查

AI 在创建 OpenSpec proposal 前先检查：

- 是否符合当前 roadmap
- 是否已有相同能力 spec
- 是否与暂缓事项冲突
- 是否应该拆成更小 change

输出：

```text
direction: aligned | risky | off-roadmap
required_specs
conflicting_rules
recommended_change_name
```

### 2. 代码变更审查

AI 读取 git diff 后检查：

- 是否符合 active OpenSpec change
- 是否改动了不该改的模块
- 是否缺少测试
- 是否违反 coding guideline
- 是否触发历史错误模式

输出：

```text
status: pass | warning | blocked
findings
matched_rules
required_actions
```

### 3. 冲突决策审核

当需求和规则冲突时，AI 输出冲突报告：

```text
new_request
conflicting_existing_rules
impact
options
recommended_human_decision
```

人确认后，系统生成新的 decision record。

### 4. 决策漂移检测

AI 定期检查当前代码、spec、roadmap、文档是否漂移：

- 当前实现是否偏离 specs
- 当前开发计划是否偏离 roadmap
- 历史错误是否重复出现
- 已废弃规则是否仍被引用

输出 drift report。

## 与 DecisionAtlas 现有能力的关系

这个方向可以复用 DecisionAtlas 当前已经存在的能力：

- repository document ingest：导入 Markdown 文档。
- decision extraction：从规范和复盘中抽取规则与决策。
- review queue：让人审核 AI 抽取出的规则是否正确。
- why search：回答“为什么有这条规范”。
- drift detection：发现代码或计划是否偏离规范。
- OpenSpec integration：把 specs 和 changes 作为最高优先级项目约束。

建议把治理知识层视为新的上层能力，而不是独立产品。

## 优先级模型

AI 判断时应按优先级处理上下文：

```text
1. 当前明确的人类决策
2. active OpenSpec change
3. main specs
4. 当前 roadmap
5. release policy
6. security / architecture standards
7. postmortems / error summaries
8. older update logs
9. informal notes
```

如果低优先级文档与高优先级文档冲突，应优先采用高优先级，并提示冲突。

## 最小可行版本

建议第一版不要做复杂 UI，也不要做完全自动 agent。先做一个本地 governance checker。

建议 change：

```text
prototype-governance-markdown-ingest
```

### MVP 范围

- 支持导入 Markdown 文档。
- 允许给文档标记类型。
- 抽取规则草稿。
- 人工 review / accept / reject 规则。
- 保存 accepted rules。
- 提供一个 CLI 检查当前 git diff：

```text
decisionatlas governance check
```

输出：

- 命中的规则
- 潜在冲突
- 是否偏离 roadmap
- 是否缺 OpenSpec change
- 是否缺验证

### MVP 非目标

- 不做完整企业权限。
- 不做复杂知识图谱 UI。
- 不做自动阻断 CI。
- 不做多项目 SaaS。
- 不让 AI 自动覆盖人工规则。

## 后续阶段

### 阶段一：Markdown governance ingest

目标：让用户上传或导入规范、复盘、路线图文档。

输出：

- 文档列表
- 文档类型
- 规则草稿
- 人工审核入口

### 阶段二：AI rule review

目标：AI 从文档中抽取规则，人类确认后生效。

输出：

- accepted rules
- rejected rules
- rule source trace
- rule severity

### 阶段三：diff governance checker

目标：AI 读取当前 git diff，对照规则和 specs 输出审查报告。

输出：

- blocker
- warning
- note
- recommended fix
- required tests

### 阶段四：human decision override loop

目标：当新需求与旧规则冲突时，让人类审核并形成新决策。

输出：

- decision record
- superseded rule
- new rule
- rationale

### 阶段五：governance drift detection

目标：把规范偏离也纳入 DecisionAtlas drift 模型。

检测对象：

- 代码偏离规范
- roadmap 偏离执行
- specs 与实现不一致
- 旧规则被误用
- 历史错误重复出现

## 风险与边界

### 风险：文档质量不稳定

如果用户上传的 Markdown 模糊、过期或互相矛盾，AI 判断会变差。

缓解：

- 引入文档状态。
- 引入优先级。
- 引入人工审核。
- 冲突时不自动选择，必须显式报告。

### 风险：AI 过度执法

AI 如果把所有规则都当 blocker，会阻碍开发。

缓解：

- severity 分级。
- blocker 只用于安全、scope、release gate 等硬规则。
- warning 用于方向和风格建议。

### 风险：治理系统变重

如果一开始做完整企业治理平台，会偏离当前产品主线。

缓解：

- 第一版只做本地 / 单项目。
- 先支持 Markdown ingest 和 diff check。
- 不做 billing、org admin、复杂权限。

## 长期愿景

长期看，DecisionAtlas 可以从“工程决策记忆系统”升级为：

```text
AI-native project governance memory
```

它帮助团队回答：

- 为什么我们这样开发？
- 当前变更是否符合项目方向？
- 哪条规范约束了这次实现？
- 这个错误以前是否出现过？
- 如果方向改变，哪些规则和代码需要同步更新？
- AI 生成的代码是否遵守人类确认过的项目决策？

这会形成一个清晰差异化：

```text
普通 AI coding 工具负责写代码。
DecisionAtlas 负责让 AI 知道什么代码该写、什么方向不该偏、哪些错误不能再犯。
```

## 结论

用户提出的方向可行，并且值得作为 DecisionAtlas 的长期产品企划保留。

短期内不要把它塞进当前 v0.3 RC 主线。当前 v0.3 仍应先完成 release candidate、real stack validation 和 hosted preview。

但在 v0.3 基线稳定后，可以启动第一刀：

```text
prototype-governance-markdown-ingest
```

这会把用户上传的开发规范、错误总结、路线图和人工决策转化为 AI 可读取、可审核、可执行的项目治理知识层。
