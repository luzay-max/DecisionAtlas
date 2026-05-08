# Governance Diff Checker

日期：2026-05-06

## 目标

Governance Diff Checker 是阶段 5 的第一刀：读取当前工作区变更，并对照 OpenSpec、主 specs、路线计划、accepted governance rules 和近期项目记录，输出保守、可解释的治理检查结果。

它不是自动裁决系统，也不是默认 CI blocker。第一版只提供 advisory result，帮助人或 AI agent 在提交前发现明显偏离。

## 运行方式

从仓库根目录运行：

```powershell
python services/engine/app/governance/diff_checker.py --root . --pretty
```

也可以使用薄封装入口：

```powershell
python scripts/governance/check.py --root . --pretty
```

如果需要读取本地 SQLite governance rules，可以传入 owner scope 和数据库路径：

```powershell
python scripts/governance/check.py --root . --owner-scope local-default --database-url sqlite:///services/engine/decisionatlas.db --pretty
```

## 输出结构

输出为 JSON，面向人和后续 AI tool 调用：

- `status`: `pass` / `warning` / `blocked`
- `findings`: source-linked findings
- `matched_rules`: 命中的 accepted governance rules
- `conflicts`: blocker 级别冲突
- `required_tests`: 推断出的测试或验证要求
- `recommended_next_action`: 建议下一步
- `context`: 本次检查读取到的上下文摘要，包括 stale / superseded accepted rules 的 `inactive_rule_traces`

## 状态语义

- `pass`: 未发现治理阻塞；仍需正常 code review。
- `warning`: 有缺失证据、路线不明确、验证不足等问题，需要人工确认。
- `blocked`: 有明确治理问题，例如非平凡代码变更缺少 OpenSpec，或直接违反 accepted governance rule。

## Accepted Rule Lifecycle

checker 只把 `review_state=accepted`、`status=active`、`lifecycle_status=current` 的规则作为权威输入。`stale` 和 `superseded` 规则不会生成 authoritative blocker finding。

为了保留审计链路，checker 会在 `context.inactive_rule_traces` 中暴露 accepted 但 inactive 的规则摘要，包括 lifecycle status、lifecycle rationale 和 `superseded_by_rule_id`。这些信息用于人工复核和交接，不用于自动裁决。

## 边界

当前 checker 不会：

- 修改代码。
- 修改 OpenSpec artifacts。
- 自动改写 accepted governance rules。
- 默认阻断 CI。
- 替代人工 review。

如果 checker 发现规则冲突，正确动作是由人审核当前变更或更新治理文档，而不是让 AI 私自改写项目方向。
