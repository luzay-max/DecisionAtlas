# DecisionAtlas · 跨项目 AI Agent 决策记忆 MCP 产品实施计划（提案）

> 日期：2026-10-22  
> 状态：**PROPOSED / Draft PR / 待人工审核**，不是已实施能力、交付承诺或生产可用性声明。  
> 规划基线：`main@9bc32ce739db0bebeaeb928c6fc979dca34fe005`。  
> 与 [框架借鉴计划 PR #11](https://github.com/luzay-max/DecisionAtlas/pull/11) 和 [README 精修 PR #13](https://github.com/luzay-max/DecisionAtlas/pull/13) 相互独立，两者仍在评审中；本 PR 只有计划文档，不涉及合并。  
> **实施前置门禁**：先完成 [2026-10-21 安全整改与真实仓库价值验证计划](2026-10-21-security-hardening-and-real-repo-validation-plan.md) 中的 P0 安全检查与证据质量门槛；该计划要求安全收口后冻结非必要新功能，转向实测，因此本文件**不能自行解除冻结或替代原有门禁**。后续开发需单独审批。

## 1. 一句话目标和明确边界

把 DecisionAtlas 从“Web 管理界面 + 本地 AI 治理脚本”扩展为**独立、可接入的工程决策与项目约束 MCP（Model Context Protocol）服务**：

> 当开发者用 Claude / Cursor / Codex / OpenCode 或其他支持 MCP 的 AI Agent，在本地拉取一个**公司内部仓库**或**第三方开源仓库**并持续开发时，Agent 能在工作开始、计划生成、代码修改和交付检查等节点主动获得“这个项目为什么如此设计、哪些决策已经被采纳、哪些约束不可随意偏离、当前变更是否与证据冲突”，帮助 Agent **在有人类授权的边界内持续自主实现任务**，而不是脱离历史决策盲写代码。

这里的“自动把握方向 / 自动开发”指**经配置的 Agent 依流程自动获取上下文、执行实现、运行测试，并遇到证据冲突时请求人类决策**；不表示 MCP 自身是自动写代码的 Agent，不表示所有宿主都必定自动调用工具，更不意味着未经审核的 AI 抽取结论有强制权威。

**首版必须可在 DecisionAtlas 仓库之外工作**，不能仅能检查 DecisionAtlas 自己的 `REPO_ROOT`。

## 2. 完成后的用户旅程（核心端到端场景）

### 场景 A：公司仓库（敏感数据，需授权）

1. 开发者在自己有权访问的机器上 `git clone` 公司项目并用支持 MCP 的 AI Agent 打开该目录。
2. 开发者显式配置/确认本地 DecisionAtlas MCP 和当前工作目录；MCP 使用**本地 `stdio`**，不默认联网、扫描其他目录或上传源码。
3. Agent 请求 `project_status`：识别工作区的规范化绝对路径、git 根目录、当前 HEAD、远端标识（必要时脱敏）和绑定状态。**识别不等于授权，不自动关联其他同名远端/Owner Scope。**
4. 用户确认仓库绑定、允许扫描的文件类别与数据边界后，DecisionAtlas 加载显式声明的 ADR / README / 设计规范 / OpenSpec / accepted decisions。若需要读取公司 Git 服务器 PR / Issue，则必须独立授权；没有权限即跳过，不偷偷用其他凭据。
5. Agent 在设计/编码前请求 `get_project_guidance` 或 `search_project_decisions`，拿到**可信状态明确、逐条来源可核验**的工程决策上下文；随后先给出任务计划再编码。
6. 编码中/提交前 Agent 请求 `check_change_against_decisions`（针对显式授权的当前工作区 diff），核对架构约束和未解决的冲突，并按 `continue / caution / pause / unknown` 处理；`pause` 时向人类提问，不擅自改规则以消除阻断。
7. 开发者复查代码与证据后决定是否提交；MCP 本身**不自动执行写仓库、合并 PR 或采纳治理规则**。

**隐私承诺的验收方式**：本地模式默认**仅本机**读写；用户明确启用共享 Engine、云模型或远端索引前，UI/CLI 必须展示数据去向、权限、可能的费用和可取消方式。源码、私有 URL、认证凭据不出现在日志、CI Artifact 或跨 Scope 检索中。

### 场景 B：陌生开源仓库（没有决策数据库）

1. 开发者 clone `pallets/click` 等公开项目，首次连接时状态为 `not_indexed`，而不是返回“已理解项目”。
2. 按用户确认的范围读取项目自带的 ADR、规范、开发文档；有网络与用户授权时**可选**获取 GitHub PR / Issue / Commit（保留真实合并状态、commit SHA、引用）。
3. 候选决策与已被人类确认的采纳决策**严格分离**；仅凭可访问的 URL、PR 合并、模型摘要或 FakeProvider 结果不能自动升级为“项目规则”。
4. Agent 可以引用候选作为“可能的历史背景，待复核”，但没有可信决策时应回报 `insufficient_evidence`，仍可遵循现有项目显式测试、规范和用户任务进行实现。
5. 后续显式同步更新后，旧决策需要标注索引 SHA、更新时间、是否 superseded/stale，不能把过时决策当作当前方向。

### 场景 C：开发者的连续迭代（理想的自主工作流）

`任务 → 识别 repo + scope → 读取已采纳决策与工程约束 → 形成计划（引用出处） → Agent 写代码并测试 → 对 diff 做建议性偏离检查 → continue / caution / pause / unknown → 人工 review / 合并`。

必须说明：不同 MCP Host 的“自动调用”取决于 Host 的工具调用策略与权限。提供接入说明、推荐触发点与可选宿主 Hook，但**不声称配置 MCP 就能保证 Agent 每次自动遵循**。验收需用真实客户端执行 E2E，不能只测模拟 JSON。

## 3. 当前资产与缺口（2026-10-22 的已知事实）

| 方向 | 已有代码 / 依据 | 状态与限制 |
| --- | --- | --- |
| 已审核 Decision 与 SourceRef | `services/engine/app/api/decisions.py`、Review API、Why Search | 可复用；候选与 accepted 的分离必须贯穿 MCP |
| 检索与 Why Search | `services/engine/app/api/query.py`、`app/retrieval/` | 存在 REST/Engine 能力；真实仓库引用正确率未达到本提案的 MCP 验收门槛 |
| Governance 规则 | `services/engine/app/api/governance.py` | 含 owner scope/role、规则复核与 `GET /governance/guardrail`；不代表 MCP 认证已完备 |
| 本地 Agent Guardrail | `scripts/governance/agent_guardrail.py`、`services/engine/app/governance/agent_guardrail.py` | 有机器可读 JSON 与 continue/caution/pause、测试；目前服务器端 Guardrail 使用固定 `REPO_ROOT`，**不适用于任意连接仓库** |
| 基础安全边界 | `services/engine/app/auth.py`、`apps/api/src/auth.ts` | 当前是 session/cookie + owner scope 模型；外部 MCP 客户端的授权、租户隔离仍需设计 |
| 标准 MCP | 当前 `main` 无可核实 MCP 服务入口、Tools/Resources 实现、Client 示例或协议级 E2E | **未实施**，不得把已有 REST/CLI 包装为“已支持 MCP” |
| 真实证据质量 | [`pallets/click` 8 候选独立核查](../validation/2026-10-21-pallets-click-eight-candidate-independent-audit.md) | FakeProvider 8 条候选的 AI 辅助初判为 0 接受 / 7 拒绝 / 1 不确定，**不是独立人类金标或真实 LLM 的准确率** |

在 PR #11 尚未合并/实施时，不将其 T0–T3 质量测试、其他框架依赖或计划目标视为可用实现；后续如复用其验收方法，应明确建立依赖并单独评审。

## 4. 目标技术架构与取舍

```text
Developer clones/opens arbitrary repository (company or OSS)
    |
    | explicit local project selection and read permission
    v
AI Agent Host (Codex / Claude / Cursor / OpenCode)
    |
    | MCP stdio: structured tool calls
    v
DecisionAtlas MCP Adapter (new, isolated, read-only v0)
    |  - project identity and verified path scope
    |  - permission & audit, data minimization and error contracts
    |  - tool registration; no direct write to Git
    v
Project Context Service (new abstraction)
    +-- local workspace resolver + docs/ADR/OpenSpec reader (allowlisted)
    +-- approved, scoped DecisionAtlas API/Engine client
    +-- optional explicit GitHub / enterprise Git data import
    +-- evidence verification + freshness + citations
    +-- advisory diff-check / guardrail adapter scoped to target repo
    |
    v
Trusted accepted decisions / reviewable candidates / explicit project docs
    |
    v
Evidence-grounded guidance -> Agent plans, codes, tests, asks for review
```

**优先选 Python 适配层**：已有 Python Engine / governance checks，首版隔离 MCP 适配器，调用已有业务能力并新增跨仓库上下文服务；不直接对外开放 DB、内部 Session 或无边界文件访问。正式选型前通过小型 spike 核对官方 MCP Python SDK **v2 稳定 API**、Python 3.11+、`stdio`、最低可用客户端、依赖锁定与版本兼容，不复制网上的旧 `FastMCP`/`initialize` 教程直接开工。

官方资料（实现前重新核验）：
- [MCP 规范](https://modelcontextprotocol.io/specification/2026-07-28)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Python SDK 文档](https://py.sdk.modelcontextprotocol.io/)

### 为什么先本地而不是远程？

- 公司源码、Token、策略和决策可能是敏感信息。**第一版坚持本地 `stdio` + 最小权限 + 无外发**。
- 若使用中心 DecisionAtlas Engine：必须显式选择服务器，且只有在经过客户批准的环境与 `owner_scope / workspace` 内请求，保持用户身份与角色语义；本地启动不意味着可访问公司云端索引。
- `Streamable HTTP`、组织级 SSO、OAuth/细粒度 Token、托管部署、企业数据驻留与 SaaS 计费统一放到后续阶段，不以 CLI 伪造这些能力。

## 5. MCP 接口合同（拟议而非已经可用）

### 5.1 MVP 只读 Tools

| Tool | 输入（最小） | 返回（必须） | 失败行为 |
| --- | --- | --- | --- |
| `project_status` | 由服务启动绑定的工作区；可选展示身份 | `project_id`、`repo_root`（必要时脱敏）、`head_sha`、`scope`、`indexed / not_indexed / stale / unauthorized`、来源目录/后端是否可用 | 不自动读取未授权目录 |
| `list_project_decisions` | `workspace_id`、`status=accepted`、限制数量 | 决策 ID、人工审阅状态、更新时间、摘要、来源引用 | 默认只列 accepted；无数据返回空和原因 |
| `search_project_decisions` | 问题、`workspace_id`、上限 | 排名、摘要、引用、证据强弱、采纳状态、索引 SHA | 低证据返回 `insufficient_evidence`，不自动升格 |
| `get_decision_evidence` | 决策 ID | 选择/取舍/约束/审核轨迹、源路径、commit/PR URL 与 SHA、来源片段定位 | 跨 scope 返回拒绝/隐藏，缺失来源显式标注 |
| `get_project_guidance` | 当前任务说明、有限长度 | accepted 约束、适用范围、可核验 citations、未定事项、时效、工作前检查建议 | 不把模型建议包装成已批准政策 |
| `check_change_against_decisions` | **绑定的**工作区 diff（默认本地由适配器安全读取）、必要的用户上下文 | `continue / caution / pause / unknown` + 冲突说明 + 对应已审核证据 + 建议测试 + 人工问题 | 上下文无法确定时返回 `unknown`，不误报 `continue` |

第一版不开放 `accept_decision`、`modify_governance_rule`、`push_commit`、`create_pr`、`merge_pr`、`execute_shell` 等写/执行型 MCP Tools。候选写入/人工复核、MCP Resources/Prompts 和远端服务均需单独验收、评审权限后再开放。

### 5.2 输出语义与可信程度（示例形状）

```json
{
  "project_id": "local/project-fingerprint",
  "workspace_id": "explicitly-bound-workspace",
  "repo_revision": "git-commit-sha",
  "index_revision": "source-snapshot-sha-or-null",
  "result": "caution",
  "evidence_status": "accepted_verified | source_document | candidate_unverified | insufficient_evidence | stale",
  "advisory_only": true,
  "decisions": [
    {
      "decision_id": "decision-id",
      "review_state": "accepted",
      "scope": "relevant-module",
      "claim": "source-supported decision statement",
      "citations": [{"source": "relative/path/or/url", "revision": "sha", "locator": "line-or-section"}]
    }
  ],
  "conflicts": [],
  "human_questions": [],
  "required_tests": []
}
```

字段名是**草案**，实现时以固定 schema、可机器验证的 JSON 结构及语义测试为准。`advisory_only` 的 `pause` 表示“向人类确认”，不等于自动 CI 阻断；`unknown` 与 `insufficient_evidence` 必须和真正的 `continue` 区分。

### 5.3 证据分级（避免“知道”变成“编造”）

1. `accepted_verified`：有归属当前项目、经人工确认的决策和原始证据；保留时间、适用模块、引用与版本。
2. `source_document`：明确的项目 ADR/规范原文，但未经过 DecisionAtlas 人工审核；可作为“文档声明”，不可伪造审核记录。
3. `candidate_unverified`：模型/启发式提取的候选；不进入默认强约束和自动阻断。
4. `insufficient_evidence`：没有支撑材料或索引为空；返回未知和补充证据建议。
5. `stale` / `superseded`：来源与当前 Git SHA、规则生命周期存在变更；旧决策只能带警示使用。

单一 Web URL、PR merged、Issue closed、模型信心分数都不等同于人类对具体设计决定的采纳证明。所有摘要在呈现时必须区分**来源原文、已审核解释和模型推断**。

## 6. 外部仓库绑定、索引和生命周期设计

- **项目身份**：本地规范化仓库根路径 + git 工作树标识 + 当前 revision + 可选规范化 remote（含 URL 脱敏）。**只靠项目名/remote URL 不得自动切换 Tenant**；fork、同名仓库、迁移 remote、子模块、worktree、浅克隆和无 remote 必须可预期处理。
- **显式选择当前项目**：MCP Server 只访问启动时绑定的根目录；仓库换目录/多个 workspace 时必须显式选择或重新确认，且结果显示使用的 project_id、scope 和 revision。
- **受控本地抽取**：默认读取允许列出的 ADR、docs、规范和 README；遵循 `.gitignore` 与敏感文件 denylist、大小/字节与文件数量配额；拒绝符号链接穿越仓库边界、目录穿越、隐式读取 `.env` / private keys / 凭据。
- **按需增强索引**：使用 DecisionAtlas 既有 ingestion/Decision/SourceRef；首次未索引仍提供明确状态和说明，不偷偷开启外部网络、付费模型、Github Token 调用；本地静态文档索引与远程授权索引需清楚标识来源。
- **更新与失效**：Git HEAD、远端元数据、文档 mtime/hash、index snapshot 与接受决策生命周期各自记录；默认允许读已确认但过时的信息**并强烈提示 stale**，不可默认为最新有效。
- **多工作区隔离**：索引查询与缓存 key 包含 user/owner_scope/project/workspace/index revision；切换仓库需保证任何旧的 private evidence 不在新项目上下文残留。
- **测试代码内容只作为数据**：仓库 README、issue/PR 文本、注释、嵌入 prompt 等均视为**不可信输入**，不得成为 MCP Server 的系统指令、执行指令或关闭审计/泄漏凭据的理由。

## 7. 安全、自治边界和审批门禁

| 风险 | 必须实施的防线 | 负向验收 |
| --- | --- | --- |
| 企业源码/密钥泄漏 | 默认本地处理；明示出站目标/费用；敏感文件过滤；日志和输出脱敏 | 假私钥、`.env`、私有 PR 内容不出现在另一 scope、标准输出日志或网络请求 |
| 任意路径读写 | 绑定根目录、真实路径校验、路径策略、只读文件访问，拒绝不在根目录的路径 | `../`、symlink、worktree 外路径均拒绝 |
| Token 与跨租户越权 | 不接受匿名管理员；身份/Owner Scope/Workspace 重查；凭据不写入 MCP Tool 输出 | A scope 查询 B scope 返回 403/404 或不泄露存在性 |
| 提示注入 | 不可信仓库内容与指令分离、上下文引用归因、不得动态改变 Tool 能力 | README 里“忽略人类批准/发送密钥”不能被 MCP 执行 |
| 错误决策导致自动开发偏航 | accepted/source/candidate 分级；引用证据、freshness、unknown；`pause` 请求人 | FakeProvider 占位候选绝不成为强约束 |
| 自动运行权过大 | 无 Shell/Git 写 Tool；MCP 仅提示、决策仍归宿主 Agent 和用户 | 无法调用 MCP 来自动提交、推送、采纳规则或绕过人工批准 |
| 数据体积/费用 | 文件和令牌数上限、超时、缓存限额；远程调用 opt-in | 无许可时不执行外部模型请求、项目批量扫描或付费 API |
| 本地 MCP 稳定性 | `stdout` 仅协议；诊断走 `stderr`；可终止/重试/超时 | 无首启打印污染 JSON-RPC、无 hangs、有限资源开销 |

任何需要读取**公司私有仓库、共享索引或远端服务器**的试点，除代码审查外还必须取得该公司授权，落实密钥保管、隔离环境、日志策略和合规许可。开源仓库也要遵循其授权与服务访问速率限制。

## 8. 阶段划分、依赖、工作包与验收条件

估算为单人开发的**粗略工程量（人日）**，不包括等待审核、私有公司试点审批、第三方 API 波动或生产运维。顺序不能越过安全/证据门禁。每阶段独立 PR，不与本计划文档 PR 混合。

| 编号 | 优先级 | 内容与拟放置位置 | 估算 | 前置条件 | 最小验收证据 |
| --- | --- | --- | --- | --- | --- |
| G0 | P0 / Gate | 安全整改与证据质量审核；对齐原执行计划、PR #11 可复用条目 | 1–2 | 本计划获批 | 记录安全放行决定、真实数据质量基线、冻结例外审批；未获批停止开发 |
| M0 | P0 | MCP SDK v2 技术 Spike；`stdio`、客户端兼容性、协议发现、受控退出与输出 | 1–2 | G0 | 可复现真实 Host 握手/发现工具的短日志与固定版本；未触及用户业务仓库 |
| M1 | P0 | `services/mcp/`（拟议）只读适配器 + `project_status` + 目录约束 | 2–4 | M0 | 客户端连接任意授权 clone；无 repo/not indexed/越界情形可测 |
| M2 | P0 | 显式 repo 绑定、文档输入与项目/Owner Scope 身份解析 | 3–5 | M1 | 两个同名及一个私有仓库模拟 fixture 互不串读；缺少授权时无网络访问 |
| M3 | P0 | `search/list/get_project_decisions` + 引用证据 + 信任状态；复用 Engine/REST | 3–5 | M2 + 证据门槛 | 返回真实 source locator/revision；候选/无证据/过时均标记，不能冒充 accepted |
| M4 | P0 | `get_project_guidance` 与只读 `check_change_against_decisions`，让 Guardrail 绑定**目标仓库**而非服务器 `REPO_ROOT` | 4–6 | M3 | 固定可追溯样例区分 continue/caution/pause/unknown；不执行更改或默认 CI 阻断 |
| M5 | P0 | 测试/接入/文档：真实 MCP Client 端到端、Windows/Linux、最少 2 种 Host 的兼容记录 | 3–5 | M4 | 从 clone → 上下文 → plan → 修改/测试 → 检查/人工提问 全路径复演，无强制写操作 |
| M6 | P1 | 显式的 GitHub/企业 Git 同步、版本更新、缓存清除与 Resync | 3–6 | M5 + 明确授权 | API 权限不足/私有数据/速率限制时降级；来源与索引快照关联 |
| M7 | P1 | 宿主触发策略、文档模板/Hook 示例、部分自动化反馈循环 | 2–4 | M5 | 至少 2 种 Host 的真实自动触发/提问测试；无能力的 Host 明确标注手动调用 |
| M8 | P2 | Streamable HTTP、远程 Token/OAuth/SSO、审计/配额与多租户部署 | 另行评估 | 私有数据试点、客户需求、独立威胁模型 | 经过身份与权限穿透测试后单独发布 |
| M9 | P2 | 人审候选提交、规则生命周期写 Tools、Agent 任务队列编排 | 另行评估 | 人工审核 UX 与原始安全门禁 | 必须独立授权/确认，不能让 AI 自行升级规则权威 |

M0–M5 的**粗估合计 16–27 人日（不含 G0，且取决于现有 Engine 可复用程度）**；只是排期与风险讨论的起点，不是承诺发布日期。优先产出**可在任意 clone 项目上工作的只读、可信上下文闭环**，不要先做远程平台或花哨的工具集。

## 9. 明确的 Go / Caution / No-Go 测量门槛

### 9.1 质量样本与执行方式（先定集，避免挑最好看的回答）

预定义小而严格的人工验收包：
- 开源试点 A：已核验的 `pallets/click` 真实 GitHub 证据（必须保留 FakeProvider 候选不可直接当作知识的负例）。
- 开源试点 B：另一份包含真实 ADR 或明确约束的公开仓库，具体仓库和固定 commit SHA 在独立审核包里签字；不要在本提案中虚构结果。
- 公司试点 C：经负责人批准的**脱敏/合成**私有仓库 fixture；未经公司授权不得接入真实公司仓库或公开任何内容。
- 任务类型：架构约束查询、变更与历史决定冲突、证据不足、候选未审核、规则 superseded、仓库/Scope 切换、恶意注释提示注入。

**每项测试留存**：repo SHA、任务、Agent Host/版本、调用工具与请求/响应（脱敏）、引用是否正确、人工裁决、时间/费用、发生错误时的状态。自动测试与模型自评分只能辅助，不等于人审结论。

### 9.2 MVP 发布建议门槛

| 类别 | Go | Caution | No-Go |
| --- | --- | --- | --- |
| MCP 协议互通 | `stdio` 接入、工具发现与调用、超时/异常，至少 2 种真实 Host 完成 E2E | 仅 1 种 Host E2E | 仅 mock/单元测试，无真实客户端 |
| 证据与方向 | **人工核查**的 accepted 决策引用准确率 ≥ 90%，且 ≥ 8/10 固定任务的推荐约束/冲突被人工判定支持；不足时返回 unknown | 指标边缘，需缩小开放范围并公开限制 | 错把候选/推断作为硬规则，或者编造来源 |
| 跨项目与安全 | 所有高风险隔离/路径/Token 负向用例通过，0 已知高严重度漏洞 | 只有低风险已知局限且列出缓解 | 任意私有数据串租户、越权读、敏感信息外发 |
| 自主开发辅助 | Agent 在 8/10 固定工作流的正确节点读取上下文；出现 `pause` 时**100%** 正确交接人工，不自动篡改规则；实际代码仍须测试/评审 | Host 不支持自动触发，需手动作为当前限制 | 过度自主导致无授权写入、绕过人审 |
| 可安装/可恢复 | Windows 和 Linux 从零安装、配置、连接、断开/重连均有可复现记录 | 仅开发者机器运行 | 依赖未锁定/无说明/无法重现 |

这些是**提议的放行阈值，尚无实际测量结果**。具体样本数和评分准则由人工评审确认后冻结；不能靠更换问题提高通过率。评审未通过时维持 `Draft` / `No-Go`，不因为 CI 绿灯就称为“完成 MCP 产品”。

## 10. 工程验收 Checklist（未来实施 PR 必须逐项勾选）

- [ ] 明确安装指令：在**其他** clone 项目目录能运行；MCP Host 真实调用，不依赖打开 DecisionAtlas 自己的源码目录。
- [ ] 录制/归档 MCP Client 的协议测试、tool discovery、`stdio` 输出净化、JSON schema 校验及超时。
- [ ] `not_indexed / unauthorized / stale / insufficient_evidence / superseded` 五类均有负向测试。
- [ ] 只读工具默认只能返回该身份该项目所允许的上下文，跨 Scope 和路径穿越测试通过。
- [ ] 仓库文本 prompt injection、secret leakage、恶意 symlink、重复项目 remote、fork / worktree / detached HEAD 有覆盖。
- [ ] Agent 先获取 accepted 决策和显式项目规范，再计划并执行任务；每一步明确是否真实调用了 MCP。
- [ ] 变更检查指向当前仓库 Git diff，不读写服务器运行目录；只有已核实约束才产生权威引用。
- [ ] 人工标签、具体证据、指标与 CI Artifact（脱敏）在 PR 里可复查。
- [ ] 公司仓库试点须单独得到许可并保留审计记录；没有授权只能使用合成样本。
- [ ] 对外 README 清晰区分“已支持 MCP”与“规划中”，避免预先宣传。
- [ ] 新依赖经许可/安全审查，锁定版本并在隔离 CI 验证 Windows/Linux。

## 11. 建议的实施 PR 拆分与原计划关系

1. **本 PR：仅本提案**。讨论产品场景、数据边界、指标和分期；不修改 Engine/MCP/前端。
2. **未来 PR A：G0 + M0**，冻结通过后的 SDK Spike 与协议测试；未获安全放行不可进入下一阶段。
3. **未来 PR B：M1–M3**，跨仓库身份与只读、可引用的决策检索。
4. **未来 PR C：M4–M5**，Agent 全流程辅助、风险控制、E2E 证据与客户端接入指南。
5. **后续独立 PR**：M6–M9 视真实使用反馈和企业安全需求决定，不自动排入主线。

本计划与 [框架借鉴 PR #11](https://github.com/luzay-max/DecisionAtlas/pull/11) 在质量 fixture、源引用校验上可能有可复用工作，但**该 PR 未合并、MCP 实现不以它已交付为前提**。与 [README PR #13](https://github.com/luzay-max/DecisionAtlas/pull/13) 不耦合；只有 MCP E2E 验收后才应更新 README 的“已实现”功能描述。

## 12. 提交给维护者审查的关键决策

请在未来实施任何编码 PR **之前**明确确认：

| 决策项 | 默认推荐（待审核） | 原因 / 需要确认 |
| --- | --- | --- |
| 产品核心 | **本地可自托管、证据优先的跨项目 MCP** | 先证明真实 Agent 能在任意公司/开源 clone 工作 |
| MVP 运行方式 | 本地 `stdio`，只读 | 避免早期远程权限、网络暴露与租户设计风险 |
| 索引的首选材料 | 授权范围内的本地 ADR/README/规范 + 已审核决策 | 先解决质量和来源，不强推全 GitHub 扫描 |
| 未审核候选 | 不作为默认强制规则 | 防止 FakeProvider/模型误判导致自动开发偏航 |
| AI 自动开发 | Agent 执行代码工作；MCP 提供指导与 `pause` 建议 | 明确写代码权属于宿主 Agent/用户权限，不属于 MCP |
| 公司私有数据 | 显式同意、默认本地、不远程同步 | 安全最小权限和企业机密边界 |
| 与当前安全冻结 | **G0 人工放行后方可写新功能** | 避免计划变更冲淡现有 P0 与真实价值门槛 |
| 下一步进入实现 | 先做协议 Spike，再做只读链路和真实 Host E2E | 阶段性交付，任何一步失败都可停损 |

**审批请求**：评审本计划是否准确表达“让 AI Agent 在别人的仓库里自动理解经审核的项目决策并谨慎持续开发”。批准本计划只代表认可产品方向与阶段门槛，**不等于授权接入任何公司源码、调用付费模型、启用远程服务、开放写 Tools、推送代码或合并实施 PR**。

## 13. 范围调整（2026-10-23）：复用既有导入，补齐 GitLab 与 Gitee，再统一暴露 MCP

**维护者新增诉求**：既然 DecisionAtlas 已有 GitHub 仓库接入与决策数据处理链路，避免重新建一套通用“克隆后本地扫描 → 自研索引”平台。以现有 Workspace / Import Job / Artifact / SourceRef / Candidate Review / Why Search / Governance 能力为**唯一可信数据链路**；新增 GitLab/Gitee 连接器及 MCP 适配层。

### 13.1 已有能力与不要重做的东西

- **复用**现有 `POST /imports/github`、`GET /imports/lookup`、`GET /decisions`、`GET /decisions/:id`、`POST /query/why`、`GET /governance/rules`、`GET /governance/guardrail` 和索引、抽取、审阅模块。
- **保留** GitHub 公开/私有仓库 + App/Token 授权的独立接入方式；外部 Agent 不需要重复下载一遍已在 Workspace 中的仓库资料。
- **新增** MCP 中的 repo identity → 有权访问的 Workspace 绑定、accepted 决策读取与引用追踪、可选基于用户当前 Git diff 的治理检查。
- 若用户工作区**没有索引**，默认回应 `not_indexed` / `import_required` 并提供显式人工启动导入入口；不能偷偷扫描本地目录、调用外部 API 或写入数据库。
- 现有 `services/engine/app/git_sources.py` 把 GitLab/Gitee 标记为 `provider_unsupported`；`local_path` 是 `operator_guided`。**它们不是已实现的导入能力**。不允许将“下拉菜单可选”描述为“已经支持”。

### 13.2 新增必须完成的仓库导入矩阵（正式交付范围）

| 数据源 | 首版能力 | 第二阶段能力 | 交付边界 |
| --- | --- | --- | --- |
| GitHub.com | 复用现有公开 + 已授权私有导入、full/since_last_sync、Workspace 绑定 | 改进已存在的凭据复核及来源时效 | 绝不回归现有安全与导入状态 |
| GitLab.com | **必须实现**：公开项目元数据、Issues、Merge Requests、Commits、README/ADR/docs → 既有 Artifact/SourceRef；全量导入与受控增量同步 | 明确批准后支持私有项目个人/项目 Token | 每个 artifact 保留 GitLab URL、MR `iid`/`state`、原始 source revision |
| GitLab Self-Managed | **必须实现**：管理员显式配置的 HTTPS GitLab 实例 + 只读授权，导入与 GitLab.com 等价 | 管理员批准的内部证书或内网代理策略 | 默认禁止任意 URL / 非批准 Host，防 SSRF、DNS 重绑定和元数据地址访问 |
| Gitee.com | **必须实现**：公开仓库元数据、Issues、Pull Requests、Commits、README/ADR/docs → 既有 Artifact/SourceRef；全量导入与受控增量同步 | 明确批准后支持私有仓库 API Token | 映射真实 Gitee PR 状态/合并状态与来源链接，拒绝“GitHub PR 默认语义” |
| 本地仓库路径 | 本次不是前三种远程接入的前置依赖；MCP 可以经授权识别本地 Git remote 并绑定已导入 Workspace | 受控本地文档导入能力单独评审 | 不将浏览器/服务端任意本地路径读取作为首版能力 |

**不把 GitLab、Gitee 标记为“已实现”，直到公开仓库真实导入、增量同步、审阅、Why Search、真实 MCP Host 查询均通过验收。**

### 13.3 实施技术任务：一个正规化 Provider 接口，而不是三套决策系统

1. 抽象 `GitProviderClient` 的读取合同：`get_repository_metadata`、`get_default_branch`、`fetch_issues`、`fetch_pull_requests`（GitLab 为 MR）、`fetch_commits`、`list_repository_files`、`fetch_markdown_document`。统一映射为现有 `GitHubArtifactPayload` / `GitHubRepositoryFile`（后续可重命名为 provider-neutral 的 payload，不必重建数据库）。
2. GitLab 从官方 `/api/v4/projects/:id`、`/issues`、`/merge_requests`、`/repository/commits`、`/repository/tree`、`/repository/files/:path/raw` 读取；项目完整路径须 URL-encode，`PRIVATE-TOKEN` 只能用于审批通过的实例，支持响应中真实的下一页链接、限额、重试和中断。
3. Gitee 从官方 `https://gitee.com/api/v5/repos/{owner}/{repo}`、`/issues`、`/pulls`、`/commits`、`/contents` 及递归文件树能力（以官方 API 支持范围为准）读取；鉴权只在批准的域名使用，验证分页、速率限制、返回字段、404/401/403 分类。
4. 对外源 URL **按平台构造**（GitLab 文档路径 `/-/blob/<revision>/...`、GitHub/Gitee `/blob/<revision>/...`），并记录 project canonical id、provider、完整 repo identity、source id、SHA、采集时间和状态；当前 `GitHubImporter` 文档 URL 逻辑不能原封不动用于 GitLab。
5. 复用现有 `GitHubImporter` 中的文档筛选、Artifact upsert、索引、候选抽取、review、why/drift 流程；将调用方重构为 provider-neutral import orchestration，逐步让既有 Github 测试持续通过，不得跳过审批链路。
6. 新增 `POST /imports/git-sources/import` 或等效**经过鉴权**的通用导入任务入口；与既有 `/imports/github` 共存。对 `provider=gitlab/gitee` 检查 `owner_scope` + admin 角色，支持显式绑定、去重、导入任务状态、full/since_last_sync 与审计；**不能复用 GitHub 的 Token 存储表/加密格式假装通用**，需设计安全的 provider-scoped 凭据记录与轮换。
7. 接入 MCP 时，只按 repo remote / canonical URL 查当前 actor 已授权的 Workspace；用户明确发起才可执行新的导入。MCP `list/search/get evidence` 仍按统一 accepted/source/candidate 语义返回；同名 repo 不跨 Provider、Owner Scope 或 Worktree 串读。

### 13.4 安全与质量的硬性验收

- [ ] 真实公开 GitLab.com 与 Gitee.com 仓库各至少一次**固定 SHA** 的端到端导入，Artifacts/SourceRef、候选与 Why 的数据可追溯；未进行人工核验时不能宣称抽取正确率。
- [ ] GitLab 自建实例使用可控测试容器/Mock HTTPS 环境验证 allowlist、代理、DNS 重绑定、拒绝私网任意 Host 的安全边界；不把任意第三方 URL 接进服务器端抓取器。
- [ ] 各平台全量/增量、重复运行幂等、分页、限速、异常/退避、中途取消、空仓库、被删除/重命名的 repo 均有测试。
- [ ] 私有仓库 Token 测试只使用假凭据或经授权的隔离环境，含加密、权限撤销、轮换、跨 Scope 越权和日志脱敏。
- [ ] GitLab MR `merged`、Gitee PR `merged`/`closed` 与“决策已采纳”严格分离；FakeProvider 候选绝不升级为 accepted。
- [ ] GitHub 旧导入、后续 Decision/Review/Why/Drift 及 Node/Python/Browser CI 无回归。
- [ ] 对两个真实 MCP Host 完成 GitHub/GitLab/Gitee 的查找、决策读取与状态标记 E2E；默认只读并遵守身份边界。
- [ ] 新提供者的公开可用性/私有凭据行为，只有通过验收后才更新 README 为“支持”，否则应标注 `experimental` 或 `not_implemented`。

### 13.5 修订优先级与可审查的实施 PR

| 实施 PR | 交付 | 依赖 / 边界 |
| --- | --- | --- |
| **A0：连接器基础** | GitLab/Gitee 客户端、统一 payload 映射和只读 HTTP Mock 契约测试 | 不接凭据持久化、不宣称端到端、保持独立 Draft |
| **A1：GitLab 端到端** | GitLab.com + 可配置的受信 Self-Managed 环境，导入、任务、索引/审阅/Why | G0 放行、授权/SSRF、数据库与工作流复用 |
| **A2：Gitee 端到端** | Gitee.com 同等导入、鉴权、增量、状态、索引/审阅/Why | G0 放行，含独立平台语义和限速测试 |
| **B0：MCP 最小读链路** | MCP `stdio` 服务，Workspace 绑定，4–6 个只读 Tools，真实 Host 集成 | 可先复用 GitHub 已导入 Workspace；A1/A2 独立并行 |
| **B1：全平台 Agent 场景** | GitHub/GitLab/Gitee 上的开发前 Why、决策引用、diff advisory，Host 接入和安全测试 | A1+A2+B0；人工证据门槛和安全策略均满足 |
| **C：增强项** | 授权私有 Token、多 Host 触发与远程 MCP、受控本地导入 | 按企业试点批准程度拆 PR，不把未经批准功能静默上线 |

**更新后的关键路径**：`已有 GitHub 核心能力 + A0（Provider 适配）→ A1/A2（真实平台落地）║ B0（并行 MCP 接口）→ B1（跨平台 Agent E2E）`。这取代前文将“重新建立本地扫描和上下文索引”作为首要任务的建议；第 8 节原人日预估**不包含 GitLab/Gitee 的实现和安全验证**，必须在 A1/A2 独立估算后再报总工期。

### 13.6 需要维护者确认的交付准则

- **GitLab/Gitee 是确定要做的范围**，而非“以后也许有”的扩展项；但任何代码 PR 都须逐个 CI/安全/人工证据验收。
- 无法获取某个公司的私有仓库授权时，该环境只能标记为 `operator_guided / blocked`，不能编造通过结果。
- GitLab Self-Managed 默认要明确批准受信主机；对于公司内网不要求强制公开访问，也不应为方便使用而移除 SSRF 防护。
- 计划审核、CI 通过与完成真实导入/MCP E2E 是不同阶段；**不将本规划 PR 当成实现完成**。

**参考 API 文档（实现前确认当前版本）**：[GitLab REST](https://docs.gitlab.com/api/rest/)、[GitLab Merge Requests](https://docs.gitlab.com/api/merge_requests/)、[Gitee Open API v5](https://gitee.com/api/v5/swagger)。
