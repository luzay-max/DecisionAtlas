# DecisionAtlas 后续开发执行计划：可信证据 → 真实价值 → Agent 闭环

> **状态：PR #37 仍为 Draft；本文是持续更新的执行路线图，单项任务状态以第 13 节的固定 SHA / CI / 审批记录为准。路线图本身不构成任何代码合并、迁移或生产操作授权。**  
> **制定：2026-10-30。基线：`main@8aa461f5bc30f16e023c9c00f0d641794fd16f86`。**  
> **适用范围：** 后续开发的统一待办入口；分支 / PR / CI / 人工验收按本文逐项推进。本文仅是计划，**没有修复任何生产代码、没有合并任何 PR、没有授权任何付费 LLM 请求或真实私有数据处理**。  
> **历史材料：** [仓库内部 2026-10-28 深度审查](../reviews/2026-10-28-strategy-architecture-code-ui-review.md)、[2026-10-21 安全与真实仓库计划](2026-10-21-security-hardening-and-real-repo-validation-plan.md)、[历史计划归档索引](archive/2026-10-21-reviewed-plan-index.md)；另结合维护者提供的两版《DecisionAtlas 深度分析与迭代建议》（2026-10-30，第二版增加第 15 节）。外部评审是**问题线索与建议**，并非已独立验证的验收凭据；须以固定代码基线和回归结果复核。  
> **维护原则：** 每次开始新任务，先核对 `main`、在途 PR 和本表状态；已合并并满足验收门槛才可将任务标记完成。旧计划保留作为历史，不重写历史“已完成”断言。

## 0. 一页执行决策

**产品定位（建议）：** Evidence-first Engineering Decision Memory —— 从代码托管仓库的历史及讨论中发现**候选**工程决策，给出可核对的原始证据，由人审核形成可信的决策记忆，再供 Web / CLI / MCP / ADR 使用。

**本轮唯一优先主线：**

1. **可信：** 凭据与导入事务安全、完整覆盖、同步水位、历史证据不可被静默改写、审核与漂移处置不丢失。
2. **有用：** 补全评论和 PR review 信号，真实模型 + 人类标注验证候选精确率 / 可恢复 ADR 召回 / Why 引用质量。
3. **可用：** 中英文检索、可理解的审核流程、一键试用与可迁移 ADR、只读 Agent 入口。
4. **可维护：** 契约测试、Linux + PostgreSQL CI、明确持久化任务语义、可观测性与真实部署说明。

**本轮不做：** 删除 Fastify / 改写整套栈；把低可信 LLM 判断当治理阻断；全面重做漂移规则引擎；在没有真实质量数据前拓展收费、SaaS、多租户计费或海量接入源；为了“使用 pgvector”而无评测地改数据库；无结论地清空历史文档。已有 Web、漂移、治理、权限保持原状并按证据渐进改进。

**交付原则：** CLI 负责启动和自动化；Web 是人工证据审核台；MCP/ADR 负责交付给开发者与 Agent。默认只暴露 **accepted** 决策，治理建议不阻断、不自动批准。

## 1. 任务状态、优先级与验收口径

- **P0：安全 / 不可恢复数据完整性风险**。在相关功能继续扩展前先处理。
- **P1：核心可信链路缺陷或首次价值阻塞**。当前开发主线。
- **P2：成本、体验和中期维护改进**。与主线绑定，不抢占 P0/P1。
- **Proposed** = 未开始；**Draft PR** = 实现仅在在途分支，主分支尚无；**Merged-unverified** = 已合并但必要验收缺失；**Done** = main 中已实现且通过明确门槛；**Deferred** = 有条件后置。
- 任务表为**建议执行顺序，不是日历承诺**；若前置条件未满足，后续阶段不应以“并行开发”绕过安全和质量闸门。
- **每个代码 PR** 必须列明：任务 ID / 固定 base SHA / 改动范围 / 非目标 / 风险与回滚 / CI 结果 / 未验证事项 / 所需人工验收。单 PR 尽量只覆盖一个可独立验收问题；有堆叠依赖的明确标注。
- 合并门禁：最新 head CI 通过；必要的跨层、生命周期、权限/数据隔离测试通过；维护者完成代码评审；无新的凭据泄漏、审核历史被改写、错误成功状态；文档与实际能力一致。**CI 绿不等于真实用户价值、私有部署或真实模型已验证。**

## 2. Stage A — 收敛已有 Draft PR，先止血（优先执行）

> 这里是“处理**已有**改动”的顺序，不新开一批重复修复 PR。截至本文基线，#26、#28–#35 均为未合并 Draft（请在执行前重新检查状态）。不可将 Draft 功能算作 main 已有能力。

