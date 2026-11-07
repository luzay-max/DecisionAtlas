# B06b：从 OpenAPI 路由清单到 Why 跨服务类型契约

状态：独立 Draft；B06a #51 已经维护者明确批准并合并至 main@9925c9e22c024f574ffbfc8e3ff7a99be5696e9f。B06b 仍须独立审批，无自动合并授权。

## 解决的问题

现有 `/query/why` 的 Engine 返回类型是 `dict`，BFF 接收未约束 body 并手写 fetch，Web 独立维护响应类型。这使字段漂移能够绕过编译检查。例如 Engine 已返回 `answer_context.retrieval`，Web 手写类型却没有它。

本变更不增加业务接口。以现有 Why 查询为第一条完整纵向切片，保留其他接口的现状与显式边界。

## 实现

1. `services/engine/app/api/query_contract.py` 定义实际输出：回答状态、检索模式、引用、诊断、workspace readiness 和既有 HTTPException 错误体。Why 请求继续复用原有 `WhyQueryRequest`。
2. 原路由绑定 `response_model`。严格类型和 `extra=forbid` 阻止生产者悄悄改变响应；`response_model_exclude_unset=True` 保留字段缺省，不给 chunk 引用补造 source_ref_id，也不把缺省 primary_decision 改为 null。
3. 扩展 B06a 的同一个导出器，输出完整 OpenAPI；固定版本 `openapi-typescript` 生成共享 workspace 包。生成器使用 `uv --frozen`，无外部 schema 请求；`contract:check` 对比当前 Engine schema 和生成类型，均不允许陈旧。
4. BFF 的 Why 路由使用 `openapi-fetch`，路径、方法和 body 由生成类型约束；客户端仅接纳已审核的 Why operation，避免将其他宽泛 dict 响应误报为类型安全。
5. Web 保留原有 same-origin API transport、Cookie、Origin 和错误处理，删除 Why／readiness 手写类型，引用生成类型并用生成请求类型构造 body。

## 行为与兼容性

- 既有 200 响应结构、中文问题、检索模式、引用、retrieval 诊断及 nullable URL 保留。
- 401 / 403 / 404 / 422 / 502 / 503 的 Engine 状态和既有 detail 错误体透传；非 JSON 上游错误继续包装为 `{error: text}`。
- 网络异常继续使用原有 BFF 502 envelope。**成功状态但无效 JSON 现在返回该 502，而不是伪装成成功 message**；新增测试明确这个变化。
- `response_model` 在 Engine 运行时校验；TypeScript 客户端是编译期约束，不能独立验证任意远端 JSON 或旧版 Engine。部署混用版本仍须验证，不能把生成类型当成网络信任边界。
- 可选字段保留兼容范围；必填 question、answer、citations、answer_context、status 不放宽为 any。
- 本 PR 没有全局统一错误 DTO，也未改变现有 env Zod 校验。跨服务错误归一化与环境策略需下一独立范围评审，不用本次单端点契约冒充全部 B06 完成。

## 验证机制

- Engine、BFF、Web 共享同一份公开合成 fixture；Engine 通过实际 HTTP 路由验证后序列化，BFF／Web 精确比对字段。
- Engine 拒绝非法 status、错误引用类型、缺失 answer、未声明新增 evidence 字段；验证请求 422 和既有异常状态。
- TypeScript 负向用例覆盖错误路径／方法、缺少必填字段、错误字段类型、非法检索模式、nullable URL 和错误体误当成功响应；`@ts-expect-error` 变为无效时 CI 必须失败。
- 保留 B02+B03 的中文查询 + Cookie／Origin 组合断言；mock 改用真实 Request／Response 以匹配生成客户端的 fetch 接口。
- CI 增加完整 schema／DTO freshness，其余 Node、typecheck、Engine、MCP、离线、benchmark、Playwright 和适用 PostgreSQL 检查不删减。

执行：

```sh
pnpm contract:generate
pnpm contract:check
pnpm test
pnpm typecheck
cd services/engine
uv run pytest -q
```

完整远端 CI 结果以 PR 的**最终 head** Actions 为准；未完成前不标为通过。当地运行环境需 socksio 才能初始化预设 SOCKS 代理；该临时环境依赖不进入项目依赖锁文件。

## 后续顺序与审批

1. B06a #51 已完成独立审批并合并；审批未被 B06b 绕过。
2. 核对合并后 main CI，更新 B06b 基线并重跑完整 CI；单独审批 B06b。
3. 沿用同一套生成基础设施，优先将 Decisions／Imports／Auth 的现有响应模型化；每次明确可选／nullable、错误状态和敏感字段边界。
4. 逐步消除其余 handler 中与生成契约脱节的手写 fetch；最后再定义跨服务统一错误迁移方案和环境验证。

#34 不迁移；#36 继续禁用；#47 integration-only，绝不合并。无私有仓库、付费模型、生产部署或凭据变更。

技术依据：[FastAPI response model](https://fastapi.tiangolo.com/tutorial/response-model/)、[openapi-typescript Node API](https://openapi-ts.dev/node)、[openapi-fetch API](https://openapi-ts.dev/openapi-fetch/api)。
