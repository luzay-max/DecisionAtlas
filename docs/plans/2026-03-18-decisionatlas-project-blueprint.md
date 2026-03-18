# DecisionAtlas 项目蓝图

版本：`v0.1`
日期：`2026-03-18`
状态：`Proposed`

## 1. 项目定义

DecisionAtlas 是一个面向工程团队的“决策记忆与漂移检测平台”。

它的目标不是替团队做决定，而是把散落在 GitHub、ADR、设计文档、会议纪要和聊天记录中的“为什么这样做”沉淀为结构化决策对象，并在后续实现偏离这些决策时给出证据化提醒。

一句话定义：

> Turn GitHub, docs and notes into a living decision memory, with citations and drift detection.

## 2. 蓝图目标

这份蓝图服务于两个对象：

- 项目发起人：用来判断这个项目是否值得立项、先做什么、暂时不做什么。
- 执行代理和未来协作者：用来直接进入实现，避免反复讨论抽象方向。

这份文档默认以下现实约束：

- 你不负责底层模型研发，只提供 API key、GitHub 凭据和产品判断。
- 第一阶段以公开仓库演示为主，不先做企业内网接入。
- 第一阶段目标是做出“可跑、可演示、可解释”的 MVP，而不是企业级全套平台。

## 3. 产品边界

### 3.1 产品要解决的问题

- 决策信息分散：关键背景存在于 issue、PR、commit、文档和会议记录中。
- 决策上下文丢失：新人和后来维护者很难知道“为什么现在会这样”。
- AI 回答不可信：没有证据链的总结无法支撑工程判断。
- 决策与实现漂移：历史约束被后续变更悄悄突破，但没人持续检查。

### 3.2 产品不做什么

- 不做通用聊天机器人。
- 不做 Notion/Confluence 替代品。
- 不做开发者 KPI 仪表盘。
- 不做“全自动真理机”，不允许无证据生成结论。

### 3.3 北极星能力

MVP 只证明一件事：

> 系统能够从公开工程资料中恢复关键决策，并用原始证据回答 “why” 类问题。

## 4. 目标用户与核心场景

### 4.1 目标用户

- 独立开发者或小团队维护者
- 新接手仓库的工程师
- 需要追踪架构演化的技术负责人

### 4.2 核心场景

1. 用户导入一个 GitHub 仓库和关联文档。
2. 系统自动抽取候选决策，并生成 Decision Card。
3. 用户搜索“为什么这么设计”并查看带引用的答案。
4. 用户查看某个模块或主题的决策时间线。
5. 当新变更可能与历史决策冲突时，系统给出 `possible drift` 提示。

## 5. 产品分阶段范围

### 5.1 MVP

MVP 只包含以下能力：

- GitHub 导入：Issues、Pull Requests、Commits
- 文档导入：Markdown、ADR、仓库 Wiki 导出文本
- 本地文本导入：会议纪要、聊天导出文本
- 候选决策抽取
- Decision Card 审阅与确认
- Why 搜索
- 带引用答案
- 决策时间线
- 基于规则的第一版漂移提示

### 5.2 明确延后到 V1 之后

- Slack 原生连接器
- Jira / Linear 双向同步
- 组织级权限矩阵
- 多租户 SaaS
- 图数据库
- 自动执行修复建议
- 复杂工作流编排

### 5.3 MVP 成功标准

- 能导入 1 个公开仓库和其文档
- 能稳定生成 20-50 条候选决策
- 用户能在审阅台确认或驳回候选决策
- Why 查询的每个回答至少附带 2 条有效引用
- 能对至少 1 类规则偏移给出提示
- 新用户在 5 分钟内可以本地跑通 demo

## 6. 需求摘要

### 6.1 功能需求

- 导入仓库元数据、Issue、PR、Commit、文档文本
- 对文本分块、归档、索引和关联
- 抽取候选决策及其字段
- 保留决策与原始证据之间的映射
- 支持关键词、全文、向量和关系过滤的混合检索
- 对自然语言问题生成“引用优先”的回答
- 用时间线方式展示决策演化
- 对新 Artifact 执行漂移检测
- 提供人工确认流转：`candidate` / `accepted` / `rejected` / `superseded`

### 6.2 非功能需求

