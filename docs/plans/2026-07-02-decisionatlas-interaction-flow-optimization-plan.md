# DecisionAtlas 前端交互流程优化计划

日期：2026-07-02

关联 OpenSpec change：`streamline-workspace-interaction-flow`

## 1. 背景判断

DecisionAtlas 当前已经具备主要产品页面：登录、首页、Workspace Dashboard、Review、Search、Timeline、Drift、Governance、Team、Settings、Evidence、Decision Detail。问题不在“有没有页面”，而在“用户该按什么顺序完成工作”还不够清楚。

当前前端更像工程控制台：功能入口很多，但新用户、管理员、审阅者、只读成员、发布操作员看到的是同一套入口。后续产品化应优先优化交互流程，而不是继续增加页面或只做视觉 UI。

## 2. 当前交互流程

```text
未登录 / 登录
   │
   ▼
首页 /
   ├─ Quick Actions: Review / Search / Drift / Team
   ├─ Guided Demo: /workspaces/demo-workspace
   └─ Advanced Controls
        ├─ Provider mode
        ├─ GitHub App
        ├─ Private token
        └─ Live repo analysis
             │
             ▼
          lookup repo
             ├─ 新仓库：start import
             └─ 已存在：open / incremental sync / full rerun
             │
             ▼
Workspace Dashboard /workspaces/[slug]
   ├─ Review candidates
   ├─ Ask why / Search
   ├─ Timeline
   ├─ Drift
   ├─ Governance
   └─ Evidence
```

## 3. 主要问题

1. 首页承担过多职责

首页同时承担产品介绍、demo 入口、导入仓库、provider 设置、GitHub App、private token、下一步导航。对第一次使用的人来说，不像一个清晰任务入口。

2. Workspace 上下文不够稳定

Dashboard 使用 `/workspaces/[slug]`，但 review/search/timeline/drift 主要通过 `?workspace=slug` 传递上下文。用户感知上像在不同工具页之间跳转，而不是在同一个 workspace 内切换功能。

3. 仓库导入不够像核心任务

商业化自托管产品的第一价值路径应该是“导入仓库并看到决策结果”。现在导入在首页高级区里，路径偏隐藏。

4. 角色差异没有充分体现在入口上

项目已经有 admin/reviewer/viewer 权限和 AdminOnly，但导航和首页没有明显根据角色突出不同任务。viewer 看到管理入口会困惑；reviewer 应该直接看到待审阅；admin 应该直接看到导入、账号、配置和证据。

5. Evidence 页面更像脚本说明页

Evidence 当前能展示 guardrail 简要状态，也列出 CLI 命令，但还不像“发布证据中心”。后续应展示 release evidence、benchmark comparison、hosted readiness、guardrail、趋势历史、缺失证据。

6. Decision Detail 的中心地位不够突出

Review、Search、Timeline、Drift 都围绕 decision，但用户钻入一个 decision 后，需要看到来源证据、审阅状态、漂移关系、时间线位置和后续动作。

## 3.1 当前路由与入口清单

| 页面 | 路由 | 当前主要入口 | 交互定位 |
| --- | --- | --- | --- |
| 首页 | `/` | sidebar logo、全局 Home、登录后默认回跳 | 产品介绍、demo 入口、repo 导入、角色化 workbench |
| 登录 | `/login?next=...` | sidebar account surface、权限不足回跳 | 登录并返回原任务 |
| Workspace Dashboard | `/workspaces/[slug]` | Guided Demo、导入完成、workspace sidebar | 当前 workspace 的任务总览和下一步 |
| Review | `/review?workspace=[slug]` | dashboard、sidebar、角色化 reviewer 入口 | 候选决策审阅 |
| Why Search | `/search?workspace=[slug]` | dashboard、sidebar、viewer 入口 | 解释决策原因和证据 |
| Timeline | `/timeline?workspace=[slug]` | dashboard、sidebar、search next action | 决策演化时间线 |
| Drift | `/drift?workspace=[slug]` | dashboard、sidebar、drift next action | 检查决策与治理漂移 |
| Governance | `/governance` | global sidebar、operator 入口 | 治理规则和文档 |
| Team | `/team` | global sidebar、admin workbench | 账号、角色、workspace 成员 |
| Settings | `/settings` | global sidebar、admin workbench | provider 和系统配置 |
| Evidence | `/evidence` | global sidebar、operator/viewer 入口 | 发布证据、guardrail、benchmark、hosted readiness |
| Decision Detail | `/decisions/[id]?workspace=[slug]` | Review、Timeline、后续 Search/Drift 扩展 | 单个 decision 的证据、审阅、来源和下一步 |

## 4. 主流产品交互参照

GitLab 的核心模式是：Project/Group 作为上下文，Merge Request 是审阅、讨论、CI、批准和历史的集中对象。GitLab 文档明确把 Merge Request 描述为团队审阅、讨论和跟踪代码变更的中心。

Jira/Atlassian 的新导航强调 sidebar 中的全局入口、最近访问、收藏、Apps，以及项目/工作区内的导航分层。它的方向是减少跨上下文迷路。

