## Context

DecisionAtlas 当前已经有一个可工作的 `v0.2.1` 基线，也已经具备 release checklist、`scripts/ci/pre-release.ps1`、curated real-repo benchmark fixtures，以及较完整的 README / quick start / demo script / release notes 文档。但这些内容还没有真正收成一个统一的发布基线：

- 维护者仍然需要知道哪些命令是 canonical，哪些只是单独文档里的提示
- `uv` 与 `python -m uv` 的环境差异虽然已有零散说明，但没有被明确收口到发布验证路径
- offline fixture benchmark 已经存在，但还更像辅助验证，而不是 release baseline 的明确组成部分
- demo lane 与 imported lane 的边界虽然已经具备产品和 spec 支撑，但 release-facing 文档还需要以统一口径表达

这个 change 因此不是新增产品功能，而是把当前 branch baseline 收口成“可重复验证、可解释、可发布”的基线。

## Goals / Non-Goals

**Goals:**

- 定义一个清晰的 release baseline validation 入口，作为本地发布验证的 canonical 路径
- 把 release checklist、pre-release 脚本、README、quick start、demo script、release-facing baseline 文档对齐
- 明确 offline fixture benchmark 是 release baseline validation 的稳定组成部分
- 保持 demo lane 与 imported lane 的边界在 release-facing 文档中一致且清楚

**Non-Goals:**

- 不新增 hosted demo 能力
- 不扩展 GitHub App、private repo、auth、roles 或 owner scope
- 不改变 imported why / drift / extraction 的产品行为
- 不把 optional live real-repo smoke checks 变成默认必须通过的 CI-like gate

## Decisions

### 1. Use the existing pre-release script as the canonical executable release gate

保留 `scripts/ci/pre-release.ps1` 作为本地发布验证的唯一 canonical 入口，而不是再新增第二套脚本或分散的命令清单。

这样做的原因：

- 现有脚本已经覆盖 `pnpm test`、`pnpm typecheck`、engine pytest、benchmark fixture validation、Playwright
- 它已经内建了 `uv` / `python -m uv` 的 fallback 逻辑
- 把 release baseline 固定在现有脚本上，比重新引入平行入口更容易保持一致

备选方案：

- 新增新的 release wrapper 命令。拒绝，因为会增加第二个“官方入口”，反而扩大文档漂移面。

### 2. Keep release-facing docs human-readable, but make them point back to the same executable validation path

README、quick start、demo script、release checklist、release notes 仍然保留各自面向读者的表达方式，但必须指回同一条可执行验证路径。

这样做的原因：

- 文档面向的读者不同，不适合强行统一成同一份文本
- 但验证入口和命令口径必须统一，否则维护者仍需要依赖隐含知识

备选方案：

- 把所有文档压缩成一处引用。拒绝，因为会损失面向不同读者的可读性。

### 3. Treat offline fixture benchmark validation as part of release baseline, not as optional supporting work

保留 lightweight real-repo benchmark 的“默认离线、fixture-backed”模式，并明确它是 release baseline validation 的组成部分。

这样做的原因：

- 当前 benchmark fixture 已经承担了 curated real-repo expectation 的回归保护职责
- 它比 live imports 更稳定，适合作为 release gate 的默认部分
- 如果不把它纳入 baseline，发布前验证仍会依赖维护者记得手动执行

备选方案：

- 把 live real-repo smoke checks 纳入默认 release gate。拒绝，因为这会引入 provider、网络、已有 imported workspace 状态等不稳定因素，不适合作为默认发布闸门。

### 4. Separate mandatory baseline checks from operator-guided optional validation

把发布验证拆成两层：

- mandatory baseline：默认必须执行，可离线或本地稳定执行
- optional operator validation：例如 live real-repo smoke checks，用于发布前增强信心，但不是默认 gate

这样做的原因：

- 当前项目仍处于“可信产品基线”阶段，不适合把所有真实世界验证都强行变成硬门槛
- 必须先保证默认 gate 稳定，再保留 operator-guided 增强验证

备选方案：

- 把所有验证都写成必须项。拒绝，因为这会让 release gate 过于脆弱，降低执行频率。

## Risks / Trade-offs

- [文档之后再次漂移] → 以 `pre-release.ps1` 和 release checklist 为 canonical source，其他 release-facing 文档都围绕这两处对齐
- [把过多人工检查塞进 baseline] → 区分 mandatory baseline 和 optional operator validation，不把 live smoke 直接变成默认门槛
- [继续保留多个读者文档会增加维护成本] → 接受这种成本，但要求它们共享同一条可执行验证路径
- [不同开发环境下 `uv` 仍可能不一致] → 明确把 fallback 口径写入 README、quick start 和 release baseline 文档

## Migration Plan

1. 先对齐 release-facing 文档和 release checklist 对当前 `v0.2.1` 基线的描述
2. 明确 `scripts/ci/pre-release.ps1` 是 canonical release baseline validation 入口
3. 把 benchmark fixture validation 在文档和 checklist 中明确为默认 release gate 的一部分
4. 把 optional live real-repo smoke checks 保留在 baseline / roadmap 文档中，但降级为 operator-guided validation
5. 用一次完整本地验证确认新的 release baseline 口径可执行

Rollback 很简单：如果本次文档和脚本收口引入混乱，可以回退到当前分散说明方式；因为这个 change 不引入数据迁移，也不改变产品运行时行为。

## Open Questions

- 是否需要为 `pre-release.ps1` 再提供一个 `pnpm` 别名，还是保留当前脚本入口即可？
- 是否要在 release-facing 文档中明确列出“当前推荐的 curated live smoke repo”，还是继续把这部分留在 baseline 文档中？
- 是否要在本 change 内顺手清理部分本地-only 文档，还是只先对齐它们的定位与引用关系？
