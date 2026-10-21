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
- [x] Engine 会话绝对有效期及闲置有效期，超时后拒绝访问；兼容 SQLite UTC naïve timestamp，生产配置可调整且有上限。
- [x] 显式 logout 删除服务端 session，API 清 Cookie，前端退出并清理本地状态。
- [x] 账号禁用和管理员密码重置立即撤销该用户全部存量 session。
- [ ] 覆盖已过期、无效、撤销、越权、角色变化的负向回归测试。（已补过期/注销/重置/禁用，角色变化专项仍待验收）

### A2. Browser/Auth 边界 (P0)
- [x] API Origin allowlist，生产默认不允许任意跨域，开发允许显式 localhost Origins。
- [x] 生产认证 Cookie `Secure; HttpOnly; SameSite=Lax`，退出时正确失效；测试开发 HTTP 保留可用。
- [ ] 正确处理 Cookie/Session header，避免默认凭据泄露、无效 token 自动被当作本地 bootstrap。（无效 token 拒绝已实现；localStorage 与服务端 cookie 的完全统一仍待处理）
- [ ] 确认不把 XSS 风险误报为已彻底解决；localStorage Token 搬迁到同源 BFF/服务端 Session 单独评估。

### A3. 私有仓库凭据加密与迁移 (P0 — 放行客户私有仓库前)
- [x] 使用 cryptography.Fernet 认证加密（成熟密码学库，非 KMS）；显式密钥配置与离线轮换、恢复限制已记录。KMS/密钥托管仍属部署责任。
- [x] 仓库统一加密新 Token，全部环境缺密钥 fail-closed；旧明文 Token 不能被应用静默读取。
- [x] 提供可先 dry-run、显式 --apply 与 --include-legacy 的事务性离线迁移命令，失败回滚；迁移前需停止写入并保留受控备份。
- [x] 新增密文落盘、错误密钥、跨 scope、篡改、事务迁移和轮换测试；最终 CI 尚需最新 SHA 验证。
- **无需自制密码学**：cryptography 已锁进 uv.lock；CI、部署密钥管理、备份恢复和运营审查仍是客户部署前的必要验收。参见 [私有 Token 操作手册](../security/private-github-token-encryption.md)。

### A4. 完成门禁
- [ ] Node/API/Web/Engine、TypeScript、E2E、Webhook 签名、OpenSpec strict 和 canonical pre-release 有当前 SHA 证据。
- [ ] 安全复核无匿名管理员、会话复用、跨域凭据、旧 Token 明文读取后门。
- [ ] PR 保持 Draft，**未经用户后续明确授权不得合并 main**。

## 3. 阶段 B：唯一真实仓库价值验证（不增加新功能）

**候选**：`pallets/click`（公开、无私有凭据；实际运行前确认可访问与 PR/issue/文档信号）。不重复使用内置演示 `encode/httpx` 作为主样本。固定 commit/ref、分析窗口、导入模式、模型 provider 与 prompt 配置。

### B1. 环境与可重复运行
- [x] 在 GitHub Actions Windows 隔离 Runner 的 Python Engine 中进行公开仓库试点，记录 commit、测试 bootstrap、Fake Provider、SQLite 健康检查与仓库 HEAD。（非 Web/API/Engine 全栈或客户环境测试）
- [x] 通过实际 GitHub API 导入真实 `pallets/click` 的来源（非 fixture），观察 1,093 条 Artifact，Job `succeeded`，8 候选与 11 条 SourceRef；模型分析使用 Fake Provider，不代表真实 LLM 价值。API 配额和外部用户试验未验证。
- [x] GitHub Actions 上传本次公开仓库 JSON/Markdown 报告（数据库、Engine 原始日志和密钥不上传）；[成功运行 #39554248395](https://github.com/luzay-max/DecisionAtlas/actions/runs/39554248395)。质量评测仍为 `not_run`。

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

## 5. 2026-10-21 本轮阶段进度

- 安全代码与测试已提交到 PR #7 独立分支（会话 TTL/注销/重置撤销、CORS/Origin、生产 Cookie、回归测试）。
- **生产私有 Token 已切换为需显式密钥的密文路径**：不配置密钥或者遇到旧明文都会 fail-closed。已提供迁移/离线轮换工具；实际生产密钥管理、备份恢复与 CI 验证仍未完成。
- **真实仓库候选已核对**：`pallets/click`，固定 Git SHA `2247b35ea1c47c727d7a06e51fa280e12a863ff6`，有 [PR #3877](https://github.com/pallets/click/pull/3877) 和 [#3884](https://github.com/pallets/click/pull/3884) 可核对。详见 [试点操作与 10 个预注册问题](../validation/2026-10-21-pallets-click-value-pilot.md)。
- 这轮仅确认 GitHub 上有可评估材料；**DecisionAtlas Engine 真实导入、人工评分、外部用户试验均未运行**。无法取得可执行真实栈时继续标为 `not_run`，不得改写成 pass。
- 新 CI 尚待当前最新 SHA 验证；中途曾有新增 TS 测试语法错误，已在后续提交纠正。以最新 CI 结果为准。

## 6. 新增云端验证证据（2026-10-21）

- Actions 工作流：`.github/workflows/public-value-pilot.yml`，只在 PR #7 分支按路径推送触发；合入默认分支后才具备正常的 `workflow_dispatch` UI 手动运行入口。当前无需本地环境，可在 Actions 的运行页面重新运行已有 job。
- 第一次运行 [#39553746386](https://github.com/luzay-max/DecisionAtlas/actions/runs/39553746386) 实际 GitHub 数据导入后，SQLite 独立写连接在 extraction progress 汇报时发生 `database is locked`；标记 failed，不包装成 provider 网络失败。
- 修复 `services/engine/app/jobs/import_jobs.py` 中的同 Session commit 行为，并增加 SQLite 未提交候选 + 进度更新的专项回归测试。重新导入 [#39554248395](https://github.com/luzay-max/DecisionAtlas/actions/runs/39554248395) **成功**。
- 本次观测为 `pallets/click`、SHA `2247b35ea1c47c727d7a06e51fa280e12a863ff6`、数据库 Artifact=1,093、候选决策=8、SourceRef=11。统计真实性来自 Actions 上传的 artifact；**数据不是 Fake Provider 捏造的 GitHub 源**，但候选的提取由 Fake Provider 完成，尚未证明真实 AI 价值。
- 当前禁止把导入链路 Pass 当作 20 条人工审核、10 条 Why、5 条 Drift 或安全整改全部完工；这些仍处于 `not_run` / `blocking`。
