# Hosted Preview Readiness（中文）

[首页](../README.md) | [快速开始](quick-start_zh-CN.md) | [部署](deployment_zh-CN.md) | [Hosted Operator Guide](hosted-demo-operator-guide_zh-CN.md) | [演示脚本](demo-script_zh-CN.md) | [English](hosted-preview-readiness.md)

---

这份清单用于把 DecisionAtlas v0.3 RC 准备成可外部展示的 hosted preview。它是运行环境上的 post-RC confidence layer，不替代本地确定性的 release gate：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ci\pre-release.ps1
```

## Preview 边界

hosted preview 不是生产级 SaaS release。当前不包含 SLA、billing、完整组织管理、secret vault、GitHub Marketplace/OAuth 自助安装、多人协作 review，也不承诺无限真实仓库导入。

稳定公开演示路径是 seeded guided demo：

```text
demo-workspace
```

真实仓库导入、GitHub App sync、token-backed 私有仓库访问都是可选 operator/admin 演示能力。它们依赖 provider、凭证、GitHub 和网络状态，不应成为完成公开 walkthrough 的前置条件。

## 最小环境条件

| 区域 | preview 前置条件 | 状态 |
| --- | --- | --- |
| Web | 公网 URL 可以访问 Next.js app | pass / blocking / known limitation |
| API | API health endpoint 可从 web 和 operator shell 访问 | pass / blocking / known limitation |
| Engine | Engine health endpoint 可从 API 和 operator shell 访问 | pass / blocking / known limitation |
| Database | `DATABASE_URL` 指向预期 PostgreSQL | pass / blocking / known limitation |
| Redis | `REDIS_URL` 指向预期 Redis | pass / blocking / known limitation |
| Seeded demo data | `demo-workspace` 存在且可完成 walkthrough | pass / blocking / known limitation |
| Recovery | reset/reseed 路径明确，条件允许时已演练 | pass / non-blocking / known limitation |
| Secrets | provider key 和仓库凭证只存在于后端/host surface | pass / blocking |
| Imported lane | 展示前已理解可选真实仓库 workspace 状态 | pass / non-blocking / known limitation |

## 必跑 operator checks

对外部 hosted 服务运行 health：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\health-check.ps1 `
  -WebBaseUrl "https://your-demo.example.com" `
  -ApiBaseUrl "https://your-api.example.com" `
  -EngineBaseUrl "https://your-engine.example.com"
```

运行 hosted guided-demo smoke：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\smoke-check.ps1 `
  -WebBaseUrl "https://your-demo.example.com" `
  -ApiBaseUrl "https://your-api.example.com" `
  -EngineBaseUrl "https://your-engine.example.com"
```

如果本轮没有可访问的外部 hosted 环境，不要把这些检查写成 passed；应在 readiness report 中记录为 `operator-guided / unavailable` 并保留重跑命令。

## Recovery drill

seeded walkthrough 状态漂移时先用 reset：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\reset-demo.ps1
```

迁移或更深数据漂移导致 reset 不够时用 reseed：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\reseed-demo.ps1
```

本地隔离 demo 数据库演练：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\reset-demo.ps1 -UseLocalDemoDatabase
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\reseed-demo.ps1 -UseLocalDemoDatabase
```

默认 reset/reseed 只处理 `demo-workspace`，不能被描述为 imported workspace 清理。

## 外部 walkthrough

1. 打开首页并说明边界：guided demo 使用稳定 seeded data；advanced/imported lane 是可选能力。
2. 打开 `/workspaces/demo-workspace`。
3. 确认 dashboard 给出下一步。
4. 打开 `/review?workspace=demo-workspace`，解释 human review。
5. 打开 `/search?workspace=demo-workspace`，提问 `why use redis cache`。
6. 打开 `/timeline?workspace=demo-workspace`，展示已采纳决策成为 durable memory。
7. 打开 `/drift?workspace=demo-workspace`，解释 conservative drift。
8. 可选：展示 imported readiness 或 admin access-source panels，但必须先说明 provider/凭证/网络依赖。

## 状态分类

- `pass`：hosted 环境或本地演练得到预期结果。
- `blocking`：公开 walkthrough 无法可靠展示，必须先修。
- `non-blocking`：公开 walkthrough 可继续，但可选 lane 或 operator 细节需要后续跟进。
- `known limitation`：检查依赖当前不可用的 hosted infrastructure、凭证、provider、GitHub 或网络状态，并已给出重跑命令。

## 演示前最低要求

外部 walkthrough 前，operator 应确认：

- web/API/engine health check 有记录。
- seeded guided demo smoke check 有记录。
- reset/reseed 命令明确，最好已经演练。
- 当前 readiness report 没有 blocking 项。
- imported/private lanes 已验证，或已明确从公开 walkthrough 中排除。
