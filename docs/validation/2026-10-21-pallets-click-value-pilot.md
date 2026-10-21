# 2026-10-21 · 独立真实仓库试点：pallets/click

> 状态：**REPOSITORY VERIFIED / ENGINE IMPORT NOT RUN**（仓库可访问，尚未使用 DecisionAtlas Engine 完整导入）
>
> 目的：在停止增加新功能后，用非 Demo 的真实仓库测试决策提取、人工审核、引用问答和漂移检测的价值。绝不把 `fixture` / GitHub 元数据检查宣称为 DecisionAtlas 端到端成功。

## 云端执行（无需本地环境）

- GitHub Actions 工作流：[Public repository value pilot (pallets/click)](https://github.com/luzay-max/DecisionAtlas/actions/workflows/public-value-pilot.yml)。
- PR #7 仍未合并时，GitHub 只能通过**此分支的代码推送**触发新增工作流；该工作流有精确分支和路径过滤。你现在可以打开现有 run 右上角 **Re-run all jobs** 重新运行同一提交。
- **重要限制**：GitHub 的 `Run workflow`（`workflow_dispatch`）按钮一般要求工作流文件已经存在于默认分支。因此在 PR #7 未合并前，不能依赖该按钮；未来工作流进入 `main` 后才可以从 Actions 手动选择分支执行。
- Runner 使用 Windows 2025、Python 3.13、锁定的 `uv` 依赖、孤立的临时 SQLite 和仅绑定 `127.0.0.1` 的 Engine。只允许本次临时测试用 `APP_ENV=test` / `AUTH_AUTO_BOOTSTRAP_LOCAL=true`。
- **不需要用户设置任何模型或 GitHub API Key**：GitHub Actions 自带的临时 read-only token 仅用于访问真实的公开 GitHub API；分析模型明确设为 Fake Provider。这能证明真实仓库的可导入性和流水线行为，**不能证明真实 LLM 提取或回答质量**。
- 每次运行在 **Artifacts** 区域上传 `decisionatlas-pallets-click-public-import-<run number>` ZIP，内含 `pilot-pallets-click-import.json/.md` 和 `pilot-pallets-click-summary.json/.md`。数据库、Engine 原始日志、密钥不上传；即使导入失败也保留诊断报告。
- 结果只有在导入任务 `succeeded` 且落地至少 1 条真实源 Artifact 时才写 `import_pass_only`。20 候选、10 Why、5 Drift 的人工判断仍为 `not_run`，不得包装成成功。
- 第一次实际云端运行：[run #39553746386](https://github.com/luzay-max/DecisionAtlas/actions/runs/39553746386)，真实导入 1,093 条资料后在提取阶段因 `sqlite3.OperationalError: database is locked` 失败；产出的失败报告被保留。针对这一生产可靠性问题已在 PR #7 同分支加入修复及回归测试，待最新云端复测验证。

---

## 1. 真实来源和固定样本

- Public GitHub: https://github.com/pallets/click
- 首次采样时间：2026-10-21；default branch `main`，固定 SHA：`2247b35ea1c47c727d7a06e51fa280e12a863ff6`（执行导入时记录实际 HEAD，若发生变化必须注明）。
- 当前可核对的工程决策材料：
  - https://github.com/pallets/click/pull/3877：区分 `Parameter.decls`、`spec`、`name` 三类受众；弃用 `human_readable_name`，旨在统一公开/内部 API 概念。
  - https://github.com/pallets/click/pull/3884：规范 `show_envvar` 对空值和序列的用户可见错误提示与帮助输出。
- 以上仅证明 GitHub 上存在可追踪的决策线索；尚未证明系统能提取它们。

## 2. 受控运行（Windows PowerShell）

**前置门禁**：在本地、隔离的真实栈运行；不能把生产私有 Token 放进当前尚未完成加密迁移的存储路径。确保 `APP_ENV=development` 或专用测试环境仅绑定 localhost，`AUTH_AUTO_BOOTSTRAP_LOCAL=true` 只用于本机封闭 Demo；真实生产必须正常登录。使用固定模型 provider；Fake Provider 的测试结果不能冒充真实 AI 质量。

```powershell
# 仓库根目录；依照项目现有文档启动真实栈，独立记录健康检查
powershell -ExecutionPolicy Bypass -File .\scripts\dev\start-real-stack.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\demo\health-check.ps1 -SkipDependencyChecks

# 通过现有导入脚本的新 --repo 参数进行本次独立验证
python scripts\ci\rehearse_public_github_import.py `
  --repo pallets/click `
  --wait --timeout-seconds 900 --poll-seconds 5 `
  --output-json .tmp\pilot-pallets-click-import.json `
  --output-markdown .tmp\pilot-pallets-click-import.md
```

API 若禁用演示 bootstrap，使用有权限的管理员登录并给脚本提供 `--session-token`，该脚本同时向 Fastify 传 Session Cookie 和向 Engine 传 Session Header。**不要把真实 session token 写入脚本文件、命令日志或版本控制**；避免在共享 Shell 历史里以明文命令参数传 Token。可使用隔离本机 Demo 的自动 bootstrap，或进一步改善操作密钥传递方案后再启用受控认证脚本。

如果 `setup.outcome=operator_guided`、`provider_failure`、`local_stack_failure`，这是部署/访问条件，不是产品质量分；必须先排除并重跑。必须有 `import_job.status=succeeded` 和非零可用证据，才能进入评估。

## 3. 人工评估协议

采用真实 `pallets/click` 的当前数据，不使用曾经导入的 `encode/httpx` Demo 结果替代。

### 决策提取（样本 20）
- 导入后的候选决策中取前 20 条并固定排序与 ID，少于 20 则取全部。
- 每条判定 `real_decision` / `not_decision` / `unclear`，以及 `source_verified` / `missing_source`；记录原始 URL，不提交大段原文。
- 通过率分母必须是实际已审核条数，零条候选不得记为 100%。

### 预先登记的 Why 问题（避免只挑成功案例）

| # | 用户问题 | 预期来源或判定原则 | 结果 |
| --- | --- | --- | --- |
| 1 | 为什么 Click 区分参数的 `decls`、`spec`、`name`？ | PR #3877 | not_run |
| 2 | 为什么将 `human_readable_name` 弃用并改为 `Parameter.spec`？ | PR #3877 | not_run |
| 3 | 为什么参数需要把开发者声明、帮助界面和内部标识拆开？ | PR #3877 | not_run |
| 4 | `get_help_spec` 与参数显示规范调整有什么关系？ | PR #3877 与其引用的 #3821；证据不充分须明说 | not_run |
| 5 | 为什么 `show_envvar` 的空字符串值不应该显示误导性提示？ | PR #3884 | not_run |
| 6 | 为什么环境变量列表的错误提示不应显示 Python 列表文本？ | PR #3884 | not_run |
| 7 | 为什么帮助输出在空 `envvar` 时不应该出现空标签？ | PR #3884 | not_run |
| 8 | 为什么 `spec` 应该等于某种特定 CLI 风格？ | 检查 PR #3877 是否真的说明；不能凭模型推断 | not_run |
| 9 | Click 是否决定将所有 help 输出强制改为 man page？ | 负向对照：未证实的 Issue/提议不等于 accepted decision | not_run |
| 10 | Click 是否接受了所有关于 shell completion 的 Issue 建议？ | 负向对照：不得把 Issue 误说成已接受的架构决策 | not_run |

评分：正确且可核验引用=pass；依据不足时明确拒答=honest_limit；错误归因、伪造引用=fail；没运行=not_run。必须保留失败案例。

### Drift
- 使用系统已接受的规则/决策执行 5 条真实变更案例；缺少规则或可判断案例写 `not_provided`。
- 记录正确提醒、误报、漏报以及人工结论；不以 AI 自评充当 ground truth。

## 4. 验收与真实状态

| 检查项 | 当前状态 |
| --- | --- |
| 公共仓库 GitHub 可访问性和选题有真实证据 | verified |
| 本次版本上的 DecisionAtlas Engine 导入 | **not_run** |
| 20 条候选人工审核 | **not_run** |
| 10 条 Why 回答及引用评分 | **not_run** |
| 5 条 Drift 人工验证 | **not_run** |
| 非作者独立体验 | **operator_guided** |
| 私有仓库 Token 加密及迁移 | **blocking** |

结论：当前只有**试点选题与复现实验材料**，不能声称 DecisionAtlas 已在 `pallets/click` 产生有效决策知识。真实执行证据放 `.tmp/pilot-pallets-click-*.json/.md`，审核后再提交脱敏摘要。终止新功能开发，只有与验收阻断直接相关的 Bug 允许进入下一轮修复。