Linear 的概念模型强调 workspace 是容器，issue 是日常工作基本单位，project/view 帮助用户在个人执行、团队计划和跨项目协调之间移动。

NN/g 对复杂应用的建议可以转化为本项目原则：复杂功能可以保留，但必须给用户清晰的信息线索、可恢复路径、稳定对象上下文和角色相关的下一步动作。

参考资料：

- GitLab Merge Requests: https://docs.gitlab.com/user/project/merge_requests/
- Jira New Navigation: https://support.atlassian.com/jira-software-cloud/docs/what-is-the-new-navigation-in-jira/
- Linear Concepts: https://linear.app/docs/conceptual-model
- NN/g Complex Application Design: https://www.nngroup.com/articles/complex-application-design/

## 5. 目标交互模型

```text
Login
   │
   ▼
Role-aware landing
   ├─ Admin
   │    ├─ Setup / Provider
   │    ├─ Import repository
   │    ├─ Team accounts
   │    └─ Evidence readiness
   │
   ├─ Reviewer
   │    ├─ My pending reviews
   │    ├─ Decision detail
   │    └─ Next candidate
   │
   ├─ Viewer
   │    ├─ Workspace dashboard
   │    ├─ Decision search
   │    ├─ Timeline / Drift
   │    └─ Evidence read-only
   │
   └─ Operator
        ├─ Evidence Center
        ├─ Guardrail summary
        ├─ Benchmark comparison
        ├─ Hosted readiness
        └─ Release evidence export
```

## 6. 推荐信息架构

```text
Global
   ├─ Home
   ├─ Workspaces
   ├─ Team
   ├─ Settings
   ├─ Evidence Center
   └─ Governance

Workspace: [slug]
   ├─ Dashboard
   ├─ Decisions
   ├─ Review
   ├─ Why Search
   ├─ Timeline
   ├─ Drift
   └─ Workspace Evidence

Decision: [id]
   ├─ Summary
   ├─ Source evidence
   ├─ Review state/history
   ├─ Drift relationship
   ├─ Timeline position
   └─ Next actions
```

## 7. 推荐实现阶段

### Phase 1：整理入口和上下文

- 明确 Global Navigation 与 Workspace Navigation 的分区。
- 在所有 workspace 工具页显示当前 workspace，并提供回 dashboard 的路径。
- 保留旧 URL，避免破坏现有测试和链接。
- 增加浏览器 smoke，覆盖首页、workspace dashboard、review/search/timeline/drift/evidence。

### Phase 2：角色化首页

- admin 登录后优先看到 setup/import/team/readiness。
- reviewer 登录后优先看到 pending review queue。
- viewer 登录后优先看到 workspace decision discovery。
- operator 登录后优先看到 Evidence Center。

### Phase 3：仓库导入向导

- 独立导入入口：输入 repo。
- access check：公开仓库、私有 token、GitHub App 状态。
- workspace exists：打开、增量同步、全量重跑。
- import progress：显示阶段、失败原因、恢复动作。
- completion：进入 workspace dashboard 并提示下一步 review。

### Phase 4：Decision Detail 中心化

- 将 decision detail 做成跨功能对象页。
- 从 Review、Search、Timeline、Drift 进入 detail 后，都能看到来源和下一步。
- reviewer 操作后提供继续审阅、看证据、回 workspace 三种出口。

### Phase 5：Evidence Center 产品化

- 按 operator 问题组织页面：
  - 能不能发版？
  - guardrail 是什么状态？
  - benchmark 比上次好还是差？
  - hosted readiness 是否完成？
  - 哪些证据缺失或过期？
- 展示 JSON/Markdown evidence 路径和最近归档记录。
- 支持发布材料导出或复制。

## 8. 优先级

P0：Workspace 上下文和导航分层。

这是最基础的交互修复，能立刻降低迷路感。

P1：角色化 landing 和 repository import wizard。

这是商业化自托管产品的第一价值路径。

P1：Decision Detail 中心化。

这是把产品从“页面集合”变成“决策审阅系统”的关键。

P2：Evidence Center 产品化。

这是 operator/release 场景的核心，但可以在 P0/P1 稳定后推进。

P3：Recent、Starred、Command Palette、个性化 sidebar。

这些是效率增强，不应早于主流程重构。

## 9. 验收标准

- 新用户能在 3 步内理解如何导入仓库并进入 workspace。
- reviewer 登录后能直接找到待审阅 decision。
- viewer 不会被管理操作干扰。
- admin 能快速完成配置、导入、成员管理。
- operator 能在 Evidence Center 判断发布证据是否完整。
- 所有 workspace 内页面都能明确显示当前 workspace 和返回路径。
- 浏览器 smoke 覆盖 admin/reviewer/viewer/operator 的核心路径。

## 10. 下一步

建议通过 OpenSpec change `streamline-workspace-interaction-flow` 推进。

第一刀不重做视觉 UI，只做交互流重构：

1. 增强导航分区和 workspace 上下文。
2. 抽出 repository import guided flow。
3. 增加角色化入口。
4. 增强 Decision Detail。
5. 重构 Evidence Center 的信息组织。