- 易部署：单机 Docker Compose 可启动
- 易解释：所有回答和告警必须有证据来源
- 易维护：服务边界清晰，可单独替换模型与连接器
- 成本可控：默认支持低成本 API 使用，不依赖自训练
- 安全优先：默认本地或自托管，不把私有原文暴露给无权限用户

### 6.3 建议指标

- Web 首屏加载：`< 2.5s`
- Why 查询响应：`< 8s`
- 单仓库首次导入：`< 15min`，按中型仓库估算
- 漂移检测任务：`< 2min` 完成一次增量检查
- LLM 调用失败可重试，不阻塞整个导入任务

## 7. 核心产品设计

### 7.1 Decision Card

Decision Card 是系统里的第一等对象，建议包含：

- `id`
- `title`
- `status`
- `problem`
- `context`
- `constraints`
- `options_considered`
- `chosen_option`
- `tradeoffs`
- `stakeholders`
- `confidence`
- `review_state`
- `created_at`
- `updated_at`

### 7.2 审阅状态

- `candidate`：模型抽取后待人工审核
- `accepted`：人工确认，成为正式决策
- `rejected`：不是有效决策
- `superseded`：被更晚决策替代
- `archived`：历史保留，不再活跃

### 7.3 查询体验

用户输入问题，例如：

- 为什么这个仓库选择 TypeScript？
- 为什么缓存层不允许作为 source of truth？
- 哪些 PR 体现了这个架构转向？

系统输出必须包括：

- 简要回答
- 相关 Decision Card
- 2-4 条 SourceRef
- 引用片段
- 证据不足时的保守提示

## 8. 高层架构

```text
┌─────────────┐
│   Web App   │
│ Next.js UI  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  API Layer  │
│ Node.js API │
└──────┬──────┘
       │
 ┌─────┼─────────────────────────────────────┐
 │     │                                     │
 ▼     ▼                                     ▼
Ingest Service                        Query / Answer Service
Python FastAPI                        Python FastAPI
导入、分块、标准化                      混合检索、组装引用、回答
 │                                           │
 ▼                                           ▼
Extractor Service                     Drift Service
候选决策抽取                           规则检测、语义匹配
 │                                           │
 └────────────────┬──────────────────────────┘
                  ▼
         PostgreSQL + pgvector
     决策、工件、关系、全文、向量索引
                  │
                  ▼
                Redis
          队列、缓存、异步任务状态
```

## 9. 技术选型

### 9.1 推荐选型

- 前端：`Next.js + TypeScript`
- API：`Next Route Handlers` 或 `Fastify`
- 抽取与检索：`Python + FastAPI`
- 数据库：`PostgreSQL + pgvector`
- 队列：`Redis + Dramatiq`
- ORM：`Prisma` 或 `Drizzle` for Node，`SQLAlchemy` for Python
- 模型接入：provider-agnostic，先接 OpenAI 兼容接口
- 部署：`Docker Compose`

### 9.2 关键判断

- 先不上 Neo4j：MVP 的关系复杂度还不值得引入额外运维成本。
- 先不上微服务全拆：逻辑上分层，部署上可先 3 个服务。
- 先不用自训练：现成模型足够支撑抽取、总结和 embedding。

## 10. 数据模型

### 10.1 核心实体

```text
Decision
- id
- workspace_id
- title
- status
- review_state
- problem
- context
- constraints
- chosen_option
- tradeoffs
- confidence
- created_at
- updated_at

Artifact
- id
- workspace_id
- type(issue|pr|commit|doc|meeting_note|message)
- source_id
- repo
- title
- content
- author
- url
- timestamp
- metadata_json

SourceRef
- id
- decision_id
- artifact_id
- span_start
- span_end
- quote
- url
- relevance_score

Relation
- id
- from_type
- from_id
- to_type
- to_id
- relation_type(supported_by|contradicts|implements|supersedes|discussed_in|derived_from)
```

### 10.2 关键原则

- `Decision` 是核心，不以文档页作为主对象。
- 所有生成结果都必须能回链到 `Artifact` 和 `SourceRef`。
- 任何“结论”都不能脱离证据独立存在。

## 11. 核心流程

### 11.1 导入流程

1. 用户配置 workspace 和 GitHub 仓库。
2. 系统抓取 Issue、PR、Commit、Docs。
3. 系统做文本清洗、分块、标准化。
4. 系统写入 Artifact 表，并建立全文和向量索引。

### 11.2 候选决策抽取流程

