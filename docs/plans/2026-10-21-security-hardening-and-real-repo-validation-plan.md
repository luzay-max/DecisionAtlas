# DecisionAtlas 2026-10-21 安全收口与真实仓库价值验证执行计划

> Status: **ACTIVE / 进行中** · Owner: DecisionAtlas maintainers · Branch: `fix/security-bootstrap-webhook-import-20261021` · PR: [#7](https://github.com/luzay-max/DecisionAtlas/pull/7)
>
> 本计划取代历史路线图作为**当前执行入口**，但不改写历史结果，不代表产品已完成客户验收。

## 0. 基线与目标

- `main` 基线 `36374ce69019290ebf9865543f871c81e5994eaf`；2026-10-21 PR #7 Draft，首阶段 CI `39539935220` success。尚未合并。
- 核心产品路径：公开/私有仓库导入 → 证据支撑的候选决策 → 人工审核 → why-search → drift → 可交付 Code Decision Audit。
- **北极星目标**：一个未参与开发的团队能在受控环境中使用一个真实仓库得到可验证的工程决策价值。
- **明确不做**：新的 SaaS、计费、SSO、Marketplace、通用 IDE 功能和额外 AI 特性。
- 一旦安全收口达到门禁，**冻结新功能开发**，资源转向真实仓库验证与修复验证中发现的阻断 Bug。

## 1. 历史计划检查及归档策略

见 [历史计划归档索引](archive/2026-10-21-reviewed-plan-index.md)。归档采取**逻辑归档**：保留原路径和既有相互引用，不批量挪动、删除、更改历史措辞。文档中的“completed”仅表示当时范围交付，不自动意味着当前分支/外部客户环境验收。OpenSpec 已归档的 change 不重复迁移。Draft PR #2–#6 不可被视为已合入；特别是 #4 → #5 → #6 有堆叠依赖，必须分别评审合并策略。

## 2. 阶段 A：PR #7 第二阶段安全整改

### A1. 会话生命周期与权限 (P0)
- [ ] Engine 会话绝对有效期及闲置有效期，超时后拒绝访问；兼容 SQLite UTC naïve timestamp，生产配置可调整且有上限。
- [ ] 显式 logout 删除服务端 session，API 清 Cookie，前端退出并清理本地状态。
- [ ] 账号禁用和管理员密码重置立即撤销该用户全部存量 session。
- [ ] 覆盖已过期、无效、撤销、越权、角色变化的负向回归测试。

### A2. Browser/Auth 边界 (P0)
- [ ] API Origin allowlist，生产默认不允许任意跨域，开发允许显式 localhost Origins。
- [ ] 生产认证 Cookie `Secure; HttpOnly; SameSite=Lax`，退出时正确失效；测试开发 HTTP 保留可用。
- [ ] 正确处理 Cookie/Session header，避免默认凭据泄露、无效 token 自动被当作本地 bootstrap。
- [ ] 确认不把 XSS 风险误报为已彻底解决；localStorage Token 搬迁到同源 BFF/服务端 Session 单独评估。

### A3. 私有仓库凭据加密与迁移 (P0 — 放行客户私有仓库前)
- [ ] 选用审计成熟的 AEAD 库/KMS；添加显式密钥配置、密钥轮换与灾难恢复说明。
- [ ] 新写入须为密文；生产缺密钥须 fail-closed；读取旧明文记录不能静默在生产使用。
- [ ] 提供可回滚的旧 Token 迁移/重新授权流程，避免已有客户凭据丢失。
- [ ] 添加密文落盘、错误密钥、跨 owner-scope、泄露防护及轮换测试。
- **禁止自制密码学实现**；如果依赖锁文件和可执行 CI 未能完成，A3 维持 blocking，不能宣称可接入真实客户私有仓库。

### A4. 完成门禁
- [ ] Node/API/Web/Engine、TypeScript、E2E、Webhook 签名、OpenSpec strict 和 canonical pre-release 有当前 SHA 证据。
- [ ] 安全复核无匿名管理员、会话复用、跨域凭据、旧 Token 明文读取后门。
- [ ] PR 保持 Draft，**未经用户后续明确授权不得合并 main**。

## 3. 阶段 B：唯一真实仓库价值验证（不增加新功能）

**候选**：`pallets/click`（公开、无私有凭据；实际运行前确认可访问与 PR/issue/文档信号）。不重复使用内置演示 `encode/httpx` 作为主样本。固定 commit/ref、分析窗口、导入模式、模型 provider 与 prompt 配置。

### B1. 环境与可重复运行
- [ ] 在隔离的安全 Demo/真实栈，记录 Engine/API/Web 版本、commit、健康检查、权限设置。
- [ ] 对仓库执行一次真实 GitHub import（非 fake、非 fixture）；记录耗时、GitHub API 配额、导入数、失败数及最新同步时刻。
- [ ] 输出安全、脱敏的 JSON/Markdown evidence 到本地 `.tmp`，只把汇总与复现说明入库；**不可把未运行的计划写成 `pass`**。

### B2. 价值衡量：人为标注而不是“模型自己给自己打分”
- [ ] 抽样 20 条候选决策（不足则全部），两类判定：是否是真实可执行的工程决策、证据能否点击核验。记录接受/拒绝/不确定、引用可靠度。
- [ ] 设计并回答 10 个真实 Why 问题；逐项标注答案正确性、证据充分性、无证据时是否诚实拒答。
- [ ] Drift 采用 5 个真实变更/规则案例评价误报；不具备标注条件时写 `not_provided` 而非计算虚假准确率。
- [ ] 记录非作者用户完成导入→审核→搜索→报告的时间与阻碍；暂无外部用户写 `operator_guided`。

### B3. 退出门禁
- **Go**：完成导入和人工核验，≥70% 抽样候选有真实决策价值且具可核验证据；≥8/10 Why 回答正确且引用真实来源；没有高严重度安全问题。
- **Caution**：质量偏低但能解释/修正；需列出具体样例与影响范围。
- **No-go**：凭据风险、证据伪造/越权，无法导入或为何回答缺可靠来源。进入定向 Bug 修复而非新功能开发。

## 4. 执行记录与发布边界

每次提交更新本计划勾选状态、SHA、CI 链接、明确哪些步骤没有运行。客户私有仓库验证只能在客户控制环境进行，任何 token/源码/私有 Issue 都不得写入公开仓库。2026-10-21 当前仅已验证 Phase 1 CI；Phase 2 和 `pallets/click` 的真实导入必须另行有证据，不能沿用历史的 `encode/httpx` 报告当作本次结果。
