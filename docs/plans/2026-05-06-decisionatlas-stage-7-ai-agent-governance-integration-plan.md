# DecisionAtlas 阶段 7 后续开发计划：AI Agent Governance Integration

日期：2026-05-06  
当前基线：`main` @ `dc8e00c`  
当前状态：阶段 4、阶段 5、阶段 6 已完成；OpenSpec active changes 为 0；本地 `main` 相对 `origin/main` ahead 3

## 背景判断

DecisionAtlas 已经具备 AI governance layer 的三个基础能力：

- 阶段 4：Markdown Governance Ingest MVP  
  人类可以导入规范、路线、错误总结、人工决策等 Markdown 文档，并审核 accepted governance rules。

- 阶段 5：Governance Diff Checker  
  当前 git diff 可以对照 OpenSpec、roadmap、main specs、accepted rules 和验证期望输出 `pass` / `warning` / `blocked`。

- 阶段 6：Governance Drift Detection  
  项目可以生成长期 governance drift report，识别 roadmap mismatch、spec gap、stale rule、repeated postmortem issue、unsynced decision 等信号。

下一阶段不应继续单纯增加检查器，而应把这些检查器接入 AI agent 的开发工作流，让 AI 在动手前、修改中、提交前都能读取项目治理上下文。

## 阶段 7 总目标

让 AI agent 能够把 DecisionAtlas 当成项目治理组件使用：

```text
人类确认方向
  -> Markdown governance docs / accepted rules / OpenSpec / roadmap
  -> AI agent 开发前读取治理上下文
  -> AI agent 开发后运行治理检查
  -> 发现冲突时暂停并请求人工决策
```

重点不是让 AI 自动裁决，而是让 AI 不再“盲写代码”。

## 建议 Change

```text
integrate-ai-agent-governance-guardrails
```

## 第一刀范围

### 1. Agent-facing Governance Runbook

新增文档，定义 AI agent 在以下节点应该怎么使用治理能力：

- 开发前：
  - 读取 active OpenSpec change。
  - 读取 roadmap / master plan。
  - 读取 accepted governance rules。
  - 确认本次任务是否需要 OpenSpec。

- 开发中：
  - 当实现范围偏离 tasks 或 design 时，标记为 possible scope drift。
  - 当需要改变规则或方向时，暂停要求人工决策。

- 开发后：
  - 运行 governance diff check。
  - 运行 governance drift report。
  - 汇总 status、findings、signals、required tests。
  - 对 blocker / review_required 明确暂停。

### 2. 组合检查入口

新增本地组合命令或脚本，例如：

```text
scripts/governance/agent_check.py
```

输入：

- repository root
- owner scope
- optional rules JSON
- optional output mode

内部调用：

- `scripts/governance/check.py`
- `scripts/governance/drift_report.py`

输出一个简化后的 agent summary：

```json
{
  "status": "continue | caution | pause",
  "diff_check": {
    "status": "pass | warning | blocked"
  },
  "drift_report": {
    "status": "clean | watch | drift_detected | review_required"
  },
  "blocking_reasons": [],
  "required_tests": [],
  "human_decisions_needed": [],
  "recommended_next_actions": [],
  "evidence": []
}
```

### 3. Agent Pause Rules

第一版 pause 规则必须保守、明确：

- Governance diff check 返回 `blocked`。
- Governance drift report 返回 `review_required`。
- 发现 accepted blocker rule conflict。
- 发现 behavior code change 但没有 active OpenSpec context。
- 发现 unsynced human decision。
- 发现 required tests 为空但存在行为代码变更。

warning / watch 不应默认阻断，只应输出 caution。

### 4. Tests And Fixtures

需要覆盖以下场景：

- clean + pass -> `continue`
- warning + clean -> `caution`
- pass + watch -> `caution`
- blocked + any -> `pause`
- any + review_required -> `pause`
- API-shaped `{"rules": [...]}` 规则输入仍可用

### 5. Documentation

补充：

- AI agent 如何调用治理检查。
- 输出状态如何解释。
- 什么情况下必须暂停找人。
- 为什么当前不是 CI blocker。
- 如何把人工新决策反向同步到 specs 或 governance rules。

## 非目标

短期不要做：

- 自动 CI 阻断。
- 自动修复代码。
- 自动改 OpenSpec。
- 自动 accept / reject governance rules。
- 自动把 AI 判断写入主规范。
- 多团队企业级治理平台。
- 外部 LLM provider 绑定为必需依赖。

## 验收标准

阶段 7 第一刀完成时，应该满足：

- AI agent 有一个稳定入口能获取治理摘要。
- clean 情况下不会误报 pause。
- blocker / review_required 情况下会明确暂停。
- 输出包含 source-linked evidence。
- 输出能说明下一步是补测试、补 OpenSpec、更新 spec、人工决策，还是继续开发。
- `openspec validate --all --strict` 通过。
- targeted governance tests 通过。
- practical release gate 不被新增脚本破坏。

## 风险评估

### 风险：AI 过度服从检查器

如果 agent 把 advisory report 当成绝对裁判，会导致开发被误阻断。

缓解：

- 输出使用 `continue` / `caution` / `pause`，不使用“approved / rejected”。
- 只有硬条件进入 pause。
- 所有 pause 都要求 source-linked evidence。

### 风险：治理信号噪声过高

如果 drift report 太敏感，agent 会频繁暂停。

缓解：

- `watch` 只进入 caution。
- repeated historical issue 只在当前 diff 明确重叠时触发。
- 不把 broad roadmap mismatch 直接当 blocker。

### 风险：agent check 变成另一个复杂平台

如果第一版就接 UI、数据库、CI，会拖慢节奏。

缓解：

- 第一版只做本地脚本和文档。
- 输出 JSON，方便后续再接 UI 或 agent adapter。

## 建议执行顺序

```text
1. propose: integrate-ai-agent-governance-guardrails
2. implement agent-facing runbook
3. implement local aggregate agent_check.py
4. add fixtures for continue/caution/pause
5. add targeted tests
6. run governance check + drift report + OpenSpec validation
7. archive and commit
```

## 后续扩展

阶段 7 第一刀稳定后，再考虑：

- 接入 Codex / Claude / OpenCode 等 agent 的实际工作流。
- 在 PR 描述中自动附加 governance summary。
- 在 release checklist 中加入 advisory governance summary。
- 在 UI 中展示最近一次 agent governance check。
- 允许人工把 pause 原因转成新的 governance decision record。

## 成功判断

阶段 7 成功不以新增页面数量衡量，而以 AI 是否能稳定做到以下三点衡量：

- 开发前知道项目方向。
- 开发后知道自己是否偏离方向。
- 遇到方向冲突时知道暂停找人，而不是继续猜。