1. 从新 Artifact 中筛出高价值片段。
2. 调用 LLM 识别是否存在“问题-约束-取舍-结论”结构。
3. 生成候选 Decision Card。
4. 建立候选决策与 SourceRef 映射。
5. 进入人工审阅队列。

### 11.3 Why 查询流程

1. 用户输入自然语言问题。
2. 系统做 query rewrite 和意图判断。
3. 系统执行 hybrid retrieval：
   - 全文检索
   - 向量检索
   - 按 repo / time / decision status 过滤
   - Relation 扩展召回
4. 系统组装证据包。
5. LLM 仅在证据范围内组织答案。
6. 返回回答、Decision Card、SourceRef 和证据不足提示。

### 11.4 漂移检测流程

1. 新 PR 或新文档进入系统。
2. 规则引擎扫描硬约束。
3. 相似检索召回相关历史决策。
4. 语义判断是否存在冲突或替代迹象。
5. 产出：
   - `possible_drift`
   - `possible_supersession`
   - `needs_review`

## 12. 漂移检测策略

第一版坚持“规则优先，语义增强”。

### 12.1 第一层：规则漂移

适合表达为结构化约束的决策，例如：

- 某服务不得直接依赖另一服务
- Redis 只能作为缓存
- PR 必须引用 Decision ID
- 某目录下只能使用特定接口

### 12.2 第二层：语义漂移

对新 PR、Issue 和文档变更执行：

- 与历史决策做相似召回
- 对照 `chosen_option`、`constraints`、`tradeoffs`
- 输出“可能偏移”，而不是直接下定论

### 12.3 为什么这样做

- 规则层可解释、可测试、误报较低
- 语义层增加覆盖面，但不直接做最终裁决
- 两层结合更适合个人项目先落地

## 13. API 与界面草图

### 13.1 主要页面

- Workspace Dashboard
- Decision Search
- Decision Timeline
- Review Queue
- Drift Alerts
- Settings / Connectors

### 13.2 MVP API

- `POST /api/workspaces`
- `POST /api/connectors/github/import`
- `POST /api/connectors/text/import`
- `GET /api/decisions`
- `GET /api/decisions/:id`
- `POST /api/decisions/:id/review`
- `POST /api/query/why`
- `GET /api/timeline`
- `GET /api/drift-alerts`

## 14. 仓库结构建议

```text
apps/
  web/                    # 搜索、时间线、审阅台、设置
  api/                    # 鉴权、REST API、Webhook
services/
  ingest/                 # GitHub / docs / text import
  extractor/              # 候选决策识别与结构化抽取
  retrieval/              # hybrid retrieval + citation assembly
  drift/                  # 规则漂移 + 语义漂移
packages/
  schema/                 # Decision / Artifact / Relation schema
  prompts/                # LLM prompts and evaluation fixtures
  ui/                     # 共享 UI 组件
examples/
  demo-workspace/         # 公共演示数据
docs/
  architecture/           # ADR、架构文档
  plans/                  # 项目蓝图与实施计划
infra/
  docker/                 # Docker Compose、初始化脚本
```

## 15. 部署与运行模式

### 15.1 本地开发

- 使用 Docker Compose 启动 `postgres`、`redis`
- `web/api` 与 Python 服务本地跑
- 通过 `.env` 注入 API keys 和 GitHub token

### 15.2 演示环境

- 单机 VPS 或云主机
- 公开 demo workspace
- 只接公开仓库数据
- 方便录屏、测试和 GitHub 流量转化

### 15.3 后续扩展

- GitHub App Webhook
- 私有仓库接入
- 更细粒度访问控制
- 多 workspace 支持

## 16. 安全与权限

MVP 不做重权限系统，但必须提前留接口。

### 16.1 最低要求

- 敏感凭据只存 `.env` 或安全密钥服务
- 不在前端暴露供应商密钥
- 原始 Artifact 默认不匿名分享
- 引用结果保留 source 级元数据
- 日志避免记录原始敏感文本

### 16.2 权限演进

- MVP：单管理员 workspace
- V1：viewer / reviewer / admin
- 之后：source-level access control

## 17. 风险与规避

