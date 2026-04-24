# DecisionAtlas 发布说明：v0.2.2

状态：发布基线准备中  
基线目标：当前 `main`，包含 imported readiness、benchmark、smoke 和双语文档更新

## 相比 v0.2.1 的变化

- 导入候选决策转换能力增强：
  - 更细的导入文档 family routing
  - 对可恢复的首轮失败执行有界 recovery extraction
  - recovery 跑尽后保留更清晰的转换诊断
- 导入工作区 readiness 更明确：
  - candidate-only 的 `review_ready` 与 first accepted baseline 进展分开表达
  - dashboard/search 会展示 accepted baseline 状态
  - why readiness 仍然受当前问题的 grounding 约束
- 导入 why-search 继续 fail closed：
  - 已采纳决策不会自动把不相关问题升级为可信答案
  - grounding 不足时返回 `evidence_limited`
  - `limited_support` 仍然与完全支持的 `ok` 区分开
- 发布验证更清晰：
  - `scripts/ci/pre-release.ps1` 是标准本地发布门禁
  - 离线真实仓库 benchmark fixture validation 已纳入默认路径
  - Playwright smoke 覆盖当前稳定 guided demo 主线
- 文档更清晰：
  - 英文和中文 README / 项目文档已拆分
  - quick start、FAQ、demo script 和发布文档会区分 guided demo 与 imported real-repo validation

## 标准验证

在仓库根目录运行发布基线门禁：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ci\pre-release.ps1
```

该命令覆盖：

- workspace tests 和 typechecks
- engine pytest
- 离线 benchmark fixture validation
- Playwright smoke coverage

本次发布基线验证结果：

- 2026-04-24 09:11 +08:00 通过，退出码 `0`。
- 覆盖 `pnpm test`、`pnpm typecheck`、engine pytest（`154 passed`）、离线 benchmark fixture validation、Playwright smoke coverage（`1 passed`）。
- 标准门禁没有发现 release-blocking mismatch。

## 支持范围

- 稳定的 seed guided demo 工作区
- 公共 GitHub 仓库导入到 imported workspace
- review、why、drift、evidence-limited、conversion-limited 等 imported readiness 状态
- candidate review 和 first accepted baseline 工作流
- 带支持度评级的引用优先 why answer
- 已采纳决策背后的 chunk-backed 支持证据
- rule-first 与保守语义 drift evaluation
- 离线 fixture-backed 真实仓库 benchmark validation

## 已知限制

- 尚未实现生产级 auth 和多用户产品 UI
- GitHub App onboarding 尚未产品化
- private repository 产品化尚未完成
- hosted demo operator flow 仍在计划中
- live real-repo validation 仍依赖操作员、provider 和网络条件
- imported workspace 仍可能因仓库信号质量而稀疏
- semantic drift 仍然保守且刻意收窄
- drift 是手动评估，不是连续 watcher

## Tag readiness

- 计划 tag：`v0.2.2`
- release-baseline 文档提交前的当前基线：`main` at `615a4d4`
- 计划 tag 目标：包含这些 v0.2.2 文档、验证证据和 OpenSpec 归档状态的 release commit
- tag 准备前工作树检查：当前仅有 release-facing 文档、后续开发计划和 OpenSpec change artifacts 处于修改或未跟踪状态；没有应用/运行时代码改动
- tag 状态：尚未创建；仅在明确发布确认后创建

release commit 创建并确认后，建议使用：

```powershell
git rev-parse --short HEAD
git tag v0.2.2 HEAD
git push origin v0.2.2
```
