# Deployment | 部署指南

[English](deployment.md) | [快速开始](quick-start_zh-CN.md) | [常见问题](faq_zh-CN.md) | [演示脚本](demo-script_zh-CN.md) | [托管操作指南](hosted-demo-operator-guide_zh-CN.md) | [返回首页](../README_zh-CN.md)

---

### 推荐 v0.3 RC 架构

DecisionAtlas v0.3 RC 仍围绕单机演示或预览部署设计，并在现有 web/API/engine 拓扑上叠加明确的 owner-scoped 产品流程：

```
┌─────────────────────────────────────────────────────┐
│                    公共流量                          │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│                 Web (Next.js)                       │
│                 端口: 3000                          │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│              API (Fastify)                          │
│              端口: 3001                             │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│              Engine (FastAPI)                       │
│              端口: 8000                             │
└──────────┬───────────────────────┬───────────────────┘
           │                       │
┌──────────▼──────────┐  ┌─────────▼────────┐
│    PostgreSQL        │  │      Redis       │
│    端口: 5432        │  │    端口: 6379    │
└─────────────────────┘  └──────────────────┘
```

### 环境变量

**必需配置：**

| 变量 | 说明 |
|------|------|
| `DATABASE_URL` | PostgreSQL 连接字符串 |
| `REDIS_URL` | Redis 连接字符串 |
| `ENGINE_BASE_URL` | Engine 服务地址 |
| `API_BASE_URL` | API 服务地址 |
| `AUTO_BOOTSTRAP_AUTH` | 为本地 demo 和 real stack 启用本地/bootstrap session 恢复 |

托管环境中，`DATABASE_URL`、`REDIS_URL` 和提供商凭据应只存在于宿主机或后端服务面。浏览器可见配置只应包含访问 API 所需的 Web/API 地址。

**实时大模型提供商模式：**

| 变量 | 说明 |
|------|------|
| `LLM_PROVIDER_MODE` | 设置为 `openai_compatible` |
| `LLM_API_KEY` | 您的 API 密钥 |
| `LLM_MODEL` | 模型名称（如 `gpt-4o`） |
| `EMBEDDING_MODEL` | 向量化模型名称 |

**可选配置：**

| 变量 | 说明 |
|------|------|
| `EMBEDDING_API_KEY` | 向量化 API 密钥 |
| `LLM_BASE_URL` | 自定义大模型端点 |
| `LLM_TIMEOUT_SECONDS` | 请求超时时间 |
| `GITHUB_TOKEN` | GitHub 访问令牌 |
| `DEMO_REPO` | 演示仓库标识符 |

### 平台访问边界

v0.3 RC 包含以下 operator/admin 产品流程：

- 本地/bootstrap session 恢复和登录
- owner scope 切换
- 基于角色的工作区操作
- GitHub App 安装绑定
- token-backed 私有仓库访问绑定

RC 不包含完整 SaaS 组织管理台、secret vault、billing、GitHub Marketplace/OAuth 自助安装或多人协作 review workflow。

### 托管操作员流程

运行持久化演示环境时，使用托管操作指南中的检查流程：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\health-check.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\smoke-check.ps1
```

需要恢复时，先重置 seeded demo：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\reset-demo.ps1
```

当迁移或数据库漂移需要更深重建时，再使用 `reseed-demo.ps1`。默认恢复脚本不会删除导入工作区。

### 启动顺序

```powershell
pnpm run dev:real
```

停止本地 real stack：

```powershell
pnpm run dev:real:stop
```

只有在调试某一层服务时，才建议手动拆开启动。

### 网络安全

- **公共流量** → `web`（端口 3000）
- `web` → `api` → `engine`
- `engine` → `postgres` + `redis`

> ⚠️ **重要提示**：切勿将提供商 API 密钥暴露到浏览器端。只将其保留在宿主机上或仅注入后端容器中。

### 验证

启动后，按以下步骤验证：

1. 打开 `/workspaces/demo-workspace`
2. 运行演示导入
3. 检查 `/review`
4. 在 `/search` 页面提问
5. 验证 `/drift` 漂移检测

托管环境在公开演示前，请运行[托管演示操作指南](hosted-demo-operator-guide_zh-CN.md)中的检查。
