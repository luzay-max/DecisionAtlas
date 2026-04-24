# DecisionAtlas 后续开发计划

日期：2026-04-24  
当前基线：`main` @ `615a4d4`  
状态：后续执行计划

## 当前判断

DecisionAtlas 当前已经越过了早期 MVP 和 v0.2 demo hardening 阶段。最近完成的几条主线已经把项目推进到新的状态：

- `release-quality-cleanup` 已完成并归档，默认 release baseline 已经有统一入口。
- `improve-imported-candidate-conversion` 已完成并归档，真实仓库导入后的候选决策转化能力更强。
- `improve-imported-review-readiness` 已完成并归档，imported workspace 已能区分 candidate-only、first accepted baseline、why-ready、evidence-limited、conversion-limited 等产品状态。
- 文档已经完成英文 / 中文拆分，并补齐 quick start、deployment、FAQ、demo script 等主文档入口。

因此，后续开发不应继续围绕“demo 能不能跑”或“真实仓库能不能导入”展开。新的主问题是：

```text
真实仓库能力能否被稳定验证、稳定展示，并逐步走向可发布和平台化。
```

## 总体路线

新的后续路线按下面顺序推进：

```text
1. v0.2.2 release baseline
2. live real-repo validation
3. imported review quality
4. hosted demo operator flow
5. v0.3 platform productization
```

核心原则：

- 先把当前主分支收成一个明确版本点。
- 再用真实仓库 live validation 验证 recent imported-lane improvements。
- 然后继续优化 review 到 accepted 的人工判断质量。
- hosted demo 放在真实仓库验收之后。
- GitHub App、private repo、login/scope 产品化最后进入，不提前抢主线。

## 阶段一：v0.2.2 release baseline

建议 change：

```text
prepare-v0-2-2-release-baseline
```

### 目标

把最近合入的 imported readiness、benchmark、Playwright smoke、双语文档等能力收成一个明确可发布的版本点。

### 范围

- 跑完整 `scripts/ci/pre-release.ps1`。
- 更新 README 当前阶段描述，不再停留在 `v0.2 Demo Hardening Complete`。
- 补 `v0.2.2` release notes。
- 确认中英文文档入口和限制声明一致。
- 打 tag：`v0.2.2`。

### 非目标

- 不继续改 extraction / why / drift 逻辑。
- 不引入 hosted deployment。
- 不做 GitHub App / private repo / login UI。

### 成功标准

- `pre-release.ps1` 通过。
- README、FAQ、release notes 对当前能力边界描述一致。
- tag 能代表当前主分支的稳定产品基线。

## 阶段二：live real-repo validation

建议 change：

```text
stabilize-live-real-repo-validation
```

### 目标

把 curated public repos 从“fixture 里有预期”推进到“真实运行后可复验、可记录、可解释”。

### 重点仓库

- `encode/httpx`
- `fastapi/fastapi`
- `Textualize/rich`
- `n8n-io/n8n`
- `browser-use/browser-use`

### 范围

- 扩展 live validation 命令，使它能检查 dashboard readiness、candidate count、accepted baseline、why status、drift status。
- 生成或更新 live validation report。
- 记录每个 curated repo 的 observed outcome。
- 保持 offline fixture validation 为默认 release gate。
- 把 live validation 作为 operator-guided release confidence layer。

### 非目标

- 不把 live validation 变成默认 CI 必跑。
- 不要求所有仓库都达到 demo 级别丰富度。
- 不用精确答案文本作为验收标准。

### 成功标准

- 每个 curated repo 都能落到明确状态：`review_ready`、`why_ready`、`evidence_limited`、`conversion_limited` 或其他可解释状态。
- `browser-use` 继续保护 known why/drift regression。
- `n8n` 继续作为 stress case，不能被误报成泛化失败。
- report 能回答“真实仓库路径现在哪里稳定、哪里仍弱”。

## 阶段三：imported review quality

建议 change：

```text
improve-imported-review-decision-quality
```

### 目标

