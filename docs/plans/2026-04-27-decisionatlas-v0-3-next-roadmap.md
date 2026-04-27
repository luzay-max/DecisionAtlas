# DecisionAtlas v0.3 后续路线规划

日期：2026-04-27  
当前基线：`main` @ `d1bfc7e`  
状态：新一轮后续开发计划

## 当前状态判断

2026-04-24 的后续计划已经基本执行完。项目已经从“demo hardening / 真实仓库能力补齐”推进到“v0.3 平台化能力已初步产品化”的状态。

已完成并归档的关键主线：

- `prepare-v0-2-2-release-baseline`
- `stabilize-live-real-repo-validation`
- `improve-imported-review-decision-quality`
- `prepare-hosted-demo-operator-flow`
- `productize-login-and-scope-switching`
- `productize-github-app-installation-flow`
- `productize-private-repo-access`

当前最新提交：

```text
d1bfc7e chore: clean local stack scripts
4275be6 feat: productize private repo access
8d5cb71 feat: productize github app installation flow
20dcbbb feat: productize login and scope switching
34fcc0b feat: add hosted demo operator flow
```

当前 OpenSpec 状态：

```text
active changes: 0
```

当前能力边界：

- demo lane 已经稳定，有 health check、smoke check、reset / reseed 操作手册。
- real repo lane 已经能导入、复用 workspace、展示 readiness，并有 live validation 基线。
- review / why / drift 已具备 imported workspace 的基础产品闭环。
- login、session、owner scope switching、role gate 已进入产品界面。
- GitHub App installation binding 已有 admin UI。
- private repo token access binding 已有 admin UI。
- 本地 real stack / demo stack 启动入口已清理，当前推荐入口明确。

因此，后续不应继续以“再补一个功能”为主线。新的主问题是：

```text
DecisionAtlas v0.3 能否作为一个可发布、可验证、可演示的产品基线成立。
```

## 总体路线

建议后续按下面顺序推进：

```text
1. v0.3 release candidate baseline
2. v0.3 real stack validation
3. GitHub App sync operations productization
4. private repo access hardening
5. real repo decision value quality
6. hosted preview readiness
```

核心原则：

- 先冻结当前平台化成果，形成 v0.3 RC 基线。
- 再用真实运行矩阵验证，而不是只依赖单条 demo smoke。
- GitHub App 和 private repo 后续只做“闭环和硬化”，避免扩大成完整 SaaS。
- 核心价值仍然是“真实仓库里的决策记忆是否有用”，平台化只是让这条路径能稳定运行。
- 每一刀必须有明确验收命令、验收报告或用户可见结果。

## 阶段一：v0.3 release candidate baseline

建议 change：

```text
prepare-v0-3-release-candidate-baseline
```

### 目标

把当前 `main` 收成一个明确的 v0.3 RC 版本点，避免后续继续叠加 GitHub App、private repo、hosted preview 时缺少稳定参照。

### 范围

- 跑完整 `scripts/ci/pre-release.ps1`。
- 更新 README 当前阶段描述。
- 更新 quick start、deployment、FAQ 中关于启动、auth、scope、GitHub App、private repo 的说明。
- 补充 `v0.3.0-rc.1` release notes。
- 明确当前不是完整 SaaS：
  - 没有完整多租户管理台。
  - 没有 secret vault。
  - 没有完整 GitHub OAuth / Marketplace 自助安装。
  - 没有多人协作 review workflow。
- 打 tag：`v0.3.0-rc.1`。

### 非目标

- 不继续改 extraction / why / drift 逻辑。
- 不新增 GitHub App OAuth callback。
- 不新增 private repo secret vault。
- 不新增成员管理 UI。

### 成功标准

- `pre-release.ps1` 通过。
- README、quick start、deployment、FAQ、release notes 对当前能力边界一致。
- tag 能代表当前平台化基线。

## 阶段二：v0.3 real stack validation

建议 change：

```text
validate-v0-3-real-stack-flow
```

### 目标

用真实运行矩阵验证 v0.3 当前能力，而不是只验证 demo smoke。

### 验收矩阵

- local demo stack：
  - demo workspace
  - review
  - why search
  - drift
  - reset / reseed
- real Postgres stack：
  - Docker Postgres / Redis
  - migrations
  - seed
  - engine / API / web health
  - session bootstrap
- public repo import：
  - lookup
  - import
  - dashboard readiness
  - incremental sync
- login / scope：
  - session recover
  - scope switch
  - reviewer/admin role gate
- GitHub App binding：
  - admin-only setup
  - binding result
  - access-source label display
- private repo binding：
  - admin-only setup
  - token not echoed
  - access-source status display
- release gate：
  - health check
  - demo smoke
  - pre-release

### 输出

- 新增或更新 `docs/project/v0-3-real-stack-validation-report.md`。
- 每条链路记录：
  - command
  - observed result
  - pass / fail
  - known limitation
  - follow-up if needed

### 非目标

- 不把所有 live repo validation 放进默认 CI。
- 不要求 private repo / GitHub App 使用真实生产凭据完成全自动验收。
- 不在验证阶段扩大功能范围。

### 成功标准

- 形成一份可复查的 v0.3 real stack validation report。
- 主链路问题能被归类为 blocking / non-blocking / known limitation。
- blocking 项修完后，v0.3 RC 可以进入 hosted preview 准备。

