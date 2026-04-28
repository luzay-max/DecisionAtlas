# Hosted Demo Operator Guide | 托管演示操作指南

[English](hosted-demo-operator-guide.md) | [快速开始](quick-start_zh-CN.md) | [部署指南](deployment_zh-CN.md) | [演示脚本](demo-script_zh-CN.md) | [返回首页](../README_zh-CN.md)

---

本指南用于运维单机托管版 DecisionAtlas 演示环境。它是运行环境的操作手册，不替代默认的本地发布门禁。

## 环境契约

托管演示保持当前拓扑：

```text
public traffic -> web -> api -> engine -> postgres / redis
```

最小托管环境：

| 变量 | 所在面 | 必需 | 说明 |
|------|--------|------|------|
| `DATABASE_URL` | engine | 是 | 托管环境使用 PostgreSQL；SQLite 仅用于本地隔离 demo stack |
| `REDIS_URL` | engine | 是 | real stack 和导入任务协调需要 Redis |
| `ENGINE_BASE_URL` | api | 是 | API 访问 engine 的内部地址 |
| `API_BASE_URL` | web | 是 | Web 运行时或构建产物访问 API 的地址 |
| `DEMO_REPO` | engine | 可选 | 默认使用 seeded lane 的精选演示仓库 |

可选实时提供商环境：

| 变量 | 所在面 | 说明 |
|------|--------|------|
| `LLM_PROVIDER_MODE` | engine | 实时提供商使用 `openai_compatible`；seed/local smoke 使用 `fake` |
| `LLM_API_KEY` | engine | 后端专用密钥 |
| `LLM_MODEL` | engine | 实时模型名称 |
| `EMBEDDING_MODEL` | engine | 向量模型名称 |
| `EMBEDDING_API_KEY` | engine | 如果不同于 `LLM_API_KEY`，可单独设置 |
| `LLM_BASE_URL` | engine | 可选的兼容提供商端点 |
| `GITHUB_TOKEN` | engine | 可选，用于公共 GitHub rate limit |
| `GITHUB_APP_WEBHOOK_SECRET` | engine | 可选的后端专用密钥，用于校验 GitHub App webhook 签名 |

提供商密钥和仓库凭据必须保留在宿主机或后端面。不要把它们暴露到浏览器可见配置、客户端 bundle 或公开日志里。

## 车道边界

稳定公开演示使用 seeded workspace：

```text
demo-workspace
```

导入的真实仓库工作区是另一条由操作员管理的车道。它可以作为有界可信度检查，但不是主要公开演练路径，也不会被默认 demo 恢复脚本删除。

## GitHub App Webhook 同步操作

GitHub App 安装绑定是 admin/operator 设置流程。完整 GitHub Marketplace/OAuth 自助安装仍不在范围内，但操作员可以对已经安装的 GitHub App 验证 webhook 驱动的增量同步。

Webhook endpoint：

```text
POST /imports/github/webhook
```

预期 headers：

| Header | 必需 | 说明 |
|--------|------|------|
| `X-GitHub-Event` | 是 | 支持事件：`push`、`pull_request`、`issues` |
| `X-GitHub-Delivery` | 建议 | 作为排队同步的 delivery provenance |
| `X-Hub-Signature-256` | 当 `GITHUB_APP_WEBHOOK_SECRET` 已设置时必需 | 必须匹配后端专用 webhook secret |

验证路径：

1. 在 admin GitHub App setup 面板中，把仓库绑定到 installation。
2. 确认 workspace 或 lookup surface 显示 GitHub App installation access-source label。
3. 针对同一个 installation 和 repository 发送或重放支持的 webhook event。
4. 确认 workspace dashboard/readiness surface 显示 webhook-triggered sync provenance。
5. 保持默认发布门禁分离：live webhook delivery 是 operator-guided，不要求进入 `scripts/ci/pre-release.ps1`。

排障：

- `missing installation binding`：重放 webhook 前先绑定 repository 和 installation。
- `unmatched repository`：确认 webhook payload 中的 repository full name 与已绑定 imported workspace 一致。
- `invalid headers or signature`：检查 event headers 和 `GITHUB_APP_WEBHOOK_SECRET`；secret 必须只存在于后端。
- `duplicate active sync`：等待当前 queued/running sync 结束后再重放 delivery。
- `provider or network failure`：查看 latest import failure，在 provider/network 恢复后重放同一 delivery。

延期范围：

- 完整 GitHub Marketplace/OAuth 自助安装。
- 把 hosted live webhook delivery 纳入默认 release gate。

## 私有仓库访问操作

Token-backed 私有仓库访问是当前 owner scope 下的 admin/operator 设置流程。它用于有界的 hosted-preview 验证和受控真实仓库检查，不是完整 SaaS secret 管理。

