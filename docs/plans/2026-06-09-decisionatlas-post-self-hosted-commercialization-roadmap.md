# DecisionAtlas 后续开发总计划：自托管团队产品完成后的商业化路线

日期：2026-06-09

## 1. 当前状态判断

DecisionAtlas 已经完成从“个人分析工具”到“小团队自托管决策治理产品”的核心闭环。

已完成的主线能力包括：

- 管理员、审阅者、只读成员的团队权限基础。
- GitHub / GitLab / Gitee / 本地仓库接入抽象和 token 写入边界。
- 决策、governance rule、drift alert 的审阅审计记录。
- release evidence、hosted readiness、benchmark comparison、readiness history。
- 离线自托管包、package verifier、operator runbook。
- team handoff report。
- Community / Team Self-hosted / Enterprise Self-hosted 的授权和支持边界。

这意味着下一阶段不应继续堆功能，而应围绕“能被别人部署、理解、验证、购买、续费”推进。

## 2. 下一阶段目标

目标从“功能闭环”转为“可交付闭环”：

```text
真实客户/试点团队
        │
        ▼
拿到离线包和部署文档
        │
        ▼
完成管理员初始化和仓库导入
        │
        ▼
团队审阅候选决策和 drift
        │
        ▼
生成 evidence / handoff / license boundary
        │
        ▼
形成可复盘、可升级、可续费的交付记录
```

## 3. 后续优先级

### P6：干净机器自托管安装演练

目标：证明 package 不是只在开发机上能跑。

范围：

- 用干净目录或新机器执行 package guide。
- 从 `.env`、PostgreSQL、Redis、Web/API/Engine 启动到首个管理员初始化。
- 生成 package verification、release evidence、handoff report。
- 记录真实阻塞项和修复项。

验收标准：

- 非开发者按文档能启动基础服务。
- 能登录管理员账号。
- 能导入至少一个公开 GitHub 仓库。
- 能生成完整 handoff evidence。

难度：中等。主要难点是环境差异和启动脚本稳定性。

### P7：试点客户交付包

目标：把项目变成能给别人看的交付材料。

范围：

- 一页式产品说明。
- 10 分钟演示脚本。
- 试点部署 checklist。
- 交付邮件模板。
- 客户问题 FAQ。
- Community / Team / Enterprise 对比表。

验收标准：

- 不看源码也能理解产品价值。
- 试点用户知道怎么部署、怎么验证、怎么反馈。
- 价格、支持边界、延期能力都讲清楚。

难度：低到中等。重点是表达和包装，不是技术。

### P8：真实仓库质量趋势回归

目标：把“随机真实仓库测试”变成长期趋势，而不是每次手工看结果。

范围：

- 固定 benchmark 仓库池。
- 每次 release 记录 import outcome、candidate count、review-ready ratio、why-search 可用性、drift signal。
- 报告 improved/regressed/blocked。
- 把 local_stack_failure、provider_failure、operator_guided 明确纳入趋势。

验收标准：

- 每次发布能看到质量趋势。
- 回归能被发现，不靠记忆。
- 报告可以进入 handoff evidence。

难度：中等偏高。难点是指标定义和避免噪声。

### P9：权限与审计深化

目标：让团队协作更接近真实小团队使用。

范围：

- workspace 成员管理 UI 打磨。
- 审阅历史筛选和导出。
- 禁用账号后历史保留说明。
- reviewer/viewer 的前后端权限边界回归测试。
- 敏感操作二次确认。

验收标准：

- 管理员能清楚管理成员。
- 审阅责任链可追溯。
- viewer 无法越权导入、审阅、管理 token。

难度：中等。难点是权限边界不能只靠前端。

### P10：备份、恢复、升级实战

目标：让自托管客户敢升级。

范围：

- PostgreSQL 备份恢复演练。
- `.env` 和 entitlement custody 说明。
- 版本升级 checklist。
- 失败回滚记录模板。
- readiness evidence 对比升级前后状态。

验收标准：

- 能从备份恢复。
- 能解释升级失败后怎么回滚。
- handoff report 能引用升级证据。

难度：中等偏高。难点是状态一致性和 operator 文档精度。

## 4. 不建议短期做的事

短期仍不建议做：

- SaaS billing。
- 多租户托管平台。
- Marketplace / 自助 OAuth。
- 企业 SSO。
- 在线 license server。
- 强 runtime license enforcement。
- Git 托管、PR review、CI/CD 替代。

原因：这些会显著增加复杂度，但不会立刻提升小团队自托管的成交能力。

## 5. 建议开发顺序

```text
1. P6 干净机器自托管安装演练
        │
        ▼
2. P7 试点客户交付包
        │
        ▼
3. P8 真实仓库质量趋势回归
        │
        ▼
4. P9 权限与审计深化
        │
        ▼
5. P10 备份、恢复、升级实战
```

优先做 P6 的原因很直接：如果干净环境部署不稳，后面的销售、报告、授权边界都只是文档价值。

## 6. 下一刀建议

下一刀建议：

```text
clean-self-hosted-install-rehearsal
```

最小范围：

- 在干净目录构建/解包 self-hosted package。
- 按 package guide 走一遍启动和验证。
- 记录所有必须人工处理的点。
- 生成 `.tmp/clean-self-hosted-install-rehearsal.json/md`。
- 用浏览器打开本地页面或报告，确认 operator 可以读懂。

这一步完成后，DecisionAtlas 才从“开发者能交付”进入“别人能试点”。

## 7. 成功标准

下一阶段完成的标志不是新增多少功能，而是：

- 一个外部小团队可以按文档部署。
- 管理员能创建账号、导入仓库、分配角色。
- 审阅者能处理决策和 drift。
- 只读成员能查看 why-search、决策、证据。
- 发布前能生成 release evidence、handoff report、license boundary。
- 失败状态会被如实记录，不会被包装成 pass。
- 每次发布能看到真实仓库质量趋势。