| ID | 优先级 | 现有 PR / 问题 | 建议行动与合并顺序 | 验收与剩余边界 |
| --- | --- | --- | --- | --- |
| A01 | P0 | [#26](https://github.com/luzay-max/DecisionAtlas/pull/26) / K01 | 审查跨源下载 Authorization、Cookie、client auth/redirect 隔离与进度回调事务；优先独立确认并合并 #26 | 私有/公开 mock raw 下载无凭据外泄；导入失败没有已提交的半截 Artifact；当前 SHA 的 CI、失败测试与人工安全审查完成 |
| A02 | P1 | [#35](https://github.com/luzay-max/DecisionAtlas/pull/35)（**base 是 #26 分支**）/ F04、F05、F14 部分 | #26 进入 main 后重新评估 #35 差异、rebase/retarget 到 main 并验证；#35 已集成 #30 和 #31 的主要改动，先对照差异，**不得把 #30/#31/#35 作为互不重叠的三个 PR 直接逐个合并** | 分页继续 next、后页 422、tree 截断 fail-closed；失败不推进成功水位，进度事务不留部分 Artifact；开始时间+重叠窗口的回归；SQLite 暂停并发、孤儿任务人工恢复检查。**不宣称已拥有通用 durable worker、租约或自动重启恢复** |
| A03 | P1 | [#28](https://github.com/luzay-max/DecisionAtlas/pull/28) / F01、F02 | 独立审核 Web → BFF → Engine 的 pause/resume 转发、scope SessionDTO 和失败反馈；可在 A01/A02 期间并行审查，合并时以最新 main 重跑 CI | 200/400/403/404/409 及重复点击、权限切换、跨 scope 数据失效、网络错误有契约/E2E 回归；暂停不保证中途任意指令即时中断 |
| A04 | P1 | [#29](https://github.com/luzay-max/DecisionAtlas/pull/29) / F03、F07 | 审核重复检测保留人工处置、空内容清索引的修复；补一条 **resolved 后信号消失再出现** 的行为测试或登记明确 follow-up，再决定合并 | `false_positive` / `acknowledged` 对相同事实保持状态；空→非空索引替换正确；审计 ID 不丢。注意同一告警键缺版本/发生周期，**不要把重复出现等同真正回归** |
| A05 | P1 | [#32](https://github.com/luzay-max/DecisionAtlas/pull/32) / F06a | 审查当前 quote 在最新 Artifact 中的匹配诊断，作为只读警告优先落地 | `current_quotes_found / current_quote_missing / unverifiable / no_refs` 的列表与详情一致；审核记录不被改变；“文本现在存在”**不是历史快照或来源真实性证明** |
| A06 | P1 | [#33](https://github.com/luzay-max/DecisionAtlas/pull/33)、[#34](https://github.com/luzay-max/DecisionAtlas/pull/34) / F06b | **先审 RFC、再审迁移原型**；单独决定旧 SourceRef 不可追溯版本如何表达、hash 规范、数据库兼容、并发写入、隐私保留和回滚。#34 是**schema-only**，不应越过这些闸门启用运行时代码 | SQLite 与 PostgreSQL 迁移验证；旧审核引用保持 legacy-unbound、不可虚构历史快照；FK/唯一性约束与升级安全；禁止无条件自动重抽取或“看似成功”的 backfill |

**A02 的重复 PR 处理路线：** 优先选择“#26 → 整合后的 #35（经核实包含 #30/#31 的所需语义）”；对照 #30、#31 的测试和行为是否全部覆盖，仅在确认不丢功能/历史记录后再关闭或标记 superseded。若 #35 因并发修改风险不宜整体合并，则拆出安全、覆盖、水位、恢复的小 PR；不得盲目 cherry-pick 两套导入逻辑。**本文不自动合并、关闭或改动任何既有 PR。**

**Stage A 出口：** 维护者记录各 PR 的最终去向（merged / revised / deferred / superseded）、最终 commit SHA、相关 CI URL、已知残余问题；有一份可追溯的 main 回归结果。任何对 SQLite 锁竞争的测试只能算“已复现”，不能记为“已经解决”。

## 3. Stage B — 核心工程质量和检索可靠性（Stage A 安全收口后）

| ID | 优先级 | 目标与建议改动 | 测试 / Done 闸门 |
| --- | --- | --- | --- |
| B01 | P1 | F08/N6：决策 Embedding 按决策内容版本/模型/维度缓存，更新时失效；查询只 embed query、验证向量维度/有限值；先小数据集有界方案，再根据真实规模决定 PostgreSQL pgvector/HNSW | 同查询重复执行不重算未变决策；更新版本正确失效；不同模型、维度拒绝混用；测 p95 延迟/调用数与迁移兼容性 |
| B02 | P1 | F09：中文/中英混合检索（字符 bigram + 英文技术词；或 FTS5/PG FTS 对照）和词法 fallback；真实向量不可用时不让 FakeEmbedder 伪装生产语义召回，响应明示 retrieval_mode | 至少覆盖纯中文、混合技术词、英文与负例；对比 recall@k、错误命中和拒答；只证明词法失败的部分，不捏造端到端中文命中率 |
| B03 | P1 | F10/F13：修复浏览器请求 `127.0.0.1:3001` 的远程部署风险；建立同源代理或经验证的公开地址策略；修复非法 Cookie 百分号转义解析，避免单个坏 Cookie 影响所有请求 | 远程浏览器访问正确 API；本地 demo 不回归；安全 Cookie、非法 Cookie、401/403、CORS/CSRF 边界的接口和浏览器测试 |
| B04 | P1 | N4：在既有 Windows CI 外增加 Ubuntu + PostgreSQL 真实集成作业；校验 SQLite 和 PG 的迁移、索引/证据/导入事务行为。任何尚未使用的 pgvector/Redis 在文档里标为“安装但未接入” | 两个平台 CI 绿；真实 PG 测试而非仅换 connection string；必要时矩阵拆分快慢作业，不让 Fake tests 冒充真实服务 |
| B05 | P1/P2 | N5：Argon2id 优先（或经审核的 scrypt），新 hash 格式版本化；旧 PBKDF2 登录成功后迁移重哈希，采用安全比较；权限与密钥迁移回归 | 旧账号可登录并无损升级；错误密码/畸形 hash 不泄露细节；不会改变 Fernet GitHub token 加密/轮换语义 |
| B06 | P1 | F15：按独立切片完成 Engine OpenAPI → TypeScript 契约：B06a 路由清单、B06b Why DTO、B06c Decisions DTO、B06d Imports/Auth/Team DTO、B06e 统一错误格式与环境配置校验；保留 Fastify BFF | 每个切片独立 PR、生成类型 freshness、Engine 运行时响应模型、BFF 调用与 Web 类型一致；引用/审核状态/空值/权限不回归；UI 区分错误类别；配置错误启动时明确失败。不得把已完成的 a/b 误记为整个 B06 完成 |
| B07 | P1（专项设计） | F14：设计 DB jobs 租约/心跳/claim/进程重启协议，或成熟任务队列；先定义原子暂停与重试幂等语义，不在未验证时自动重放导入、审核或付费抽取 | 模拟 worker 终止/重复执行/并发 pause-resume；确保不会重复提交或无界扣费；人工恢复只在确认 worker 停止后触发 |

**依赖选择：** 在 B07 做出后台任务方案之前，不急着删除 Redis；如果最终采用 DB 队列，移除无用 Redis 与 Compose/README 声明；若用 Redis 队列，就真正接入并有崩溃恢复测试。pgvector 同理：用真实性能与维护成本决定，不靠架构图决定。

## 4. Stage C — 输入与证据完整性（证明核心价值的前置条件）

### C01 — N1：GitHub 讨论评论采集（P1，建议独立 PR 切片）

- 按来源区分 Issue comments、PR conversation comments、PR review summaries、PR review inline comments；保留稳定 ID、thread/parent 关系、作者、created/updated、原文 URL/锚点以及可见的采纳/合并状态。**讨论中的建议不等于已采纳架构决定**。
- 初始范围限 GitHub 公共仓库的只读采集；复用现有 GitHubClient/import job/Artifact 等模型，不直接开 GitLab/Gitee、Slack/Jira 的并行项目。
- 分页上限、API 错误、删除/编辑、率限制、增量与重试须与 F04/F05 一致；每个数据流覆盖、游标、水位和失败情况独立记录。超过范围应明确 partial 或 fail-closed，不能静默成功。
- 线程上下文保留赞成/反对/最终决议；长线程先安全截断和标记上下文缺失；不把评论正文里的 prompt 指令当系统指令。
- **Done：** 公共 fixtures + mock HTTPX 覆盖分页、review/inline、评论更新、去重、权限、安全边界；真实公开仓库 dry-run 的捕获数量、覆盖率、成本报告；可证明评论与原 PR/Issue 来源关联正确。
- 后续私有仓库导入必须有**显式授权、脱敏/保留策略和人工安全验收**；不得把源文本、Token 或人名直接上传到 CI artifact。

### C02 — F06：真正不可变的来源与审核链（P1）

- 以 #33 RFC / #34 迁移为参考，阶段实施 ArtifactRevision、SourceRef 修订关联、当前指针、删除墓碑和 revision-scoped extraction outcomes。
- 原有 accepted/rejected 审核、Quote、ReviewAuditEvent 永不因重新导入被静默改写；旧资料没有历史版本时返回 **unverifiable / legacy-unbound**，不在迁移时假造。
- 只对**新版本**生成候选或“需复审”，不自动替人重新接受；导入缺失不得直接认定上游删除。
- **Done：** v1→v2→删除→恢复、同时重导入、旧 Schema 迁移、失败回滚、跨 workspace 权限隔离和私有快照保留策略均有测试；新旧证据在 UI/API 中可区分。

### C03 — 抽取质量与提示注入防护（P1）

- 保留当前“候选筛选→结构化抽取→可定位 SourceRef→人工审核”的基本设计；新增线程上下文抽取、合并重复候选、采纳/否决/取代信号分层。
- 使用明确分隔的不可信来源数据区、结构化 schema、长度上限、失败重试上限；防止来源文本中“忽略指令”等内容污染提取过程。引用逐字定位不等于语义支持，更不等于来源真实性。
- 报告每 100 条 source 的时间、Token、费用**估算**与失败率；模型、Prompt、输入快照和版本与结果绑定；对模型供应商/付费额度先获得维护者批准。
- **Done：** prompt injection 与负样本回归；低证据候选不自动接受；按来源类型报告拒绝原因及重复候选比例。

## 5. Stage D — 建立真实评测门禁（C01 有基线后优先完成）

> 评测不是宣传材料；在没有通过之前，不得把 FakeProvider 结果、“运行了 452 个单测”或 ADR 存在与否当成抽取精度证明。**先做小样本核实，再扩大样本**。

| ID | 项目 | 样本与指标 | 评测注意 |
| --- | --- | --- | --- |
| D01 | 候选精确率 | 3–5 个真实公开仓库，每库前 50 条候选；人工独立判断是否是真决策、是否采纳、证据支撑、是否过期；precision@10/@50，分源报告 | 至少两名标注者独立评审，有分歧记录/仲裁；条件不足时显式“待第二标注者”，不能假称人工金标准 |
| D02 | ADR 可恢复召回 | 输入剔除 ADR/重复设计文档；对“公开历史中可恢复”的 ADR 做 recall@N | 金标准先分“有公开证据/无公开证据”；避免将不可恢复项目算失败，防止既有模型训练资料泄漏影响解读 |
| D03 | Why 与引用 | 每仓 20–30 个为什么问题，中英各半和拒答负例；recall@5、引用正确率、拒答正确率、p95 延迟、token | 只针对 accepted，不能用候选或 FakeEmbedder 制作看似真实的成绩 |
| D04 | 评论价值消融 | 同样的仓库/模型/Prompt/预算对比“有评论 vs 无评论” | 看精确率、可恢复召回、审核耗时和增量成本；不要只比较候选数量 |
| D05 | Agent 应用实验 | 选可重现的 diff 修改任务，测“无决策上下文 vs MCP 提供 accepted 证据”的历史决策冲突率 | 先只读和提示、不阻断；比较相同任务、控制可见上下文、人工核对结论 |

**验收输出（存 `docs/validation/` 或合适目录）：** 固定仓库 SHA、采集覆盖/截断状态、模型/Prompt/Embedding 版本、样本定义、标注规则与分歧、指标计算脚本、成本、限制与可复现命令。敏感数据不得提交；公开仓库结果也要最小化保存个人信息。

**Go / No-Go 决策：** 指标门槛应在基线评测前预登记并由维护者签字；报告中“10 分钟 5 条决策 / 审核 60 秒 / 30% precision / 3/10 留存”仅为候选目标，**不是强制承诺**。若真实抽取质量差、评论改善有限，考虑缩小到“针对 PR / diff 辅助起草 ADR”，而非继续堆界面功能。

## 6. Stage E — 完整产品闭环与开源可用性（通过 D 的价值门禁后）

| ID | 交付切片 | 范围与非目标 | 验收 |
| --- | --- | --- | --- |
| E01 | ADR 导出 / 回写 | accepted → MADR Markdown + frontmatter、证据引用、来源版本、状态；先本地导出，再可选 GitHub PR。未经用户确认不直接写入目标仓库 | 幂等输出、可读 diff、不会泄露私有来源、不会把候选当已接受；外部 ADR 工具可读取 |
| E02 | MCP 二期 | 继续只读 accepted，补 `applicable_to(path/diff)` 返回适用决策及证据；保留 owner scope 与 loopback/授权边界 | 用真实 MCP host 验证权限、错误、路径作用域、引用定位，不把基础 SDK in-process 测试当宿主联调 |
| E03 | GitHub Action / PR 提醒 | 在 PR 中提示相关历史决策，默认 advisory，不自动 block、不自动批准 | 与手工 diff 对照，提供证据链接；误报、无匹配和局部数据覆盖均可解释 |
| E04 | 审核台 UX | 证据/原文并排、一键接受/拒绝/合并、键盘快捷键、错误恢复、评论上下文、证据版本变化提示 | 做真实浏览器 + 键盘/移动端测试；量测审核耗时与错误操作，禁止无依据“高置信”装饰 |
| E05 | UI 可信语义 | F11/F12：拓扑图由真实关系驱动或明确标注示意；“pause”展示必须说明是**建议状态还是实际执行** | 不将服务自身仓库的治理检测误说成用户仓库已暂停，不将时间顺序误画成架构依赖 |
| E06 | 开源试用与发布 | 一条命令试用（优先 SQLite、可选 PG）；清晰的 Fake demo vs 真模型标识；英文/中文 README、真实可复现 Demo 和贡献者入口 | Windows/Linux 干净环境验证、无 Key 能跑示例、有 Key 能在获批准范围跑真实公开仓库；部署组件与 README 一致 |
| E07 | 生态扩展（Deferred） | [#15](https://github.com/luzay-max/DecisionAtlas/pull/15) / [#16](https://github.com/luzay-max/DecisionAtlas/pull/16) GitLab/Gitee 仍为独立堆叠 Draft；付费/企业能力按外部反馈后再决定 | 先确认 GitHub 真实质量闭环及依赖安全，再重审是否扩大平台；不在此计划中自动合并旧 Draft |

## 7. 技术设计中的保留与禁止事项

1. **保留 Fastify BFF 当前职责**（会话、Cookie、权限/Scope 边界），优先 OpenAPI 生成类型与契约测试。只有测得确切重复开发成本并通过认证迁移设计评审，才讨论并入 Next.js。
2. **保留漂移与治理作为可选、保守能力**。优先“这次改动涉及哪些已接受决策”，确定性规则只覆盖能从 diff 判定的类型；`continue/caution/pause` 不自动执行阻断。#29 修复重复处理后，另外设计 signal observation / disposition 分离：同事实重复扫描不重开；`resolved` 的事实消失后再次出现、或新 revision 出现时才按策略重新发告警并保留历史。
3. **SQLite 为开发/单实例试用的一等公民，PostgreSQL 为已验证的扩展**；不要把 SQLite 多进程并发与 Pg 锁模型混为一谈。后台任务可靠性方案确定后再决定 Redis 去留。
4. **来源边界优先**：任何未合并 PR、Issue 中反对意见、未证实评论、Fake LLM 结果都只能是候选信号；必须保留审核人、来源、时间和“无法核实”状态。
5. **安全第一**：Token/个人数据不得写测试输出、日志、快照或 PR 描述；真实私有仓库/付费模型/对外托管部署必须分别经维护者批准，使用最小权限与有界成本。
6. **去掉虚假的能力宣称**：pgvector 未接入就不要声称“pgvector 检索”；Redis 未协调任务就不要画成协调层；未验证的 Linux/PG、真实模型、MCP 宿主、UI 不得标已通过。

## 8. 给接手开发者的下一步任务顺序（可直接按顺序执行）

1. [ ] **确认基线：** 获取当前 main SHA、所有开放 PR 的 base/head/CI。与 Stage A 表对照并标出过期内容；不修改尚未审过的其他 Draft。
2. [ ] **A01：** 审 #26 安全、事务及回归；CI + 人工风险检查后才提出合并建议。
3. [ ] **A02：** 以 #26 为基线审 #35 的 P0/F04/F05 合并差异和 F14 部分安全；列出 #30/#31 的覆盖矩阵，消除重叠后再决定合并顺序。
4. [ ] **A03/A04：** 独立审 #28 与 #29；为 #29 增加 resolved→消失→复发的测试/设计记录。
5. [ ] **A05/A06：** 审 #32 只读诊断；审 #33 RFC 后再决定 #34 schema 的合并门槛。不要把 schema-only 误称已实现来源版本化。
6. [ ] **B01–B04：** 分别建独立小 PR 改向量重复计算、中文检索、远程 URL/Cookie、Ubuntu/PostgreSQL CI（每项含回归）。
7. [ ] **B05–B07：** 安全 hash 迁移、契约生成和后台任务模型，以明确安全/性能证据排序。
8. [ ] **C01→C02→C03→D01–D05：** 补评论、可靠证据版本、抽取与真实质量评测；**仅在评测可信后**推动 E 阶段产品增强。
9. [ ] **E01–E06：** ADR 导出、MCP diff 适用性、只读 Action、Web 审核台、开源安装与真实案例。
10. [ ] **收尾：** 每个 merged PR 更新本文件“状态追踪”、README/部署文档、验收报告；未达门槛或已推迟的项目保留为 Deferred，不伪造 Done。

### 8.1 开发 PR 模板（可复制到每个 PR）

- **Task ID / 问题 ID：** 例如 B02 / F09。
- **Baseline：** main SHA、依赖 PR、是否堆叠。
- **目标与非目标：** 本 PR 只解决什么；明确不动什么。
- **源码证据：** 受影响路径、现有问题复现（前/后对比）。
- **变更与兼容：** API/Schema、老数据、权限、迁移、失败恢复。
- **验证：** 单测、契约、真实 SQLite/PG、Web/MCP、最新 CI 链接；哪些 `not_run`。
- **安全与成本：** 数据/凭据隔离、真实 LLM 调用次数和授权、日志脱敏。
- **结论：** Ready for review / blocked / needs evidence，不将 CI pass 自动等同 merge permission。

## 9. 长期质量追踪（只用真实证据更新）

| 指标 | 当前状态（本计划制定时） | 达成规则 |
| --- | --- | --- |
| main 的导入安全/事务与复原 | 已有 Draft #26、#35；**未合并** | 安全复核、事务回归及 CI 达标并入主分支 |
| main 的跨层 pause/scope、告警与索引 | 已有 Draft #28、#29；**未合并** | 生命周期/权限/索引回归通过并入 main |
| SourceRef 版本化 | #32 只读诊断，#33 RFC，#34 schema-only；**未形成运行时版本化** | 来源版本与审核不可变语义通过迁移与重导入端到端验证 |
| GitHub 讨论采集 | 基线缺失评论 | 采集完整性与溯源、增量、隐私门禁通过 |
| 真实模型候选精确率 | **未验证**；此前 `pallets/click` 8 条 FakeProvider 候选独立核查结果不是模型分数 | 人类独立标注、真实模型/Prompt、可复现样本报告 |
| 中文 Why / 检索成本 | 词法中文缺口、重复 Embedding 已有代码证据 | 分层评测 + p95/call 统计，不用单一 happy-path 代替 |
| MCP 真实宿主与真实 UI | SDK in-process / CI 截图存在；真实宿主与外部 UX 尚未充分验证 | 独立 MCP host、浏览器、部署与用户任务实测 |
| 社区/价值反馈 | 公开 Star/Fork 不足以判断用户数 | 记录真实试用、首次成功、审核完成率、复用意愿，不猜测安装量 |

## 10. 维护与变更记录

- **变更入口：** 后续新增需求先在这里映射已有 ID/是否重复，必要时开 Issue，不直接修改多份旧路线图；PR 合并后更新状态、commit SHA、验证证据。
- **阶段闸门：** Stage A 安全/数据可信 → Stage B 质量基建与可靠检索 → Stage C 来源/抽取 → Stage D 实证 → Stage E 生态/体验；可独立并行的低风险设计研究不等于允许绕过前置验收。
- **历史与开源：** 旧计划路径保持可用；历史 Done 仅表示当时定义的代码阶段；新计划放 `docs/plans/` 而不是 README 中贴大篇清单。
- **首次记录（2026-10-30）：** 依据仓库内审查、两版第三方审查与 #26/#28–#35 当前 Draft 状态形成可执行路线；特别纠正外部审查第 15 节对 #32 的误读，识别 #35 的堆叠和 #29 的 resolved 告警语义。**尚未执行任何开发、合并或真实模型验证。**

## 11. Stage A 执行记录（2026-10-30，持续更新）

> 以下是后续执行的**事实记录**，不同于上方制定计划时的历史基线。仅 A01 已获维护者明确合并授权；其余事项未随此授权自动批准。

| 任务 | 当前处置 | 最终/当前 SHA 与 CI | 下一道门禁 |
| --- | --- | --- | --- |
| **A01 / PR #26** | **Merged**，维护者在对话中确认“ A01 没毛病，过 ” | PR head `ffeecc5755e0ba6501894c7d9f61f1a6754f68f4`；[PR CI #41032428318](https://github.com/luzay-max/DecisionAtlas/actions/runs/41032428318) 第一次浏览器冒烟失败、同 SHA 第 2 次全部成功；合并 commit `e2204cc32d6bc55204c56125b8a85141ec44acd1` | [main push CI #41036933915](https://github.com/luzay-max/DecisionAtlas/actions/runs/41036933915) **SUCCESS**；可控制的真实导入仍属于独立环境验收；浏览器偶发失败见 #38 |
| **A02 / PR #35** | **Merged**（维护者“批准”；安全缓解后合并） | PR 最终 head `a9f676076cbfc2588b25157289b4a16e81a211d0`，[#41368189607](https://github.com/luzay-max/DecisionAtlas/actions/runs/41368189607) **SUCCESS**；合并提交 `28b58eb1388c25a0a1ab3f1cca3c1848da4c2a0c`；[main push CI #41368799105](https://github.com/luzay-max/DecisionAtlas/actions/runs/41368799105) **SUCCESS** | Issue #36 **仍未修复**：`IMPORT_PAUSE_RESUME_ENABLED=false` 默认关闭，pause/resume 返回 503；#28 必须尊重能力开关；#30/#31 重叠功能不另合并或关闭 |
| **A03 / PR #28** | Draft；禁用模式的最终精确 head CI + 跨层源码验收 PASS；未合并 | head `51d85b1267404e1302d62f1565a87538cecb9050`；[CI #41559456480](https://github.com/luzay-max/DecisionAtlas/actions/runs/41559456480) **SUCCESS**；Node/TS/Engine/MCP/离线证据/Benchmark/Playwright 均通过 | Engine 默认 `IMPORT_PAUSE_RESUME_ENABLED=false`，暂停/恢复返回 503 不修改状态；Fastify 显式 503 双向透传；Web 未获 enabled 能力时隐藏控制；Issue #36 仍 OPEN，工作线程锁竞争/恢复未验收；等待维护者批准合并，生产功能保持禁用 |
| **A04 / PR #29** | Draft；current main 已整合，exact-head CI PASS；等待维护者评审 | 新 head `94ef008a93a4ab933595da8ea49743365e175972`；compare ahead 6 / behind 0；[CI #41423199943](https://github.com/luzay-max/DecisionAtlas/actions/runs/41423199943) SUCCESS（API 37 / Web 83 / Engine 534 passed, 1 skipped / MCP 1 / Playwright 5；Node、TS、offline evidence、benchmark 均通过） | Reviewed drift disposition 保留人工处理状态/ID；空和空白重索引清除旧 chunks；`resolved → absent → reappears` 回归明确记录目前不产生新 episode，后续与 F06 一起设计 revision/episode identity；六个预期文件差异、无 schema migration；未授权合并，未标记 Done |
| **A05 / PR #32** | Draft；current main 已整合，exact-head CI PASS；等待维护者评审 | 新 head `7c9104bc2fa845e6f66756cf294094d7a398c847`；ahead 5 / behind 0；[CI #41424545225](https://github.com/luzay-max/DecisionAtlas/actions/runs/41424545225) SUCCESS（API 37 / Web 83 / Engine 533 passed, 1 skipped / MCP 1 / Playwright 5；Node、TS、offline evidence、benchmark 均通过） | 只读当前 quote 诊断；list/detail/preview 的 mixed found/missing 状态一致；SourceRef ID/quote 与 review state 不变；不证明历史 revision authenticity；per-SourceRef Artifact SELECT 的 N+1 查询记为非阻断性能 follow-up；未授权合并 |
| **A06 / PR #33/#34** | DB 支持范围已确认；#33 v1 ADR 文档审查与 CI PASS，其余 ADR 待正式批准；#34 仍阻塞 | PostgreSQL + pgvector 服务端、SQLite 轻量/未来桌面、MySQL 暂不支持；RFC #33 head `8a6424a7fc364797093b6fb8b93b8535fb08ec02`，[CI #41559838115](https://github.com/luzay-max/DecisionAtlas/actions/runs/41559838115) **SUCCESS**；#34 文档 head `41e62fb51854ff6c959f12ebffbc3cb05ede32f0`，[CI #41559921484](https://github.com/luzay-max/DecisionAtlas/actions/runs/41559921484) 运行中 | RFC 明确 fingerprint v1、metadata allowlist、`(revision_id,generation)` 防 ABA CAS、legacy_unbound、DB 不可变/隐私例外、候选式重抽取；除数据库范围外仍须维护者 ADR 签字。#34 schema 缺 generation，PG/SQLite 代表数据迁移、备份/回滚未验收；不得合并/执行迁移 |
| **附属 Issue #38 / PR #39** | E2E 诊断 Draft | `2d569fd3` / [CI #41036104378](https://github.com/luzay-max/DecisionAtlas/actions/runs/41036104378) | 定位偶发语言/权限渲染问题，不因单次绿灯而关闭 |

合并 #26 **不代表** A02、#39、Stage B/C 或付费/私有数据测试获得批准。凡仅在 Draft PR 中的行为仍不计入 main。记录新的 head/CI 时必须更新上表，不能复用过期的 CI 结果。


**阶段验收证据：** [2026-11-03 Stage A A04/A05/A03 与 F06b ADR 交接记录](../validation/2026-11-03-stage-a-evidence-first-acceptance.md)。

## 12. 维护者确认的 Stage A 收口与后续执行顺序（2026-11-03）

维护者明确要求：**先完成 #29、#32 的验收，再处理带默认禁用边界的 #28，同时确定 #33 的关键架构决策。Stage A 收口后按 B → C → D 推进；UI 和生态扩展后置。** 目标是“证据可信、结果有用”的核心闭环，而不是扩展功能数量或宣称未经实测的精度。

| 顺序 | 范围 / 最新证据 | 验收处置 / 不可越过的门禁 |
| --- | --- | --- |
| 1 · A04 #29 | head `94ef008a`；[CI #41423199943](https://github.com/luzay-max/DecisionAtlas/actions/runs/41423199943) SUCCESS，6 个预期文件；已完成 F03/F07 独立源码和 SQLite 回归矩阵审查 | **自动化/源码验收通过，等待维护者合并审批**。保留 handled/reviewed ID、rationale、审计；空索引清理通过。resolved→消失→再出现是明确记录的**未实现 episode**，不作为已修复功能。 |
| 2 · A05 #32 | head `7c9104bc`；[CI #41424545225](https://github.com/luzay-max/DecisionAtlas/actions/runs/41424545225) SUCCESS，3 个预期文件；read-only quote 一致性源码和 SQLite 回归审查 | **自动化/源码验收通过，等待维护者合并审批**。现存文本 ≠ 历史真实性。列表 per-SourceRef 查 Artifact 的 N+1 成本为性能待办；上线大型工作区前量测/批量读取。 |
| 3 · A03 #28 | 既有 head `ca335a59` 的 [CI #41394043235](https://github.com/luzay-max/DecisionAtlas/actions/runs/41394043235) SUCCESS；新增 BFF pause/resume **503 默认禁用透传**测试，head `51d85b1267404e1302d62f1565a87538cecb9050`；[CI #41559456480](https://github.com/luzay-max/DecisionAtlas/actions/runs/41559456480) 运行中 | Engine 默认 `IMPORT_PAUSE_RESUME_ENABLED=false`，pause/resume 503 且无状态修改；Web 未确认能力或查询失败时隐藏控制；仅受控实验可开启。Issue #36 SQLite writer/worker 生命周期仍 OPEN，**不因 UI/CI 通过而对生产开放**。新 head CI + 维护者审核后才讨论合并。 |
| 4 · A06 #33/#34 | PostgreSQL+pgvector 正式版、SQLite 轻量版/未来桌面版、MySQL 暂不支持：**维护者已明确确认**。#33 RFC 新增可实施的 v1 决策表（指纹、pointer generation/CAS、证据绑定、隐私/不可变、worker/recovery、事件复发）；#34 仅文档补充 ABA 阻断 | 数据库支持范围已定；**其余 ADR 是待维护者审议的具体方案，不是批准**。#34 现缺单调指针 generation，无法防 A→B→A ABA；必须先审议 ADR、双数据库迁移与备份回滚，再修改或合并 schema。旧 SourceRefs 保持 legacy_unbound；不启用任何实际 dual-write/重抽取。 |

**Stage A 出口必须可审计：** A03/A04/A05 每个 PR 的最终 `merged / deferred / revised` 由维护者明确批准并有合并后 main SHA + CI；A06 至少要有独立 RFC 决议，#34 可以继续 Deferred，不可把未验收的迁移当成 Done；Issue #36 保持生产功能默认禁用直至真实并发/恢复验收，或显式选择长期禁用的产品取舍。任何自动化 CI 通过都不能代替人工合并授权。

### Stage A 后既定顺序（未提前开工）

1. **Stage B：中文检索 + 工程质量。** B01 决策向量版本缓存与维度/finite 检验；B02 中文 bigram、混合技术词、真实向量不可用时的词法 fallback 和 `retrieval_mode`；B03 同源 API、Cookie 解析安全；B04 Ubuntu + PostgreSQL 集成 CI；B05–B07 依风险/依赖继续处理密码迁移、契约和 Worker 协议。每片只建立独立小 PR + 明确 offline/PG 测试和延迟指标，不伪装 fake embedding 为生产语义检索。
2. **Stage C：评论采集 → 不可变来源版本化 → 抽取质量。** C01 只读 GitHub issue/PR/review/inline 评论、分页完整性与采纳/异议信号；C02 基于获批 #33 ADR 与安全迁移落地 revision/SourceRef；C03 防提示注入和候选/来源版本绑定。未获批准不采集私有仓库、不启用付费模型、不自动认可任何决策。
3. **Stage D：真实公开仓库质量评测。** 在 C01/C02 提供可追溯样本后，以冻结 SHA、两人独立标注、明确覆盖不足/不可验证状态和预注册门槛衡量 precision/recall、Why 引用、拒答、成本及“有/无评论”消融。不是利用 CI 单测数量或 FakeProvider 自我证明准确性。
4. **Stage E：UI/生态延期。** ADR、MCP、Action、审核 UX、桌面安装包、GitLab/Gitee 等待核心可信与实用性指标通过后再独立立项；不自动合并历史生态 Draft。

**执行状态：** 本节记录维护者优先级与现有验收事实，不授权新的代码 PR 合并，不覆盖未完成的 worker、隐私、来源版本或实际质量评测门禁。



## 13. 维护者已批准的 Stage A 最终边界与 Stage B 启动闸门（2026-11-03）

> 本节是 11、12 节历史过程之后的**最新处置**；原有旧状态不追写成当时已通过。

- **交付 / main：** #26、#35、#29、#32 全部已依维护者授权合并；#28 在明确 `IMPORT_PAUSE_RESUME_ENABLED=false`、#36 保持 OPEN 条件下亦已获维护者批准并**合并**，merge `2641989b443ca6633019fa7b713521be0ce5686d`。#28 exact-head CI #41570044464 SUCCESS；合并后 [main CI #41573941870](https://github.com/luzay-max/DecisionAtlas/actions/runs/41573941870) **需独立确认最终结果**。合并只代表 disabled 路径已交付，**没有**启用 Worker pause/resume。
- **已批准的设计 / #33 T：** 维护者明确批准 F06b 技术 ADR，采用稳定 Artifact + immutable revisions、v1 canonical fingerprint/hash、旧引用 `legacy_unbound`、同 Artifact 复合 FK、代际 CAS 防 ABA、候选式 revision/extractor 抽取、PG17+pgvector server 与文件型 SQLite local。#33 RFC 新 Head `ac2b1037c89a4febcf62c7c42ee63e836272934f` CI #41574104477 在本记录时未完成；文档合并与 runtime 交付分别验收。
- **已批准延期 / #33 P、#34：** P 隐私运营中的保留时长、删除 SLA、备份清理、加密、恢复后再删除和私有数据启用，需要独立审批和可运行能力；7/30/90 天仍是提案，**没有生效**。#34 明确保留 Draft：尽管 schema generation + PostgreSQL 17 / 文件型 SQLite 合成数据升级/恢复 CI 已通过，**不批准**合并、生产迁移、backfill、versioned runtime writer 或重抽取。
- **其他已批准延期 / 独立验收：** #36 Worker 并发锁竞争/恢复 before pause/resume activation；#40 告警 episode 复发；#41 SourceRef/Artifact N+1；#42 Windows Vitest timeline 偶现超时，#38/39 E2E 稳定性；#30/#31 已由 #35 覆盖的重叠功能不重复合并；Stage C/D/E 均按路线图另行验收。私有仓库与付费模型继续需要单独批准。
- **Stage B 入口：** 在 #28 合并后 main CI SUCCESS 与本决议写回 #37 后，先实现 **B01**：决策内容版本/Embedding 模型/维度相关的有界缓存与非有限向量检验（不依赖 #34 版本化 Schema），再单独 B02 中文 bigram/混合词和 lexical fallback、B03 远程代理/Cookie、B04 Ubuntu/PostgreSQL CI。每片开独立 Draft PR、附新 Head CI 与真实性/成本限制；**未经审批不自动合并**。

**完成定义不混淆：** 已交付的 main 行为、仅获批准的技术决策、默认禁用的实现，以及明确延期的隐私/数据库/Worker 事项必须分别报告，不得将 CI PASS 当作运行时能力或真实产品价值指标。



### 13.1 Stage A exit gate completed; Stage B B01 authorized to start (2026-11-03)

**Stage A closed with deferred issues** on `main@2641989b443ca6633019fa7b713521be0ce5686d` after post-merge Windows [CI #41573941870](https://github.com/luzay-max/DecisionAtlas/actions/runs/41573941870) **SUCCESS**. Maintainer approved #28 merge with pause/resume permanently **default OFF until #36 separate worker acceptance**, and approved #33 **T technical ADR** without authorizing #34 merge/migration or **P** privacy/retention operations. #34, #36, #40, #41, #42, #38/39 and Stage C–E are separate deferred/tracked deliverables, not Stage A feature completion.

**Stage B starts at B01** from the verified main SHA: bounded decision-vector caching tied to content/model/dimension, validation of finite and dimension-compatible embeddings, and explicit limitations; add isolated regression and exact-head CI. B02 Chinese retrieval, B03 same-origin proxy/Cookie, B04 Ubuntu+PG CI follow as separate non-stacked work items. Approval to start B is **not** authorization to merge any new code PR automatically.


### 13.2 Stage B B01 implementation started — draft #43

- **Entry gate:** #28 main merge `2641989b443ca6633019fa7b713521be0ce5686d` and exact-main [CI #41573941870](https://github.com/luzay-max/DecisionAtlas/actions/runs/41573941870) SUCCESS; #33 T ADR approved with P deferred; #34 migration remains **not authorized**.
- **B01 active Draft:** [PR #43](https://github.com/luzay-max/DecisionAtlas/pull/43) started as independent branch `feat/b01-bounded-decision-embedding-cache-20261103` from that main. Scope: bounded in-memory LRU of decision vectors keyed by decision content/model/dimension/workspace, finite/dimension/batch validation, query embeddings still fresh; FakeEmbedder deliberately not cached. Synthetic SQLite regression, no schema migration or private/paid calls.
- **Acceptance pending:** exact final PR head CI, review of cache isolation and content invalidation, benchmark limitations; not merged and no authorization to merge. B02/B03/B04 and #41 SQL N+1 remain independent.


### 13.3 Stage B B01 validated / B02 independent Draft started (2026-11-03)

- **B01 #43 · CI review ready, unmerged:** head `ea36ac789aa033245cfb9e2e00a30af6f1f432c9`, [CI #41575440346](https://github.com/luzay-max/DecisionAtlas/actions/runs/41575440346) **COMPLETED SUCCESS**; ahead 10/behind 0, four scoped files. Process-local bounded public-source-only vector cache, digest/model/dimension invalidation, malformed/overflowed embedding fail closed; private and Fake embeddings excluded. **Still Draft: maintainer merge approval not granted.**
- **B02 #44 · independent Draft on verified main:** branch `feat/b02-chinese-lexical-fallback-20261103` from `main@2641989b443ca6633019fa7b713521be0ce5686d`, *not stacked on #43*. Chinese overlapping Han bigrams, NFKC mixed English technical tokens, preserved stopwords, honest `retrieval_mode=hybrid|lexical_only|lexical_fallback|not_run`; FakeEmbedder never claims semantic retrieval. Negative Redis-vs-PostgreSQL regression was explicitly tightened. Latest candidate head `02a602429da43c58daffc3192ac1a1540fc72304`; [CI #41586893734](https://github.com/luzay-max/DecisionAtlas/actions/runs/41586893734) **IN PROGRESS** at checkpoint, not green yet.
- **Stage B merge policy:** B01 and B02 remain two independent Draft PRs; no auto merge. If B01 eventually merges, reconcile B02 to that new main and rerun exact-head CI. Chinese recall/precision, p95 and paid-provider quality remain **unmeasured** without separate evidence; #34, #36, #33 P constraints remain unchanged.


### 13.4 B02 CI accepted / B03 same-origin security Draft (2026-11-03)

- **B01 #43:** [CI #41575440346](https://github.com/luzay-max/DecisionAtlas/actions/runs/41575440346) **SUCCESS** on `ea36ac78`, four scoped files, ahead 10/behind 0; public-only bounded cache and vector validation. **Draft/unmerged; maintainer merge approval not granted.**
- **B02 #44:** [CI #41587131385](https://github.com/luzay-max/DecisionAtlas/actions/runs/41587131385) **SUCCESS** on `9de5bd35`, eight scoped files, ahead 10/behind 0; Chinese bigram/mixed-language retrieval, honest fallback, typed Why `retrieval_mode`, negative control tests. **Draft/unmerged; not stacked on B01.** Real Chinese precision/recall still unmeasured.
- **B03 #45:** [独立 Draft PR](https://github.com/luzay-max/DecisionAtlas/pull/45) from verified `main@2641989b`. Latest head `624005ca110a3ae47bda36d417719e45ddd74729`, [CI #41589046886](https://github.com/luzay-max/DecisionAtlas/actions/runs/41589046886) **IN PROGRESS** at record time (Node tests/TS typecheck passed, Engine running). Changes: Next fixed same-origin `/backend` rewrite, browser cookie-only **subsequent** authentication and legacy localStorage token removal, SSR forward only configured auth cookie, BFF duplicate/malformed Cookie fail-closed, session handling across all auth routes. **Compatibility limit:** existing login/session JSON may still return `session_token`, so no claim JS can never see it; real HTTPS/public Web Origin deployment remains untested and separately gated. **Draft/unmerged.**
- **Next B04:** only after B03 exact-head acceptance, add Ubuntu + PostgreSQL 17 integration CI for **current main schema**, not the unapproved #34 F06b migration. No private data, chargeable AI, worker enablement, automatic merging or false precision claim. If B01/02 eventually merges first, independently reconcile every other Draft on the new main and rerun exact-head CI.

**Never conflate** Stage A design-only T approval with P privacy operations or #34 database rollout; #36 remains open and pause/resume stays default-disabled.


### 13.5 B03 accepted in CI / B04 Ubuntu PostgreSQL 17 integration (2026-11-03)

**Current Stage B review-state matrix (all from `main@2641989b443ca6633019fa7b713521be0ce5686d`, independent Draft PRs, not stacked):**

| Task | Scope | Current exact-head CI | Deployment/merge status |
| --- | --- | --- | --- |
| B01 [#43](https://github.com/luzay-max/DecisionAtlas/pull/43) | Bounded, process-local public-only decision embedding cache + finite/model/dimension guards | Windows [#41575440346](https://github.com/luzay-max/DecisionAtlas/actions/runs/41575440346) **SUCCESS** on `ea36ac78` | Draft/unmerged; maintainer merge approval required; real recall/p95 not claimed |
| B02 [#44](https://github.com/luzay-max/DecisionAtlas/pull/44) | Chinese bigrams/mixed tech tokens, accepted-only lexical fallback and honest Why `retrieval_mode` | Windows [#41587131385](https://github.com/luzay-max/DecisionAtlas/actions/runs/41587131385) **SUCCESS** on `9de5bd35` | Draft/unmerged; Chinese precision/recall not measured |
| B03 [#45](https://github.com/luzay-max/DecisionAtlas/pull/45) | Browser same-origin `/backend`, HttpOnly-cookie transport, no localStorage token persistence, BFF duplicate/malformed-cookie guard | Windows [#41589046886](https://github.com/luzay-max/DecisionAtlas/actions/runs/41589046886) **SUCCESS** on `624005ca` | Draft/unmerged; live HTTPS, proxy and production Origin need independent deployment acceptance; legacy login/session JSON token field retained |
| B04 [#46](https://github.com/luzay-max/DecisionAtlas/pull/46) | Ubuntu PG17 + pgvector on **merged 0012** schema; synthetic accepted Decision/SourceRef/audit/owner workspace and FK/unique checks | Ubuntu [#41592397095](https://github.com/luzay-max/DecisionAtlas/actions/runs/41592397095) **SUCCESS** on `f166d7f`; Windows [#41592396997](https://github.com/luzay-max/DecisionAtlas/actions/runs/41592396997) **in progress at this checkpoint** | Draft/unmerged; not production migration; tests explicitly assert #34 tables/columns absent |

**Gate interpretation:** CI green means a PR may be *reviewed*, not merged without explicit maintainer approval. If any earlier B PR merges first, re-evaluate branch compatibility against updated main and rerun exact-head CI on each affected branch. All Stage A independent deferrals remain unchanged: #36 worker pause/resume **disabled**, #34 schema/migration **not authorized**, P private retention/erasure/backup **unapproved**; no real private/costly runs.


### 13.6 Stage B B01–B04 CI acceptance and independent merge approvals (2026-11-03)

All four task PRs started independently from verified `main@2641989b443ca6633019fa7b713521be0ce5686d`, have **exact-head automated CI SUCCESS**, are **Draft / UNMERGED**, and must not be auto-merged:

| Task | PR head | Verified CI | Decision |
| --- | --- | --- | --- |
| B01 public-only bounded embedding LRU / finite and dimension validation | [#43](https://github.com/luzay-max/DecisionAtlas/pull/43) `ea36ac78` | [Windows #41575440346](https://github.com/luzay-max/DecisionAtlas/actions/runs/41575440346) SUCCESS | Pending explicit merge approval |
| B02 Chinese bigrams + technical English words / honest lexical fallback and typed Why mode | [#44](https://github.com/luzay-max/DecisionAtlas/pull/44) `9de5bd35` | [Windows #41587131385](https://github.com/luzay-max/DecisionAtlas/actions/runs/41587131385) SUCCESS | Pending explicit merge approval |
| B03 same-origin API / HttpOnly cookie transport / duplicate/invalid-cookie fail-closed | [#45](https://github.com/luzay-max/DecisionAtlas/pull/45) `624005ca` | [Windows #41589046886](https://github.com/luzay-max/DecisionAtlas/actions/runs/41589046886) SUCCESS | Pending explicit merge approval; live TLS/Origin deployment test independently required |
| B04 Ubuntu PostgreSQL 17 on **merged Alembic 0012** (explicitly excludes #34) | [#46](https://github.com/luzay-max/DecisionAtlas/pull/46) `f166d7f` | [Ubuntu PG17 #41592397095](https://github.com/luzay-max/DecisionAtlas/actions/runs/41592397095) SUCCESS + [Windows #41592396997](https://github.com/luzay-max/DecisionAtlas/actions/runs/41592396997) SUCCESS | Pending explicit merge approval; isolated synthetic fresh DB only |

**Recommended gate sequence:** B01 → new-main CI → reconcile/retest B02 → new-main CI → reconcile/retest B03 → new-main CI → reconcile/retest B04. For B02/B03 both modifying `apps/web/lib/api.ts`, require explicit preservation of B02 Why `retrieval_mode` and B03 same-origin cookie/header security tests, not only automatic Git conflict resolution. Readable evidence and false positive regression must be reviewed separately from CI. No genuine Chinese recall/precision@k, real p95/model spend, production HTTPS reverse proxy, production DB migration or private-data delete/backup acceptance has been performed.

**Stage A independent gates remain open:** #34 F06b schema/production migration **NOT AUTHORIZED**; #33 T ADR approved only, P private operations/retention/erasure and backup cleanup **DEFERRED**; #36 worker restart/concurrency and pause/resume **DEFAULT OFF**. Stage B engineering CI acceptance **is not** Stage C evidence provenance or Stage D real-world quality completion.


### 13.7 B01 #43 maintainer-approved merge and combined B02/B03 review gate (2026-11-03)

The maintainer authorized **#43 merge first**, then `main` CI, then B02/B03/B04 individually tested and separately approved, with an explicit requirement to demonstrate **B02+B03 combined runtime behavior**, not merely a Git clean merge.

- **B01 [PR #43](https://github.com/luzay-max/DecisionAtlas/pull/43) MERGED** after exact-head `ea36ac789aa033245cfb9e2e00a30af6f1f432c9` Windows [CI #41575440346](https://github.com/luzay-max/DecisionAtlas/actions/runs/41575440346) **SUCCESS**; GitHub merge SHA **`f2fae3949c2da9b1401ab14c1e0ff00c48592290`**.
- **Post-merge [main CI #41594072583](https://github.com/luzay-max/DecisionAtlas/actions/runs/41594072583) is IN PROGRESS** as of this note; do not declare B01 new-main gate complete until an exact SHA SUCCESS is observed.
- **B02 [#44](https://github.com/luzay-max/DecisionAtlas/pull/44), B03 [#45](https://github.com/luzay-max/DecisionAtlas/pull/45), B04 [#46](https://github.com/luzay-max/DecisionAtlas/pull/46):** all remain **Draft/unmerged**, behind the new main baseline. Only after successful post-main CI reconcile each branch without losing independent review, run exact-head CI, and seek separate merge authorization.
- **Mandatory B02+B03 integration acceptance:** after reconciling the candidates, run an explicit *combined* test branch/check: same-origin `/backend/query/why` with valid HttpOnly-cookie-derived session, a mixed Chinese/English PostgreSQL question, `retrieval_mode` preserved through Engine/BFF/Web typed response, provider outage and FakeEmbedder lexical-only disclosure, and negative security cases (no localStorage token forwarding, rejected duplicate/malformed cookie and hostile Origin). Verify client typed `retrieval_mode` plus B03 cookie transport both survive shared `apps/web/lib/api.ts` merging. Repeat exact-head CI for any subsequently changed PR.
- **Unchanged gates:** #34 production migration not approved; #36 worker pause/resume disabled/issue open; P private retention/erasure and backup cleanup not approved. Synthetic CI is not live HTTPS, real semantic quality, production restore or privacy acceptance.


### 13.8 B01 post-main CI green; B02/B03 shared behavior integration candidate (2026-11-03)

The maintainer authorized the **B01 #43 merge only**, then required post-main CI, **individual B02/B03/B04 approvals** and a **real combined B02+B03 behavior proof** beyond Git conflict checks.

1. **B01 #43 merged** as `main@f2fae3949c2da9b1401ab14c1e0ff00c48592290`. [Post-main CI #41594072583](https://github.com/luzay-max/DecisionAtlas/actions/runs/41594072583) **SUCCESS** (exact merge SHA).
2. **B02 #44** reconciled to this main: head `8ece602df79be6f07d1643978b631dfa670b4d19`, unchanged 8-path feature diff, behind 0, [Windows CI #41594910571](https://github.com/luzay-max/DecisionAtlas/actions/runs/41594910571) **SUCCESS**. **Draft/unmerged**.
3. **B03 #45** reconciled to this main: head `130d7b0795d532c5061f52fd2a46b098ae4bd135`, unchanged 9-path feature diff, behind 0, [Windows CI #41595041085](https://github.com/luzay-max/DecisionAtlas/actions/runs/41595041085) **SUCCESS**. **Draft/unmerged**, live TLS and production public Origin still independent.
4. **B02+B03 real composition** has an **integration-only, never-merge [Draft #47](https://github.com/luzay-max/DecisionAtlas/pull/47)** on this verified main, head `e6092c8e86e72f613b98dba84aad3a3860485397`; it assembles both code paths, explicitly merges B02 `retrieval_mode` typed Why response into B03 `apps/web/lib/api.ts` while preserving same-origin `/backend` cookie-only session transport. Tests include real browser→Next→Fastify→Engine Chinese PostgreSQL Why against synthetic accepted data, candidate-only negative, HttpOnly cookie and forbidden Origin, plus Web typed mode and Fastify BFF forged-header/duplicate-cookie/Origin regression. [CI #41595983746](https://github.com/luzay-max/DecisionAtlas/actions/runs/41595983746) **in progress at this checkpoint**; this is *not* yet a composition acceptance result. All tests use synthetic data/FakeEmbedder, no private or paid upstream.
5. **B04 #46** separately reconciled to new main, head `029b97b61e2f45cea13a1e2beded26bd3e0e8646`, unchanged 3-path diff, behind 0; [Ubuntu PG17 + pgvector CI #41596182326](https://github.com/luzay-max/DecisionAtlas/actions/runs/41596182326) **SUCCESS**, [Windows CI #41596183044](https://github.com/luzay-max/DecisionAtlas/actions/runs/41596183044) **in progress**.

**Remaining review gates:** if #47 reports a conflict or behavioral regression, fix underlying #44/#45 independently and rerun both individual exact-head CI plus the composition CI; do not merge the assembled #47 test PR. After explicit #44 approval/merge, run its post-main CI, reconcile #45 and incorporate permanent combined behavior checks into #45, then separately request its approval; B04 follows the new main. None of #44/#45/#46/#47 has received merge approval. #34 remains unapproved, #36 disabled/open, P private operations deferred.


### 13.9 B01 post-main and B02+B03 composed runtime CI accepted (2026-11-03)

**Latest evidence / no implied merge authorization:**

| Gate | Head and result | Disposition |
| --- | --- | --- |
| **B01 #43** | main merge `f2fae3949c2da9b1401ab14c1e0ff00c48592290`; [post-main Windows #41594072583](https://github.com/luzay-max/DecisionAtlas/actions/runs/41594072583) **SUCCESS** | **Merged and accepted** pursuant to explicit maintainer approval |
| **B02 #44** | `8ece602df79be6f07d1643978b631dfa670b4d19`, ahead 11 / behind 0; [Windows #41594910571](https://github.com/luzay-max/DecisionAtlas/actions/runs/41594910571) **SUCCESS** | Draft/unmerged; **separate merge approval pending** |
| **B03 #45** | `130d7b0795d532c5061f52fd2a46b098ae4bd135`, ahead 14 / behind 0; [Windows #41595041085](https://github.com/luzay-max/DecisionAtlas/actions/runs/41595041085) **SUCCESS** | Draft/unmerged; separate merge approval, live HTTPS public-Origin acceptance and local auth race follow-up pending |
| **Combined B02+B03 [integration-only #47](https://github.com/luzay-max/DecisionAtlas/pull/47)** | `e6092c8e86e72f613b98dba84aad3a3860485397`; [Windows #41595983746](https://github.com/luzay-max/DecisionAtlas/actions/runs/41595983746) **SUCCESS**; API 58 tests, Web 104 tests, Engine 555 passed/1 skipped, Playwright **6 passed** | **Actual combined behavior validated on synthetic local runtime**; shared `apps/web/lib/api.ts` retained B02 `retrieval_mode` and B03 same-origin `/backend`+Cookie contract; **NEVER MERGE THIS TEST-ONLY PR** |
| **B04 #46** | `029b97b61e2f45cea13a1e2beded26bd3e0e8646`, ahead 4 / behind 0; [Ubuntu PG17 #41596182326](https://github.com/luzay-max/DecisionAtlas/actions/runs/41596182326) **SUCCESS** + [Windows #41596183044](https://github.com/luzay-max/DecisionAtlas/actions/runs/41596183044) **SUCCESS** | Draft/unmerged; separate approval pending, synthetic merged-0012 schema only |

**Combination test content:** Playwright drove a real browser → Next.js `/backend` same-origin rewrite → Fastify BFF → FastAPI Engine using an isolated **synthetic accepted Chinese PostgreSQL** decision and candidate-only negative; validated lexical-only Why `retrieval_mode`, primary decision, session Cookie `HttpOnly; SameSite=Lax`, no JS localStorage token, hostile Origin rejection and no browser port-3001 request. Node tests also verified typed lexical_only/lexical_fallback/hybrid, BFF Chinese fallback JSON pass-through, forged session header ignored and duplicate Cookie not forwarded. These are real CI processes with **synthetic data and FakeEmbedder**, not real public repository retrieval metrics or production TLS.

**Log-review exception:** Although [#47 CI](https://github.com/luzay-max/DecisionAtlas/actions/runs/41595983746) completed SUCCESS, WebServer emitted a transient SQLite `actors.username` UNIQUE error during concurrent local/test `/auth/bootstrap`; **[Issue #48](https://github.com/luzay-max/DecisionAtlas/issues/48) OPEN** for deterministic concurrency and no-500 acceptance. Web unit test logs also showed relative `/backend/governance/guardrail` URL parsing warnings in Node/jsdom mocks; not the actual browser result, but follow-up test hygiene before declaring all auth modes robust. **Do not claim auth-bootstrap concurrency or production deployment safety from the green suite**.

**Remaining approval sequence:** maintainer may now independently approve B02 #44 (not yet granted); only then merge, run exact new-main CI, reconcile B03 #45 preserving both shared-file behaviors and bring forward durable composed tests from #47, obtain its separate approval and deployment/Issue #48 disposition; B04 follows with its own new-main checks and approval. #34 migration unapproved, #36 pause/resume OFF/open and P private retention/erasure/backup deferred. #47 must never be merged.


### 13.10 Stage B B01–B04 merge and validation record (2026-11-05)

**Verified pre-B04 main baseline:** `4c400018fbf24a8308c4d8176c340235b15bd130`. Its post-B03 main CI [#41980036581](https://github.com/luzay-max/DecisionAtlas/actions/runs/41980036581) was **SUCCESS**; B04 was merged afterward as recorded in section 13.12.

| Item | Final disposition | Merge commit / CI | Remaining limits |
| --- | --- | --- | --- |
| **B01 #43** | Merged | `f2fae3949c2da9b1401ab14c1e0ff00c48592290` | Process-local public-only bounded cache; real retrieval recall/p95 still unmeasured |
| **B02 #44** | Merged | `0df1b2be3b5fb3dbf7a09c558f18f7ab666191f7` | Chinese bigram/mixed-language lexical fallback and honest retrieval mode; real Chinese precision/recall still unmeasured |
| **B03 #45** | Merged after #49 | `4c400018fbf24a8308c4d8176c340235b15bd130` | Same-origin BFF/HttpOnly cookie boundary; production HTTPS/reverse-proxy/Secure-cookie/Origin rehearsal remains separate |
| **Bootstrap concurrency #49** | Merged before B03 | `05986d207071cd7aa81923919219c1b4cfbdb31f` | SQLite/PostgreSQL local bootstrap transaction race fixed and tested; production auto-bootstrap remains fail-closed |
| **B04 #46** | Squash merged after explicit maintainer approval | Merge commit `85523b2284afc0765f4e059e91c71c3283c9ba27`; Windows [#41983163428 attempt 2](https://github.com/luzay-max/DecisionAtlas/actions/runs/41983163428) SUCCESS; Ubuntu PG17 [#41983163176](https://github.com/luzay-max/DecisionAtlas/actions/runs/41983163176) SUCCESS | Fresh PostgreSQL 17.11/pgvector DB only; migrated merged 0012 schema; no #34 tables/columns; no production migration/performance claim |

**B04 exact-head validation detail:** Windows Node/API 58 passed, Web 104 passed, Engine 561 passed / 3 skipped, MCP SDK v2 protocol, offline evidence regression and benchmark fixture validation passed; Playwright **6 passed**. PostgreSQL 17 integration passed on a disposable fresh DB, with expected FK/unique constraint rejections and persistence after reconnect. Browser logs show seven local bootstrap requests returned HTTP 200 and no duplicate-actor `actors.username` UNIQUE error.

**Intermittent E2E stability follow-up:** Windows attempt 1 on the same B04 head failed once at the imported-evidence preview Chinese heading assertion (5-second timeout); attempt 2 passed all six browser tests without code changes. This is a recurrence of [Issue #38](https://github.com/luzay-max/DecisionAtlas/issues/38), not a B04/PostgreSQL failure. Existing diagnostic [PR #39](https://github.com/luzay-max/DecisionAtlas/pull/39) has been reconciled to current main as `d6dd514238a3b7150d014cc3a34e3d69591ad9c5` (2 ahead / 0 behind; one test file changed) and is running exact-head Windows CI [#41986207204](https://github.com/luzay-max/DecisionAtlas/actions/runs/41986207204). It adds an explicit locale-readiness wait and bounded non-sensitive failure metadata while preserving the candidate/evidence/desktop/mobile assertions. Keep #38 open until repeated fixed-SHA evidence is reviewed; one green retry alone does not prove the root cause.

**Unchanged gates:** #34 F06b schema/migration remains **NOT AUTHORIZED**; #36 worker lifecycle and pause/resume remains **OPEN / DEFAULT OFF**; private-source P retention/erasure/backup operations remain deferred. Integration-only #47 must **never be merged**. Production HTTPS and real semantic retrieval quality are not established by these CI runs.

### 13.11 Stage B05 — Argon2id password-hash migration (implemented; Draft PR #50)

B05 / N5 is implemented in [Draft PR #50](https://github.com/luzay-max/DecisionAtlas/pull/50), head `9e5a0298ce798f12c64cbd2b12da6d031f2b0d98`:
- New account, local bootstrap and password-reset hashes use self-describing Argon2id PHC format with explicit parameters (19 MiB memory, 2 iterations, parallelism 1, 32-byte output, 16-byte random salt).
- Existing PBKDF2 `salt$hex` hashes remain verifiable; a successful login upgrades them automatically. Wrong passwords and malformed/unknown formats fail closed; legacy digest comparison uses constant-time `hmac.compare_digest`.
- Login uses a compare-and-set against the verified hash before creating a session. If a concurrent password reset wins, the stale-password login is rejected; a concurrent successful legacy rehash is re-read and re-verified.
- Hash upgrade and session creation share one transaction. The failure-injection rollback test confirms neither the new hash nor session persists if the transaction fails.
- No database schema migration: existing `actors.password_hash` TEXT is reused. No change to Fernet GitHub-token encryption/rotation, #34 schema work, or #36 worker lifecycle.
- Tests cover Argon2id output/verification, legacy compatibility, malformed hashes, wrong-password no-upgrade, successful login migration, concurrent password reset, transaction rollback, and password-reset output format.

**Exact-head CI on PR #50:** Windows [#41999937190](https://github.com/luzay-max/DecisionAtlas/actions/runs/41999937190) **SUCCESS** (Node/API 58 passed, Web 104 passed, Engine 572 passed / 3 skipped, MCP protocol, offline evidence, benchmark fixtures, Playwright 6 passed); PostgreSQL 17 [#41999937102](https://github.com/luzay-max/DecisionAtlas/actions/runs/41999937102) **SUCCESS** with frozen lock install and bootstrap concurrency test; merged-schema PostgreSQL 17 [#41999937085](https://github.com/luzay-max/DecisionAtlas/actions/runs/41999937085) **SUCCESS**. B05 remains Draft and unmerged pending independent technical review.

**Rollback constraint:** B05 code can verify both PBKDF2 and Argon2id. A pre-B05 application binary cannot verify Argon2id hashes; after Argon2id writes begin, rollback must target a dual-verifier B05-compatible release. The tested DB transaction rollback prevents partial migration writes but does not make a pre-B05 binary compatible with Argon2id.

### 13.12 Post-B04 merge and current Stage B gate status (2026-11-05)

- B04 #46 was squash-merged as `85523b2284afc0765f4e059e91c71c3283c9ba27`. Both post-merge main checks passed: Windows [#41997873319](https://github.com/luzay-max/DecisionAtlas/actions/runs/41997873319) (Node/API 58, Web 104, Engine 561 / 3 skipped, Playwright 6) and PostgreSQL 17 [#41997873227](https://github.com/luzay-max/DecisionAtlas/actions/runs/41997873227).
- Current main baseline for B05 is `85523b2284afc0765f4e059e91c71c3283c9ba27`; B05 is isolated in Draft PR #50.
- [Issue #38](https://github.com/luzay-max/DecisionAtlas/issues/38) remains open. Diagnostic [PR #39](https://github.com/luzay-max/DecisionAtlas/pull/39) has green exact-head Windows CI [#41986207204](https://github.com/luzay-max/DecisionAtlas/actions/runs/41986207204) (Engine 561 / 2 skipped; Playwright 6 passed), but this single clean run does not prove the intermittent Chinese heading failure's root cause is eliminated.
- #34 F06b schema/migration remains **NOT AUTHORIZED**; #36 worker lifecycle and pause/resume remains **OPEN / DEFAULT OFF**; private-source P retention/erasure/backup operations remain deferred. Integration-only #47 must **never be merged**. No production deployment, password reset, or credential migration has been performed.


### 13.13 B05 merged; post-merge main accepted; next work reconciled (historical snapshot, 2026-11-06)

**B05 / PR #50 is MERGED** after the maintainer explicitly approved the exact reviewed head `7189891c0af660b57603ee123f60e770dfdecd74`.

- Merge commit and current `main`: `6bcb6161dddb55ed00731c940ffd82b759c011b9`.
- PR #50: [merged](https://github.com/luzay-max/DecisionAtlas/pull/50), merge commit `6bcb6161dddb55ed00731c940ffd82b759c011b9`.
- Post-merge Windows full CI [#42150591510](https://github.com/luzay-max/DecisionAtlas/actions/runs/42150591510): **SUCCESS**.
- Post-merge PostgreSQL 17 bootstrap + B05 concurrency [#42150591304](https://github.com/luzay-max/DecisionAtlas/actions/runs/42150591304): **SUCCESS**.
- Post-merge PostgreSQL 17 merged-schema [#42150591312](https://github.com/luzay-max/DecisionAtlas/actions/runs/42150591312): **SUCCESS**.
- B05 includes Argon2id writes, PBKDF2 verify-and-upgrade, login CAS, rollback compatibility docs, PHC parameter resource bounds, and deterministic SQLite/PostgreSQL 17 races for concurrent login/reset/disable. The final exact-head Windows suite and PostgreSQL 17 concurrency suite passed before merge; the post-merge main lanes above also passed.
- No production deployment, account password reset, bulk hash migration, or production credential operation was performed.

**Issue #38 / diagnostic PR #39 follow-up:**

- PR #39 was reconciled with current main; its independent current head is `8156427da7293c29cb286f67c8e07d90e3cfde6f`, compare **4 ahead / 0 behind**, with only `apps/web/tests-e2e/imported-evidence-preview.spec.ts` changed.
- Its exact-head Windows CI [#42153993432](https://github.com/luzay-max/DecisionAtlas/actions/runs/42153993432) completed **SUCCESS**: Node/API 58, Web 104, Engine 581 passed / 9 skipped, MCP protocol, offline evidence, benchmark fixtures, and Playwright 6 passed. No readiness-failure diagnostic was emitted. The older green run [#42001505707](https://github.com/luzay-max/DecisionAtlas/actions/runs/42001505707) predates B05 and is historical only.
- Issue #38 remains OPEN. Even a green retry on one SHA is not proof that the original intermittent failure's root cause has been eliminated. PR #39 remains Draft and has not been approved or merged.

**Next execution order (no automatic merge authorization):**

1. Finish reviewing #39 exact-head CI and its bounded failure diagnostics; keep #38 open until repeated fixed-SHA browser evidence is available.
2. Continue Stage B with an independent **B06** Draft: generate TypeScript API types/client from the Engine OpenAPI contract; check Fastify BFF route coverage and compatibility; align error DTOs and validate required environment configuration. Retain Fastify BFF and do not introduce a second hand-maintained API schema.
3. Treat **B07** as a design-only worker reliability decision until its lease/heartbeat/claim/restart and idempotent retry semantics are independently reviewed. Do not enable pause/resume; Issue #36 remains OPEN and `IMPORT_PAUSE_RESUME_ENABLED=false`.
4. After the remaining Stage B gates are explicitly dispositioned, begin **C01** read-only public GitHub issue/PR/review/inline-comment ingestion with bounded pagination, stable IDs/thread relationships, update/deduplication and fail-closed coverage reporting.
5. **C02 remains blocked** by the unapproved #34 schema/runtime migration. No #34 migration, backfill, versioned writer or re-extraction is authorized.

**Unchanged boundaries:** #34 remains NOT AUTHORIZED; #36 remains OPEN / DEFAULT OFF; integration-only #47 must NEVER be merged; private-source retention/erasure/backup operations and paid model calls remain separately gated. CI success is not production rollout or real retrieval-quality evidence.

### 13.14 B06a and B06b merged; B06c is the next implementation slice (2026-11-07)

**Current verified main:** `64030926fe7fb7a6dbb76bab980a10571beb199e` (B06b merge commit). The Draft status and unchecked acceptance boxes in the original PR descriptions below are preserved as historical review-time evidence; they are not the current disposition.

| Slice | Current disposition | Evidence | Remaining scope |
| --- | --- | --- | --- |
| **B06a / PR #51** | **MERGED** | Reviewed head `d759cee33b3cc70264713ff5de587b5aa0610f47`; merge commit `9925c9e22c024f574ffbfc8e3ff7a99be5696e9f`; post-merge Windows CI [#42192852069](https://github.com/luzay-max/DecisionAtlas/actions/runs/42192852069) SUCCESS and PostgreSQL 17 CI [#42192852563](https://github.com/luzay-max/DecisionAtlas/actions/runs/42192852563) SUCCESS | Engine OpenAPI route/method baseline and explicit 39-operation BFF inventory only; not DTO or runtime JSON validation for all routes |
| **B06b / PR #52** | **MERGED** | Approved head `2f40cd699af68c76f75293c86fc1059d5d27221c`; merge commit/current main `64030926fe7fb7a6dbb76bab980a10571beb199e`; post-merge Windows full CI [#42332050347](https://github.com/luzay-max/DecisionAtlas/actions/runs/42332050347) SUCCESS (API 69, Web 105, Engine 591 passed / 9 skipped, Playwright 6); PostgreSQL 17 CI [#42332050182](https://github.com/luzay-max/DecisionAtlas/actions/runs/42332050182) SUCCESS | Complete typed Engine → BFF → Web slice for existing `/query/why`; other response bodies remain unmodeled; TS client remains compile-time only |
| **B06c** | **NEXT / proposed independent PR** | No implementation or approval claimed yet | Model existing Decisions list/detail/review responses in Engine OpenAPI; type the existing BFF upstream calls and Web response/request types; preserve source references, review state, nullable/omitted fields, audit history and existing role/404 behavior; no new endpoints or permission changes |
| **B06d** | Proposed; not started | Separate follow-up after B06c | Independently model existing Imports and Auth/Team contracts; no duplicate interfaces; cover job status, credential redaction and session compatibility |
| **B06e** | Proposed; not started | Separate follow-up after B06d | Normalize error format and validate required environment configuration; distinguish unauthenticated, forbidden, invalid input and upstream unavailable without changing established status semantics silently |

**B06c acceptance gates:** generated Engine response DTOs for list/detail/review; current OpenAPI JSON and TypeScript declarations regenerated and freshness-checked; Fastify uses typed operations for all three existing paths; Web consumes generated types rather than hand-maintained duplicate decision DTOs; fixtures and negative type tests cover request/response shape, citation/source-ref fields, audit state, `null` values and empty collections; Engine tests confirm authorization and existing 400/401/403/404/422 behavior is unchanged. Full Windows CI and applicable PostgreSQL 17 CI must pass on the exact PR head. No schema migration, data backfill, new endpoint, worker enablement or production rollout.

**Next sequence:** finish B06c independently; then B06d and B06e as smaller separately reviewed slices. Only after the B06 contract work is dispositioned should B07's worker-reliability ADR and C01 public GitHub discussion ingestion become implementation work. B07 remains design-first; do not enable pause/resume.

**Unchanged boundaries:** #34 remains NOT AUTHORIZED / no migration; #36 remains OPEN / DEFAULT OFF; #47 remains integration-only and must NEVER be merged. No private-source operations, paid model calls, production deployment or credential changes are authorized by these records. CI success is engineering evidence, not proof of real repository quality or production readiness.