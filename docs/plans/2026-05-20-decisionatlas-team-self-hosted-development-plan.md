# DecisionAtlas Team Self-hosted Development Plan

日期：2026-05-20  
目标路线：离线自托管包 + 小团队协作 + 多 Git 来源接入 + 管理员手动账号体系  
产品定位：自托管的代码决策治理协作平台，不做代码托管平台替代品

## 1. 一句话判断

DecisionAtlas 后续应该从“个人/本地决策分析工具”升级为“小团队可部署的决策治理协作系统”。

推荐方向：

```text
团队在自己的服务器部署 DecisionAtlas
        │
        ├─ 管理员创建账号、配置仓库 token、导入仓库
        ├─ 审阅者审查候选决策、drift、governance rules
        └─ 只读成员查看决策地图、why-search、drift、evidence
```

核心价值不是替代 GitLab/GitHub/Gitee，而是补上它们缺失的一层：

> Git 记录代码怎么变，DecisionAtlas 记录团队为什么这么做、哪些决策还有效、哪些已经漂移。

## 2. 已确认产品选择

| 问题 | 决策 |
| --- | --- |
| 部署方式 | 离线/私有自托管优先 |
| 目标客户 | 小团队 |
| 账号管理 | 管理员手动创建账号 |
| 仓库接入 | token 粘贴优先 |
| Git 来源 | GitHub、GitLab、Gitee、本地仓库都要支持 |
| 商业包装 | 离线自托管包，后续可加年度授权/支持 |
| 不优先做 | SaaS billing、多租户托管、Marketplace、自助 OAuth、企业 SSO |

## 3. 产品边界

### 要做

- 团队账号和角色权限。
- 多 workspace / 多仓库管理。
- GitHub / GitLab / Gitee / 本地仓库 token 或路径接入。
- 管理员导入公共/私有仓库。
- 审阅者处理候选决策和 drift。
- 只读成员查询和查看证据。
- 审阅记录、操作历史、证据链。
- 离线部署包、启动/停止/验收脚本。
- 自托管升级、备份、恢复路径。

### 不做或后置

- 不做 Git 托管、代码 review、CI/CD 替代。
- 不做完整 SaaS 多租户。
- 不做自助注册/找回密码/复杂账号运营。
- 不做 Marketplace/OAuth 自助安装优先路线。
- 不做企业 SSO 第一阶段。
- 不做复杂 license enforcement 第一阶段。

## 4. 目标用户与权限模型

### 管理员 Admin

职责：

- 初始化系统和主账号。
- 创建、禁用、重置成员账号。
- 分配角色。
- 配置 Git 来源 token 或本地仓库路径。
- 导入公共/私有仓库。
- 管理 workspace。
- 查看所有 evidence 和 readiness 状态。

权限：

- 可导入仓库。
- 可管理成员。
- 可管理访问源。
- 可审阅决策。
- 可修改 governance rules。
- 可运行 evidence/rehearsal。

### 审阅者 Reviewer

职责：

- 审阅候选决策。
- 接受、拒绝、标记 superseded。
- 处理 drift alert。
- 维护 governance rules。

权限：

- 可查看 workspace。
- 可审阅候选决策。
- 可处理 drift。
- 可提交治理规则变更。
- 不可管理成员。
- 不可新增全局仓库访问 token。

### 只读成员 Viewer

职责：

- 查看决策地图。
- 使用 why-search。
- 查看 drift 状态。
- 查看 evidence 和报告。

权限：

- 可查看已授权 workspace。
- 可搜索、阅读、导出有限报告。
- 不可导入仓库。
- 不可审阅候选决策。
- 不可修改治理规则。
- 不可管理 token。

## 5. 核心产品闭环

```text
管理员创建团队账号
        │
        ▼
管理员配置 Git 来源 token / 本地路径
        │
        ▼
管理员导入仓库，生成 workspace
        │
        ▼
系统抽取候选决策、来源证据、drift signals
        │
        ▼
审阅者接受 / 拒绝 / 标记过期
        │
        ▼
只读成员查询 why-search、查看决策地图
        │
        ▼
团队持续生成 release evidence / readiness history
```

这条闭环完成后，DecisionAtlas 才真正像一个团队产品，而不是单人分析工具。

## 6. 开发优先级

当前执行状态：