## 阶段三：GitHub App sync operations productization

建议 change：

```text
productize-github-app-sync-operations
```

### 目标

GitHub App installation binding 已经有 UI，但 webhook / incremental sync 仍偏后端能力。该阶段要让安装后的同步状态在产品中可观察、可解释、可排查。

### 范围

- 在 workspace dashboard 显示 GitHub App-backed workspace 状态。
- 展示 latest sync origin：
  - manual full
  - manual incremental
  - webhook
- 展示 recent sync history。
- webhook-triggered sync 与手动 sync 在产品文案中区分。
- operator 文档补充 GitHub App webhook 配置、验证步骤、排障方法。
- 增加测试覆盖：
  - GitHub App-backed workspace lookup
  - dashboard sync provenance
  - webhook origin rendering

### 非目标

- 不做完整 GitHub OAuth Marketplace 安装流程。
- 不做 GitHub App 权限申请自动化。
- 不做复杂 sync job 管理台。

### 成功标准

- 用户能回答：“这个 workspace 是否由 GitHub App 维护？”
- 用户能看到：“最近一次同步来自 webhook 还是手动操作？”
- operator 能按文档验证 webhook 是否生效。

## 阶段四：private repo access hardening

建议 change：

```text
harden-private-repo-access-operations
```

### 目标

private repo token binding 已经可用，但仍需要安全边界、失败解释、状态展示上的硬化。

### 范围

- 明确 token validation 失败时的用户提示。
- 区分：
  - missing source
  - unauthorized source
  - expired / revoked token
  - repository not found
  - network failure
- dashboard / search / review 中一致展示 access-source label、status、detail。
- 文档补充：
  - 推荐 token 最小权限。
  - token 轮换建议。
  - 不要把 token 写入 workspace。
  - 当前不是 secret vault。
- 测试覆盖：
  - token 不回显。
  - owner scope 不能由 UI 手填覆盖。
  - 非 admin 不可提交。
  - authorization failure 有明确提示。

### 非目标

- 不做 secret vault。
- 不做 token rotation history UI。
- 不做组织成员管理。
- 不做生产级审计日志。

### 成功标准

- private repo 失败时，用户能知道是权限、配置、网络还是仓库问题。
- access-source 状态在主要产品界面一致。
- 安全边界在文档和 UI 中都清楚。

## 阶段五：real repo decision value quality

建议 change：

```text
improve-real-repo-decision-value-quality
```

### 目标

平台壳子已经补齐，后续必须回到核心价值：真实仓库里提取出的 decision 是否足够有用。

### 范围

- 复盘 curated repos 的 candidate 质量。
- 优化 review queue 中的 candidate summary。
- 强化 source refs、artifact provenance、confidence、extraction family 的展示。
- 减少 thin / low-value candidates。
- 让 accepted baseline 后的 why / drift 入口更自然。
- 更新真实仓库质量报告。

### 非目标

- 不重写整个 extraction pipeline。
- 不做多人协作 review。
- 不做复杂审批系统。
- 不把单个 repo 的特殊情况硬编码成产品逻辑。

### 成功标准

- reviewer 更快判断 candidate 是否值得 accept。
- first accepted baseline 更容易建立。
- why / drift 的价值不依赖 demo 数据。

## 阶段六：hosted preview readiness

建议 change：

```text
prepare-v0-3-hosted-preview
```

### 目标

把 v0.3 RC 变成可外部展示的 hosted preview，而不是只在本地成立。

### 范围

- hosted env checklist。
- demo reset / reseed 演练。
- real stack health / smoke 自动化。
- 外部演示脚本。
- 故障恢复手册。
- demo lane 与 imported lane 数据边界说明。
- 展示前 checklist：
  - health check
  - demo smoke
  - sample why query
  - sample drift page
  - imported workspace readiness page

### 非目标

- 不承诺生产级 SLA。
- 不做完整 SaaS billing / org management。
- 不开放无限真实仓库导入。

### 成功标准

- 外部演示前能用固定 checklist 判断是否可展示。
- 出问题时能按手册恢复 demo workspace。
- 外部用户不会误解为完整 SaaS。

## 推荐立即启动

下一条最建议启动：

```text
prepare-v0-3-release-candidate-baseline
```

原因：

- v0.3 平台化主线已经完成三刀：login/scope、GitHub App binding、private repo access。
- 当前 `main` 已经具备一个值得冻结的产品状态。
- 如果继续做 GitHub App webhook 或 private repo hardening，缺少 RC 基线会让后续问题难以归因。
- 先冻结基线，再做 real stack validation，能把“发布状态”和“后续增强”分开。

推荐执行顺序：

```text
1. prepare-v0-3-release-candidate-baseline
2. validate-v0-3-real-stack-flow
3. productize-github-app-sync-operations
4. harden-private-repo-access-operations
5. improve-real-repo-decision-value-quality
6. prepare-v0-3-hosted-preview
```

## 暂缓事项

短期不建议优先做：

- 新 connector。
- 完整 SaaS 多租户管理台。
- billing。
- secret vault。
- GitHub Marketplace 完整 OAuth 安装流程。
- 多人协作 review。
- 大规模 drift 架构重写。

这些方向都可能重要，但当前项目最需要的是把 v0.3 现有能力变成可发布、可验证、可演示的稳定基线。