| 风险 | 说明 | 规避方式 |
|---|---|---|
| 抽取误判 | 普通讨论被误识别为决策 | 候选制 + 人工确认 |
| 漂移误报 | 语义判断不稳定 | 规则优先，结果只标记为 possible |
| 范围膨胀 | 连接器过多、权限过重 | 只做 GitHub + docs + text |
| 成本失控 | LLM 调用过多 | 分层调用，缓存中间结果 |
| 演示困难 | 用户无法快速看懂价值 | 做公开 demo workspace 和 5 个示例问题 |

## 18. 12 周实施蓝图

### 第 1-2 周：项目骨架与数据模型

- 初始化 monorepo
- 建立基础目录结构
- 定义 schema
- 建立 Docker Compose
- 接入 Postgres 和 Redis
- 选定 demo 仓库

交付物：

- 可运行骨架
- 初版数据库 schema
- 初版项目 README

### 第 3-4 周：导入与索引

- 实现 GitHub Importer
- 实现 Markdown / ADR Importer
- 实现文本分块与 Artifact 入库
- 建立全文和向量索引

交付物：

- 一键导入公开 demo 仓库
- 可查询 Artifact 列表

### 第 5-6 周：候选决策抽取

- 设计抽取 prompt
- 生成候选 Decision Card
- 建立 SourceRef
- 做审阅队列后端

交付物：

- 可从 demo 数据中抽取候选决策
- 可在后台查看候选与证据

### 第 7-8 周：Why 查询与前端

- 完成 hybrid retrieval
- 完成 citation-first answer assembly
- 上线搜索页和决策详情页
- 上线时间线页

交付物：

- 可以回答 5 个高价值 why 问题

### 第 9-10 周：漂移检测

- 实现规则引擎
- 实现语义召回
- 输出第一版 drift alert
- 接入 PR 变化测试集

交付物：

- 至少 1 类有效漂移提示

### 第 11-12 周：演示与发布

- 打磨 README
- 提供 Quick Start
- 补齐 demo workspace
- 准备 benchmark
- 录制 60-90 秒演示视频

交付物：

- 可发布的开源 MVP

## 19. 你需要提供的输入

你不需要研究模型原理，但需要做这些决策和提供这些资源：

### 19.1 必需资源

- `LLM API key`
- `Embedding API key`，如果与 LLM 供应商分离
- `GitHub Personal Access Token` 或后续 GitHub App 凭据
- 1 个公开 demo 仓库链接

### 19.2 必需决策

- 仓库名称最终选择：`DecisionAtlas / ContextLedger / WhyGraph`
- 哪些字段是 Decision Card 的必填项
- 审阅流里的接受标准
- 漂移提示默认是否在 UI 中公开展示

### 19.3 你不需要亲自做的事

- 不需要写抽取逻辑
- 不需要写搜索或向量检索代码
- 不需要手工搭基础架构

## 20. 开工前的关键 ADR

建议在实现开始前先确认 4 个 ADR：

### ADR-001：MVP 使用 PostgreSQL + pgvector，不引入图数据库

理由：

- 部署简单
- 工程门槛低
- 足够支撑全文、关系和向量混合查询

### ADR-002：系统以 Decision 为核心对象，而不是文档页

理由：

- 有利于从“知识页面”升级为“可追溯决策”
- 便于做时间线和漂移检测

### ADR-003：回答策略采用 citation-first，不允许无证据自由生成

理由：

- 建立可信度
- 降低幻觉风险
- 符合工程场景的高责任要求

### ADR-004：漂移检测采用规则优先、语义增强

理由：

- 误报更可控
- 更容易向用户解释为什么触发

## 21. 立即执行顺序

如果今天开始做，顺序应该是：

1. 初始化仓库和 monorepo 骨架
2. 建立数据库 schema
3. 实现 GitHub + Markdown 导入
4. 打通候选决策抽取
5. 打通 Why 查询
6. 再做审阅台和漂移检测

不要倒过来从聊天、复杂 UI 或全连接器开始。

## 22. 结论

DecisionAtlas 是一个对个人开发者依然可行、同时又具备职业辨识度的项目方向。

它真正难的地方不是“大模型”，而是范围控制、数据建模、引用链和产品闭环。只要坚持以下原则，这个项目是可落地的：

- 先做公开演示闭环
- 先做人审，不追求全自动
- 先做 citation-first，不做会聊天但不可信的系统
- 先做规则漂移，再逐步加语义能力

这份蓝图可以直接作为后续实现计划、README 初稿和 ADR 的上位依据。