- `team-account-workspace-permissions` 已进入实现阶段，目标是先打通管理员手动账号、禁用、改密、角色、workspace 成员绑定，以及后端强权限校验。
- 本阶段仍保持手动管理员模式，不引入自助注册、邀请流、SSO、OAuth Marketplace 或 SaaS billing。

### P0：团队自托管可用闭环

目标：让一个小团队部署后能分账号协作。

建议 OpenSpec change：

`team-account-workspace-permissions`

范围：

- 管理员手动创建账号。
- 账号启用/禁用。
- 密码重置。
- admin/reviewer/viewer 权限落库。
- workspace 级权限绑定。
- 前端账号管理页面。
- 所有关键操作按角色隐藏和后端校验。

验收标准：

- 管理员可以创建 reviewer/viewer。
- viewer 登录后只能查看，不能审阅或导入。
- reviewer 可以审阅，但不能管理 token 和成员。
- admin 可以管理成员和仓库接入。
- 审阅、导入、governance 关键接口都有后端权限校验。

### P1：多 Git 来源接入

目标：支持 GitHub / GitLab / Gitee / 本地仓库。

建议 OpenSpec change：

`multi-git-source-token-import`

范围：

- 统一 Git source abstraction。
- GitHub token 导入。
- GitLab token 导入。
- Gitee token 导入。
- 本地仓库路径导入。
- 公共仓库无需 token 或 token 可选。
- 私有仓库必须由 admin 配置 token。
- token 只保存在后端/服务器环境，不回显前端。

验收标准：

- admin 可以配置不同 Git 来源。
- 同一个 workspace 记录来源类型。
- 导入结果显示 source provider、授权状态、失败原因。
- unauthorized / not found / rate limit / network failure 有明确提示。
- viewer/reviewer 不能看到 token。

### P2：审阅记录与协作审计

目标：形成团队责任链。

建议 OpenSpec change：

`collaborative-review-audit-trail`

当前实施边界：

- 审计记录覆盖 decision review、governance rule review/lifecycle、drift alert disposition。
- 每条记录保留 actor、role、target、action、前后状态、rationale、timestamp。
- 前端只展示紧凑历史，帮助团队知道“谁在什么时候为什么处理了什么”。
- 这不是 Git code review、复杂审批流或合规签章系统；第一阶段只做小团队可追溯协作证据。

范围：

- decision review action 记录 actor、role、时间、理由。
- accepted/rejected/superseded 状态变更可追溯。
- drift alert 处理记录。
- governance rule 生命周期记录 actor 和 rationale。
- 前端显示“谁在什么时候做了什么”。

验收标准：

- 每条决策能看到审阅历史。
- drift alert 能看到处理历史。
- governance rule 能看到版本和来源。
- export/report 能引用审阅记录。

### P3：离线自托管发布包

目标：让别人不是开发者也能部署。

建议 OpenSpec change：

`offline-self-hosted-release-package`

范围：

- 一键启动脚本稳定化。
- `.env.example` 面向部署场景整理。
- Docker Compose 部署路径。
- Windows/Linux 启动说明。
- health/smoke/readiness 验收脚本。
- 备份/恢复/升级说明。
- 首次管理员初始化说明。
- release package 目录结构或压缩包。

验收标准：

- 新机器按文档能跑起来。
- 能创建主账号。
- 能导入一个公共仓库。
- 能导入一个 token 私有仓库。
- 能生成 readiness evidence。

### P4：团队报告与客户交付

目标：让 Team Self-hosted 可以卖。

建议 OpenSpec change：

`team-handoff-reporting`

范围：

- 团队 workspace 总览报告。
- 决策地图导出。
- drift 风险报告。
- 审阅记录报告。
- evidence history 报告。
- Code Decision Audit 团队版模板。

验收标准：

- 管理员可以生成客户/团队可读报告。
- 报告包含 workspace、仓库、决策、审阅者、证据状态、限制。

### P5：授权与商业包装

目标：为收费做准备，但不影响核心使用。

建议 OpenSpec change：

`self-hosted-license-and-support-boundary`

范围：

- license 文件或离线 license key 说明。
- Community / Team / Enterprise 功能边界。
- 支持期限和升级说明。
- 不做强 runtime license enforcement，先以交付和支持边界为主。

验收标准：

- 用户能理解免费版和付费版差别。
- 客户部署材料有授权说明。
- 不阻塞本地评估和试点交付。

## 7. 推荐开发顺序

