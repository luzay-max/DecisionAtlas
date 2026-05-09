# DecisionAtlas 商业化与产品化计划

日期：2026-05-09  
定位：本地部署 / 私有部署优先的代码决策治理软件  
当前建议路线：`Community 免费版 + Team Self-hosted 年费版 + Enterprise 私有部署/支持版`

## 一句话结论

DecisionAtlas 不适合一开始做完整 SaaS，也不适合做永久买断。更合适的路线是：

- 先把它做成像 Sentinel / Nacos 那样可以本地部署的基础设施软件。
- 用免费 Community 版降低试用门槛。
- 用 Team Self-hosted 年度授权收费。
- 用 Enterprise 私有部署、离线部署、支持和培训提高客单价。
- 等客户需求稳定后，再考虑 hosted managed service。

## 为什么不先做 SaaS

当前项目已经有 release evidence、hosted readiness、benchmark history、governance guardrail 等交付证据，但还没有完整 SaaS 必需的能力：

- billing
- 多租户组织管理
- 自助 OAuth / Marketplace 安装
- 企业级 secret vault
- 统一 SLA 运维
- 在线成本控制
- 多客户隔离和审计

如果现在直接做 SaaS，会把大量时间花在账户、计费、权限、运维、合规上，反而拖慢核心产品价值验证。

## 为什么不做永久买断

买断制看起来简单，但对这个产品风险很高：

- 客户部署环境复杂，后续支持压力不会因为买断结束。
- 私有仓库、模型 provider、GitHub App、数据库、队列、权限都会带来持续问题。
- 一次性收入无法覆盖长期升级、兼容和支持成本。
- 早期产品还在迭代，永久授权会限制未来定价。

因此可以叫“私有部署版”，但商业上应按年收费。

## 推荐产品分层

### 1. Community

目标：让开发者和小团队能低成本试用。

建议免费。

能力边界：

- 本地 Docker Compose 部署
- 单 workspace 或少量 workspace
- public repo 导入
- 基础 decision extraction
- 基础 why search
- 基础 drift detection
- 基础 governance report
- 手动运行 release evidence
- 无官方 SLA

限制：

- 不承诺生产支持
- 不包含团队权限
- 不包含企业私有部署支持
- 不包含高级 evidence history / benchmark trend 自动化

### 2. Team Self-hosted

目标：给小团队、独立产品团队、研发团队使用。

建议按年收费。

候选价格：

- 国内：¥1999 - ¥9999 / 年
- 海外：$299 - $999 / 年

能力边界：

- 私有仓库支持
- 多 workspace
- release evidence history
- benchmark regression history
- governance rule lifecycle
- Markdown / JSON 报告导出
- 基础角色权限
- 升级说明
- 邮件或群支持

适合客户：

- 小型软件公司
- 技术咨询团队
- 需要维护多个代码库的独立开发者
- 有架构/决策治理需求的研发小组

### 3. Enterprise Self-hosted

目标：给更重视数据隐私、审计和内部部署的大客户。

建议按年收费，另收部署服务费。

候选价格：

- 国内：¥30,000 - ¥200,000 / 年
- 海外：$5,000 - $30,000 / 年
- 代部署服务：¥5,000 - ¥30,000 / 次

能力边界：

- 离线部署
- 私有网络部署
- SSO / SAML / OIDC
- RBAC
- 审计日志
- 备份恢复
- 企业级报告模板
- 定制 connector
- 部署培训
- SLA 支持

适合客户：

- 中大型研发团队
- 安全要求高的企业
- 需要治理遗留代码库的组织
- 技术咨询公司服务客户时使用

## 商业模式路线

```text
阶段 1：产品可试用
Community 本地部署
        │
        ▼
阶段 2：有人愿意付费
Team Self-hosted 年费
        │
        ▼
阶段 3：高客单价
Enterprise 私有部署 + 支持
        │
        ▼
阶段 4：可选
Hosted Managed Service
```

核心原则：

- 先卖 self-hosted，不先卖 SaaS。
- 先卖年费，不卖永久买断。
- 先卖交付结果，再卖平台能力。
- 先服务少量真实客户，再扩展 pricing。

## 免费版和付费版边界

付费点不应该是“把核心功能锁死”，而是让团队能放心用。

### 免费版给什么

- 能跑起来
- 能体验核心价值
- 能看到决策抽取、why search、drift 的效果
- 能跑 demo workspace
- 能处理 public repo

### 付费版给什么

- private repo
- 多 workspace
- 团队协作
- 长期 evidence history
- benchmark trend
- release handoff
- governance lifecycle
- 报告导出
- 部署升级支持
- 企业安全能力

## 最小可卖版本