提高 reviewer 从 candidate 到 accepted 的判断效率和信心，让 first accepted baseline 更容易由人类审阅形成。

### 范围

- 优化 review queue 上的 imported candidate 摘要。
- 显示更清晰的 source refs、artifact provenance、confidence、extraction family。
- 帮 reviewer 判断候选决策为什么值得接受或拒绝。
- 减少必须打开 detail 才能判断的情况。

### 非目标

- 不做多人协作 review。
- 不做权限 UI。
- 不重写 candidate extraction。
- 不把 review 做成复杂审批系统。

### 成功标准

- reviewer 能更快判断候选是否值得 accept。
- first accepted baseline 的产品路径更清楚。
- accepted 后 why/drift 的后续入口自然衔接。

## 阶段四：hosted demo operator flow

建议 change：

```text
prepare-hosted-demo-operator-flow
```

### 目标

把当前本地可运行产品整理成可管理、可恢复、可展示的 hosted demo 方案。

### 范围

- hosted 环境变量说明。
- provider key 和安全边界。
- reset / reseed 流程。
- health checks 和 smoke checks。
- operator guide。
- demo workspace 与 imported workspace 的线上隔离策略。

### 非目标

- 不做完整 SaaS。
- 不把 hosted demo 和 auth/private repo 同时推进。
- 不承诺生产级多租户。

### 成功标准

- demo 环境可恢复。
- 出问题时 operator 知道该重置哪一层。
- 外部展示时 demo lane 和 imported lane 边界清楚。

## 阶段五：v0.3 platform productization

建议 change 顺序：

```text
productize-login-and-scope-switching
productize-github-app-installation-flow
productize-private-repo-access
```

### 目标

把已经存在于 spec 和 backend 的平台地基，逐步补成用户可操作的产品流程。

### 范围

- login / session UI。
- owner scope switching。
- owner-scoped workspace navigation。
- GitHub App installation onboarding。
- private repo access setup。
- webhook incremental sync productization。

### 非目标

- 不一次性做完整 SaaS 权限系统。
- 不把所有平台能力压进一个超大 change。
- 不在 hosted demo 稳定前推进 private repo 产品化。

### 成功标准

- 用户能理解自己当前在哪个 owner scope。
- imported workspace 的可见性和操作权限能通过产品界面解释。
- GitHub App / private repo 不再只是后端能力，而是可操作流程。

## 推荐立即启动的下一条 change

下一条最建议启动：

```text
prepare-v0-2-2-release-baseline
```

原因：

- 当前主分支已经积累了多个关键改动。
- 这些改动已经推送，但还没有形成新的版本基线。
- 在继续 live validation 或 review quality 前，应该先让当前状态有清晰版本标签和 release 口径。

完成该 change 后，再启动：

```text
stabilize-live-real-repo-validation
```

这会把最近两轮 imported-lane 改进放到真实仓库上验收，为后续 review quality 和 hosted demo 提供依据。

## 暂缓事项

短期内不建议优先做：

- 新 connector。
- 大改 drift 架构。
- 完整 SaaS 化。
- private repo 产品化。
- GitHub App onboarding UI。
- 多用户协作 review。

这些方向都可以做，但应排在 `v0.2.2 baseline`、`live real-repo validation`、`imported review quality` 之后。

## 执行节奏

建议按 2 周为一个节奏推进：

### 第 1 个节奏

- `prepare-v0-2-2-release-baseline`
- 输出：release notes、tag、pre-release 结果、文档状态更新

### 第 2 个节奏

- `stabilize-live-real-repo-validation`
- 输出：live validation report、curated repo observed outcomes、benchmark/report 命令增强

### 第 3 个节奏

- `improve-imported-review-decision-quality`
- 输出：更强的 review queue、candidate evidence summary、review-focused tests

### 第 4 个节奏

- `prepare-hosted-demo-operator-flow`
- 输出：hosted demo operator guide、reset/reseed、smoke path、环境边界说明

### 后续节奏

- 根据 hosted demo 和 live validation 的结果，启动 v0.3 platform productization。

