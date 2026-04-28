# DecisionAtlas 发布说明：v0.3.0-rc.1

状态：release candidate 准备中  
计划 tag：`v0.3.0-rc.1`  
release 文档更新前的基线代码提交：`76d63ff`

## 相比 v0.2.2 的变化

- 平台地基已经进入产品可见状态：
  - 本地/bootstrap session 恢复
  - owner scope 切换
  - 针对 imported workspace 操作的角色门禁
- GitHub App 安装绑定已成为 admin/operator 产品流程：
  - admin 可以把仓库绑定到 installation-backed access source
  - workspace 和 lookup surface 可以展示 GitHub App access-source label
  - 完整 Marketplace/OAuth 自助安装仍不在范围内
- 私有仓库访问绑定已成为 admin/operator 产品流程：
  - admin 可以在当前 owner scope 内绑定 token-backed private access
  - 提交的 token 不会在产品结果中回显
  - 完整 secret vault 和轮换历史仍不在范围内
- 托管演示操作更清晰：
  - health、smoke、reset、reseed 脚本用于 operator-guided demo confidence
  - 本地 real/demo stack 入口已经清理
  - 已删除过期早期脚本：`scripts/dev/up.ps1`、`scripts/dev/prepare-demo.ps1` 和 `scripts/ci/run_demo_smoke.ps1`
- imported workspace 质量工作仍属于当前基线：
  - 有界 readiness 状态
  - review 质量改进
  - 以已接受决策为锚点的 why answer
  - 保守 drift 行为

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

本次 release candidate 验证结果：

- 2026-04-28 09:29 +08:00 通过，退出码 `0`。
- workspace 验证通过：API tests `25 passed`，web tests `55 passed`，API/web typecheck 通过。
- engine pytest 通过：`162 passed`。
- 离线 benchmark fixture validation 通过，覆盖 benchmark queries、live-repo fixtures、real-repo why/drift fixtures。
- Playwright smoke 通过：`1 passed`。
- 未发现阻塞 release 的验证不一致。

## 支持范围

- 稳定 seeded guided demo workspace
- 公共 GitHub 仓库导入到 imported workspace
- review、why、drift、evidence-limited、conversion-limited 等 imported readiness 状态
- candidate review 和 first accepted baseline 工作流
- 带支持度评级的引用优先 why answer
- 已接受决策背后的 chunk-backed supporting evidence
- rule-first 和保守 semantic drift evaluation
- 离线 fixture-backed 真实仓库 benchmark validation
- 本地/bootstrap session 恢复
- owner scope 切换和基于角色的产品操作
- 作为 admin/operator 流程的 GitHub App 安装绑定
- 作为 admin/operator 流程的 token-backed 私有仓库访问绑定
- hosted demo health、smoke、reset、reseed 操作员检查

## 已知限制

- v0.3.0-rc.1 不是最终生产级 SaaS release。
- 不包含完整 SaaS 组织管理。
- 不包含 billing。
- 不包含 GitHub Marketplace/OAuth 自助安装。
- 不包含 secret vault 和凭据轮换历史 UI。
- 不包含多人协作 review workflow。
- hosted preview readiness 是该 RC 基线之后的后续阶段。
- live real-repo validation 仍依赖操作员、provider 和网络条件。
- imported workspace 仍可能因仓库信号质量而稀疏。
- semantic drift 仍然保守且刻意收窄。
- drift 是手动评估，不是连续 watcher。

## Tag readiness

- 计划 tag：`v0.3.0-rc.1`
- release 文档更新前的基线代码提交：`76d63ff`
- 已验证 release-doc 工作树：2026-04-28 09:29 +08:00 pre-release validation 通过。
- 最终 tag 目标：包含这些发布说明和已归档 OpenSpec change 的 release commit。
- tag 前置条件：release commit 后不存在 active OpenSpec change，且 working tree 干净。
- tag 状态：尚未创建；仅在明确 release 确认后创建。

最终 release commit 创建并确认后，建议使用：

```powershell
git rev-parse --short HEAD
git tag v0.3.0-rc.1 HEAD
git push origin v0.3.0-rc.1
```