推荐 token 边界：

- 使用只具备目标私有仓库读权限所需最小权限的 GitHub token。
- 优先使用专门给 hosted preview 环境准备的 token，而不是日常个人 token。
- 提交的 token 必须视为后端专用凭据，不应出现在浏览器可见配置、客户端 bundle、日志、截图或共享报告中。
- 当仓库权限变化、访问被撤销，或一次使用敏感数据的 hosted-preview 演练结束后，应轮换 token。

验证路径：

1. 以目标 owner scope 的 admin 身份登录。
2. 打开 private repository access setup 面板。
3. 提交 `owner/private-repo`、token 和便于操作员识别的 source label。
4. 确认产品结果显示 private GitHub source label、authorization status 和 workspace slug，且没有回显提交的 token。
5. 打开 workspace dashboard 或 readiness surface，确认 import、sync 或 review 操作前能看到同样的 access-source label 和 status。

排障：

- `missing source` 或 `credential_required`：为当前 owner scope 创建或重新绑定 private access source。
- `unauthorized`、`authorization_failed` 或 `invalid`：轮换 token，或授予它该仓库的读权限，然后重新绑定。
- `repository_not_found`：确认仓库名，以及 token 是否能看到这个私有仓库。
- `provider_failure` 或 `network_failure`：等待 GitHub 或网络恢复后重试；除非持续变成授权类失败，否则不要直接轮换凭据。
- `stale status`：重新绑定或重新跑一次校验导入，让 access-source status 反映当前 GitHub 权限。

延期范围：

- 不做 secret vault 或加密凭据管理 UI。
- 不做 token rotation history 或凭据审计日志 UI。
- 不做 GitHub OAuth / Marketplace 私有仓库自助接入。
- 默认 CI 或 `scripts/ci/pre-release.ps1` 不要求 live private repository credentials。

## 健康检查

针对运行中的托管环境执行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\health-check.ps1 `
  -WebBaseUrl "https://your-demo.example.com" `
  -ApiBaseUrl "https://your-api.example.com" `
  -EngineBaseUrl "https://your-engine.example.com"
```

针对本地 managed demo stack：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\health-check.ps1
```

该检查会验证 Web、API health、Engine health，并在操作员 shell 中存在 `DATABASE_URL` 或 `REDIS_URL` 时检查依赖可达性。

## Smoke 检查

健康检查通过后执行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\smoke-check.ps1 `
  -WebBaseUrl "https://your-demo.example.com" `
  -ApiBaseUrl "https://your-api.example.com" `
  -EngineBaseUrl "https://your-engine.example.com"
```

该命令会把 guided demo Playwright smoke 打到已经运行的 Web URL。它会设置 `PLAYWRIGHT_SKIP_WEBSERVER=1`，因此 Playwright 不会再启动本地服务。

## Reset 与 Reseed

当 seeded demo workspace 因演示交互、审核状态或临时数据变化而偏离稳定状态时，先使用 reset：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\reset-demo.ps1
```

当迁移可能不是最新，或托管数据库需要更深的 demo baseline 重建时，使用 reseed：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\reseed-demo.ps1
```

两个脚本都要求操作员 shell 中存在 `DATABASE_URL`。本地隔离 demo stack 可使用 `-UseLocalDemoDatabase`：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\reseed-demo.ps1 -UseLocalDemoDatabase
```

默认 reset 和 reseed 只作用于 `demo-workspace`。导入工作区不会被删除，除非后续有明确说明的 operator 脚本。

## 操作员检查清单

公开演示前：

- 确认后端密钥只存在于宿主机或后端面。
- 运行 hosted health check。
- 运行 hosted smoke check。
- 打开 `/workspaces/demo-workspace`。
- 把导入真实仓库证明保持为可选环节，与主演练分开。

如果演练状态不正确：

- 先运行 `reset-demo.ps1`。
- 如果 reset 不能恢复预期 baseline，再运行 `reseed-demo.ps1`。
- 重新运行 health 和 smoke checks。

## 与发布验证的关系

hosted checks 是针对运行中环境的操作员引导验证。默认分支和发布门禁仍然是：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ci\pre-release.ps1
```

## 已验证的本地操作员路径

最近验证日期：2026-04-24

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\dev\start-demo-stack.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\health-check.ps1 -SkipDependencyChecks
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\smoke-check.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\reset-demo.ps1 -UseLocalDemoDatabase
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\reseed-demo.ps1 -UseLocalDemoDatabase
```

这条路径会在本地隔离 demo stack 上验证操作员命令。托管环境应显式传入 `-WebBaseUrl`、`-ApiBaseUrl` 和 `-EngineBaseUrl`。
