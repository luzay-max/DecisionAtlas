# 2026-07-17 批准式离线依赖包更新日志

## 本次目标

为版本化 self-hosted package 提供可审计的依赖缓存：在联网环境准备，在隔离副本中验证并消费，缺失、篡改或平台不兼容时 fail closed。

## 已完成

- 新增 pnpm、uv、Playwright Chromium 和 allowlisted Compose images 的统一 bundle manifest、checksum、SBOM、prepare、verify 和 rehearsal 命令。
- 绑定 package commit/version、运行 manifest 与 lockfile，拒绝未列出文件、大小写冲突、危险路径、特殊文件、移动镜像引用和错误平台。
- 离线消费启用 pnpm/uv offline、黑洞 registry proxy、专用浏览器目录和 Docker `pull_policy=never`；随机 live repo lane 不能掩盖离线 lane 失败。
- Windows package workflow 和 readiness history 已纳入 bounded offline reports，缓存 payload 不提交也不自动发布。
- readiness 索引改为仓库相对路径，避免将开发者工作站绝对路径写入可提交证据。

## 真实验证

- 实现提交：`fa420c5`；版本：`0.4.0-offline-dependencies`。
- bundle：17,676 files、1,679,735,721 bytes、315 SBOM components、2 images；preparation 与 12/12 verification checks 均通过。
- isolated package rehearsal：7/7 stages 通过；pnpm `downloaded 0`，uv offline sync 通过，Docker image ID 与 manifest 匹配，local-only shell 无外部请求。
- fresh 随机公开仓库：`cokice/List-of-genshin-University`；imported workspace 的 Dashboard、Review、Why、Drift、Evidence 核心链路通过。
- 安装的 Google Chrome headed 模式复跑 1 passed；Chrome/Computer Use 插件初始化仍失败，因此只声明 Playwright 驱动真实 Chrome 通过。
- Canonical pre-release：engine 437、Web 83、API 32、Playwright 13/13；typecheck、benchmark fixture 和 OpenSpec strict 通过。
- readiness entry：`docs/evidence/readiness/2026-07-17-approved-offline-dependency-cache/`，离线依赖与 package verification 均为 `pass`、0 blocker。
- draft PR：`#6`；SHA `672cdf2` 的 CI run `29548155828` 和 Self-Hosted Package Rehearsal run `29548155821` 均为 `success`。
- Actions artifact：`self-hosted-package-rehearsal-29548155821`，945,592 bytes，检查时未过期。
- OpenSpec 主规格已同步，change 已归档到 `openspec/changes/archive/2026-07-17-support-approved-offline-dependency-cache/`。

## 状态解释

- release evidence 为 `warning`，但三个 required gates 全部通过；warning 来自 advisory guardrail `caution` 和可选 benchmark/trend 未提供。
- hosted readiness 为 `operator_guided`，因为没有 hosted URL 或 recovery drill；这不等于客户环境已交付。
- proof level 是 `process_enforced_offline_install`，`is_customer_controlled=false`；不声明 kernel network namespace、跨平台、发布签名或漏洞扫描。
- 约 1.68 GB bundle、Playwright trace、HAR 和临时安装目录只保留在本机临时区，不进入 Git 历史。

## 下一步

1. 在客户控制 VM/服务器接收版本化 package 和批准式依赖包，补齐真正的 external/customer-host proof。
2. 进入 3-10 人私有仓库 pilot，验证管理员、reviewer、viewer 分工和 token 处理边界。
3. 基于 pilot 故障推进升级、回滚和脱敏诊断包；billing、多租户、Marketplace、自助 OAuth 继续后置。
