# 2026-07-16 版本化自托管发布物更新日志

## 本次目标

把可运行 self-hosted source package 升级为可下载、可校验、可追溯的版本化 ZIP/tar.gz 发布物，同时保留独立 runner 与真实客户控制主机之间的证据边界。

## 已完成

- 新增确定性 release publisher：校验 package、version 和 commit，拒绝 symlink，按稳定顺序和规范化 metadata 生成 ZIP/tar.gz。
- 生成 `release-artifacts.json`、`SHA256SUMS` 和 CycloneDX 1.6 JSON SBOM；当前覆盖 278 个 npm 与 33 个 PyPI 锁定组件。
- 新增 fail-closed verifier：在任何保留解压前验证 hash/size、成员 parity、路径安全、重复成员、禁止内容、SBOM 和两种归档内的 package manifest。
- `--extract-verified-to` 只在全部验证通过后保留 ZIP 内容，并再次运行 package verifier。
- Windows package rehearsal workflow 生成并上传 release bundle 与 bounded evidence，不自动创建公开 GitHub Release。
- readiness history 新增版本化发布物证据族、index/trend 摘要、checksum 和 SBOM 附件。

## 验证结果

- 实现提交：`3cc30a2c783073c7d2d62b389ef8c50cf4628119`。
- 版本：`0.4.0-artifact-preview`；278 files；ZIP/tar.gz 内容一致；311 SBOM components。
- 专项 release artifact tests：14 passed；相关 CI/evidence tests：28 passed。
- Canonical pre-release：engine 424、Web 83、API 32、Playwright 12/12，typecheck 和 benchmark fixture 通过。
- OpenSpec strict：90/90；guardrail 为 advisory `caution`，`would_block=false`。
- readiness entry：`docs/evidence/readiness/2026-07-16-versioned-self-hosted-release-artifacts/`，release artifact blockers 为 0。
- GitHub Actions：CI run `29486627701` 和 Self-Hosted Package Rehearsal run `29486627752` 均为 `success`。
- Actions artifact：`self-hosted-package-rehearsal-29486627752`，约 906 KB，包含版本化发布物与脱敏报告，检查时未过期。
- OpenSpec 主规格已同步，change 已归档到 `openspec/changes/archive/2026-07-16-publish-versioned-self-hosted-artifacts/`。

## 真实仓库与浏览器

- 从 fresh GitHub search 随机选择此前未使用的公开仓库 `aristanetworks/j2lint`。
- 在源码 checkout 外的系统临时目录模拟下载 release bundle，完成校验、安全解压、冻结依赖安装和三服务启动。
- imported workspace 核心链路通过；可见 Google Chrome headed 模式完成 Dashboard、Review、Why、Drift 和 Evidence 导航，并保留本地 Playwright trace。
- Chrome 插件初始化报错 `Cannot redefine property: process`，因此不把插件控制声明为通过；真实安装的 Google Chrome 由 Playwright 驱动完成验证。

## 证据边界

- `SHA256SUMS` 不认证发布者；cryptographic signing 和 vulnerability analysis 尚未提供。
- SBOM 不覆盖 OS package、container image、runtime plugin 或漏洞扫描。
- 发布物不含 pnpm/uv/browser/container dependency cache，默认仍需要网络或 operator-approved cache。
- 当前 proof level 为 `independent_runner_release_artifact`，`is_customer_controlled=false`，不是客户主机安装证明。
- ZIP/tar.gz 二进制保留在 `.tmp` 和 GitHub Actions artifact，不提交到 Git 历史。

## 下一步

1. 在客户控制 VM/服务器接收同一版本化发布物，完成 operator 安装、账号分工、公开/私有仓库和恢复证据。
2. 实现 approved offline dependency cache，覆盖 pnpm、uv、Playwright browser 和 container image。
3. 进入 3-10 人私有仓库 pilot，再基于真实故障做升级、回滚和诊断包产品化。
