# Governance Markdown Ingest MVP

日期：2026-04-29

## 目标

阶段 4 第一刀的目标是把人类已经写下来的项目规范、路线、错误总结和人工决策导入 DecisionAtlas，形成可审核、可引用的治理知识层。

这一层不是自动裁决系统。它先解决三个基础问题：

- 项目治理文档能被保存，并保留来源。
- 文档里的规则候选能被确定性抽取成草稿。
- 人可以审核草稿，只有 accepted rules 才成为后续 AI checker 的输入。

## 支持的文档类型

- `standard`
- `coding_guideline`
- `architecture_policy`
- `roadmap`
- `postmortem`
- `checklist`
- `decision_record`
- `anti_pattern`
- `release_policy`
- `security_policy`

## 推荐 Markdown 写法

为了让第一版确定性抽取更稳定，建议用标题或明确 marker 描述规则：

```markdown
## Rule: Every change must have targeted tests

Severity: warning
Scope: engine
Rationale: Prevent regressions in backend behavior.

Every backend behavior change should include a targeted pytest or documented skip.
```

抽取结果会保留：

- title
- description
- severity
- scope
- rationale
- source document
- source excerpt
- review state

## 审核语义

- `pending`：系统抽取出的规则草稿，尚未成为治理规则。
- `accepted`：人类审核通过，后续 AI checker 可以引用。
- `rejected`：人类审核拒绝，不能作为有效治理规则使用。

accepted rule 仍然不是 CI blocker。它只是后续 diff checker、drift detector 和 AI review agent 的可信上下文。

## 当前非目标

- 不做自动 CI 阻断。
- 不做 git diff 自动裁决。
- 不做 LLM-only 抽取。
- 不做复杂知识图谱 UI。
- 不做企业级权限模型。
- 不把任意上传文档自动升级为有效规则。

## 后续衔接

下一阶段可以在 accepted rules 基础上启动 governance diff checker：

- 读取当前 git diff。
- 读取 active OpenSpec change。
- 读取 main specs、roadmap、历史错误总结和 accepted rules。
- 输出 pass / warning / blocked 级别的治理检查结果。

这一步必须保留人工审核入口：当规则冲突、路线变化或历史决策过期时，由人更新治理文档或调整 accepted rule 状态，而不是让 AI 私自改写大方向。