第一版可卖版本不需要完整 SaaS，只需要做到：

- 一条稳定的 Docker Compose 部署路径
- 一份快速开始文档
- 一个 public repo demo
- 一个 private repo operator guide
- 一键生成 release evidence
- 一键生成 hosted/operator readiness
- 一键归档 readiness evidence history
- 一份客户可读的“代码决策治理报告”
- 明确 Community / Team / Enterprise 边界

最小可卖版本的目标不是“所有人自助购买”，而是“你能给第一个真实客户部署并交付价值”。

## 第一批客户怎么卖

不要先说“我有一个平台”。先说结果：

- 我可以帮你分析一个真实代码库。
- 找出代码库里的关键技术决策。
- 解释这些决策为什么出现。
- 检查哪些决策可能已经漂移。
- 输出一份可复核的治理报告和 release evidence。
- 如果有价值，再部署成团队内部工具。

第一批服务可以包装成：

### Code Decision Audit

交付物：

- 代码库决策地图
- 关键架构决策列表
- drift 风险报告
- why search 示例
- release evidence
- 后续治理建议

收费建议：

- 小项目：¥3,000 - ¥10,000
- 中型项目：¥10,000 - ¥50,000
- 企业试点：¥50,000+

这个服务的作用是验证客户是否愿意为“代码决策治理”付费。

## 12 周产品化路线

### 第 1-2 周：打包 self-hosted 基线

- 梳理 Docker Compose 部署路径。
- 明确本地部署最低依赖。
- 写 Community 快速开始。
- 写 Team/Enterprise 能力边界。
- 准备一个 public repo demo。

验收标准：

- 一个新用户能按文档在本地跑起来。
- 能导入 demo repo。
- 能生成基本报告。

### 第 3-4 周：做可销售交付物

- 设计 Code Decision Audit 报告模板。
- 把 release evidence / readiness evidence history 转成客户可读材料。
- 准备销售页草稿。
- 准备一页式产品介绍。
- 准备 3 个典型使用场景。

验收标准：

- 可以给潜在客户展示一份完整样例报告。

### 第 5-6 周：私有仓库试点

- 跑 1-2 个真实 private repo。
- 记录部署难点。
- 记录客户真正关心的问题。
- 收集报告是否有价值的反馈。

验收标准：

- 至少完成一次真实客户或真实项目的私有仓库诊断。

### 第 7-8 周：Team Self-hosted 定价试验

- 明确 Team 版功能边界。
- 加入基础 license 说明。
- 准备年度授权合同/条款草稿。
- 准备升级和支持说明。

验收标准：

- 可以正式报价 Team Self-hosted。

### 第 9-10 周：Enterprise 准备

- 明确离线部署边界。
- 明确备份恢复流程。
- 明确安全和隐私说明。
- 明确支持 SLA。
- 准备部署服务报价。

验收标准：

- 可以和企业客户讨论私有部署。

### 第 11-12 周：复盘是否进入 hosted

判断是否需要做 hosted managed service：

- 是否已有客户要求“你来帮我托管”？
- 是否已有稳定 onboarding？
- 是否付费转化受部署门槛影响？
- 是否有足够时间维护线上服务？

如果答案不明确，就继续强化 self-hosted，不急着 SaaS。

## 暂时不做

短期不优先：

- billing
- 多租户 SaaS
- Marketplace 上架
- 自助 OAuth 安装
- 大规模 connector 市场
- 复杂管理后台
- 永久买断授权

这些不是永远不做，而是不应该压过当前最重要的目标：先让 self-hosted 产品可卖。

## 当前最重要的下一刀

建议下一个 OpenSpec change 做：

`package-self-hosted-commercial-baseline`

目标：

- 梳理 Community / Team / Enterprise 能力边界。
- 增强 Docker Compose / 本地部署文档。
- 加入 license / support / limitation 说明。
- 准备一个客户可读的 self-hosted 试用路径。
- 不做 billing，不做 SaaS，多租户只保留当前 owner-scope 能力。

## 成功标准

未来 1-2 个月内，如果做到下面这些，就说明商业化路线是对的：

- 至少 3 个真实代码库完成诊断。
- 至少 1 个用户愿意为报告或部署付费。
- self-hosted 部署能在非你本人机器上跑通。
- 客户能理解“决策治理 / drift / release evidence”的价值。
- 你不需要为了每个客户改一堆定制代码。

## 最终判断

DecisionAtlas 应该走：

```text
本地可部署基础设施软件
        +
Open-core / source-available 商业授权
        +
年度维护费
        +
可选代部署和企业支持
```

不要急着做完整 SaaS。  
不要卖永久买断。  
先卖 self-hosted 的可信交付结果。
