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

提供商密钥和仓库凭据必须保留在宿主机或后端面。不要把它们暴露到浏览器可见配置、客户端 bundle 或公开日志里。

## 车道边界

稳定公开演示使用 seeded workspace：

```text
demo-workspace
```

导入的真实仓库工作区是另一条由操作员管理的车道。它可以作为有界可信度检查，但不是主要公开演练路径，也不会被默认 demo 恢复脚本删除。

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
