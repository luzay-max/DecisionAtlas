# Deployment | 部署指南

[English](deployment.md) | [中文](deployment_zh-CN.md)

---

## English Version

### Recommended v0.2 Architecture

DecisionAtlas v0.2 is designed as a single-machine demo deployment:

```
┌─────────────────────────────────────────────────────┐
│                    Public Traffic                    │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│                      Web (Next.js)                   │
│                  Port: 3000                          │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│              API (Fastify)                           │
│              Port: 3001                              │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│              Engine (FastAPI)                        │
│              Port: 8000                              │
└──────────┬───────────────────────┬───────────────────┘
           │                       │
┌──────────▼──────────┐  ┌─────────▼────────┐
│    PostgreSQL        │  │      Redis       │
│    Port: 5432        │  │    Port: 6379    │
└─────────────────────┘  └──────────────────┘
```

### Environment Variables

**Required:**

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string |
| `ENGINE_BASE_URL` | Engine service URL |
| `API_BASE_URL` | API service URL |

**For Live Provider Mode:**

| Variable | Description |
|----------|-------------|
| `LLM_PROVIDER_MODE` | Set to `openai_compatible` |
| `LLM_API_KEY` | Your API key |
| `LLM_MODEL` | Model name (e.g., `gpt-4o`) |
| `EMBEDDING_MODEL` | Embedding model name |

**Optional:**

| Variable | Description |
|----------|-------------|
| `EMBEDDING_API_KEY` | Embedding API key |
| `LLM_BASE_URL` | Custom LLM endpoint |
| `LLM_TIMEOUT_SECONDS` | Request timeout |
| `GITHUB_TOKEN` | GitHub access token |
| `DEMO_REPO` | Demo repository identifier |

### Bring-up Order

```powershell
# 1. Start infrastructure
docker compose up -d postgres redis

# 2. Run migrations
cd services/engine
uv run alembic upgrade head
uv run python -m app.db.seed_demo
cd ..\..

# 3. Start all services
pnpm --filter @decisionatlas/api dev
pnpm --filter @decisionatlas/web dev
```

### Network Security

- **Public traffic** → `web` (Port 3000)
- `web` → `api` → `engine`
- `engine` → `postgres` + `redis`

> ⚠️ **Important**: Never expose provider API keys to the browser. Keep them only on the host or inject into backend containers.

### Verification

After startup, verify:

1. Open `/workspaces/demo-workspace`
2. Run the demo import
3. Check `/review`
4. Ask a why-question on `/search`
5. Verify `/drift`

---

## 中文版本

### 推荐 v0.2 架构

DecisionAtlas v0.2 设计为单机器演示部署：

```
┌─────────────────────────────────────────────────────┐
│                    公共流量                          │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│                 Web (Next.js)                       │
│                 端口: 3000                         │
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

### 启动顺序

```powershell
# 1. 启动基础设施
docker compose up -d postgres redis

# 2. 运行数据库迁移
cd services/engine
uv run alembic upgrade head
uv run python -m app.db.seed_demo
cd ..\..

# 3. 启动所有服务
pnpm --filter @decisionatlas/api dev
pnpm --filter @decisionatlas/web dev
```

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
