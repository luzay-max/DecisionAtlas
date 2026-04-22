## Why

DecisionAtlas 已经有一个可工作的 `v0.2.1` 基线，但当前发布质量仍然依赖维护者了解许多隐含约定，例如哪些命令需要用 `python -m uv` 兜底、哪些文档才代表最新产品状态、以及哪些验证步骤才足以证明 demo lane 和 imported lane 都处于可信状态。现在需要把这些隐式知识收口成一个可重复执行的发布基线，避免主分支继续停留在“能用但不够可发布”的状态。

## What Changes

- 新增一套明确的 release baseline validation 能力，定义发布前必须验证的产品面、文档面和命令面
- 把当前 release checklist、pre-release 路径和 `v0.2.1` 文档口径统一到同一个基线
- 明确 demo lane 与 imported lane 在 release-facing 文档中的边界和预期
- 把 lightweight real-repo benchmark fixture validation 作为 release-style 验证路径中的稳定组成部分
- 收口本地开发与验证命令口径，减少 `uv` / `python -m uv` 这类环境差异带来的操作歧义

## Capabilities

### New Capabilities
- `release-baseline-validation`: 定义可重复执行的发布基线验证路径，包括产品检查、文档对齐和本地验证入口

### Modified Capabilities
- `lightweight-real-repo-benchmarks`: 让 fixture-backed benchmark expectation 明确成为 release baseline validation 的一部分，而不是零散的辅助脚本

## Impact

- 受影响文档：`README.md`、release checklist、quick start、demo script、release notes、roadmap / baseline docs
- 受影响脚本：`scripts/ci/pre-release.ps1` 及相关本地验证入口
- 受影响系统：本地开发验证流程、发布前 smoke / benchmark 验证流程、对外发布说明