```text
1. team-account-workspace-permissions
        │
        ▼
2. multi-git-source-token-import
        │
        ▼
3. collaborative-review-audit-trail
        │
        ▼
4. offline-self-hosted-release-package
        │
        ▼
5. team-handoff-reporting
        │
        ▼
6. self-hosted-license-and-support-boundary
```

不要先做 GitLab 全家桶，也不要先做 SaaS。先把“小团队部署后能分工协作治理决策”跑通。

## 8. 为什么 P0 要先做账号与 workspace 权限

现在项目已经有登录、bootstrap session、角色门禁雏形，但还不够像真正团队产品。

如果不先做 P0，后面的仓库导入和报告都会出现问题：

- 不知道谁能看哪个仓库。
- 不知道谁能审阅。
- token 配置没有明确责任人。
- 审阅记录没有 actor 可信度。
- 客户无法把它给团队多人使用。

所以 P0 是团队协作产品的地基。

## 9. Git 来源支持策略

先统一模型，不要一开始为每个平台写完全不同的逻辑。

建议抽象：

| 字段 | 示例 |
| --- | --- |
| provider | `github` / `gitlab` / `gitee` / `local` |
| access_mode | `public` / `token` / `local_path` |
| repo_identifier | `owner/repo` 或本地路径 |
| credential_ref | 后端保存的 token 引用 |
| owner_scope | 团队/组织作用域 |
| workspace_slug | 导入后的 workspace |
| authorization_status | `authorized` / `unauthorized` / `not_found` / `rate_limited` / `network_failure` |

短期 token 粘贴是合理的。它比 OAuth/Git App 简单，适合离线自托管和小团队。

## 10. 安全底线

必须坚持：

- token 不回显。
- token 不进 `.tmp` evidence。
- token 不进 readiness history。
- token 不进导出报告。
- viewer/reviewer 不可读取 token。
- 所有敏感操作后端也要校验权限，不能只靠前端隐藏按钮。
- 默认管理员密码必须要求部署时修改或首次初始化。

## 11. 商业化落点

第一版可卖对象：

- 5-30 人小团队。
- 有多个仓库。
- 缺少架构决策记录。
- 经常有人问“为什么当初这么设计”。
- 想在私有环境部署，不想把代码交给 SaaS。

推荐包装：

```text
DecisionAtlas Team Self-hosted

- 离线部署包
- 管理员手动账号
- GitHub/GitLab/Gitee/本地仓库导入
- 决策审阅协作
- why-search
- drift 检查
- readiness evidence
- 团队报告
- 年度升级和支持
```

收费建议保持年费，不建议永久买断：

- 小团队早期价格：¥1999 - ¥9999 / 年。
- 部署服务：¥3000 - ¥20000 / 次。
- 企业私有部署另算。

## 12. 近期不要做的事

- 不要做 Git 托管。
- 不要做完整 issue/PR 系统。
- 不要做 CI/CD。
- 不要做 SaaS billing。
- 不要做 Marketplace。
- 不要做复杂组织邀请流。
- 不要一开始做 SSO。
- 不要为 license enforcement 打断产品体验。

这些会让项目变重，但不会立刻提高核心价值。

## 13. 下一刀建议

下一刀建议直接做：

```text
team-account-workspace-permissions
```

目标不是“做漂亮登录页”，而是让团队协作权限闭环成立。

最小实现：

- admin 手动创建账号。
- admin 设置角色。
- admin 绑定用户到 workspace。
- reviewer 可以审阅候选决策。
- viewer 只能查看。
- 后端接口强制权限校验。
- UI 清楚显示当前账号、角色、scope、workspace 权限。

这做完后，DecisionAtlas 就从“自托管工具”进入“自托管团队产品”。

## 14. 剩余待决问题

这些问题不阻塞 P0，但会影响后续设计：

- 本地仓库导入是读取服务器路径，还是允许上传压缩包？
- token 是否需要加密落库，还是第一阶段只允许环境变量/服务器本地配置？
- 小团队是否需要项目级 reviewer，还是 workspace 级权限已经够用？
- 是否要支持账号禁用后保留审阅历史？
- 是否需要审阅动作二次确认或撤回？

默认建议：

- 本地仓库先支持服务器路径。
- token 第一阶段加密落库或至少不回显，避免只靠 `.env` 变得难管理。
- 权限先做到 workspace 级。
- 禁用账号但保留历史。
- 审阅动作先支持后续 superseded/rejected 修正，不做复杂撤回。
