# B06b：从 OpenAPI 路由清单到 Why 跨服务类型契约

状态：**B06b / PR #52 已于 2026-11-07 经维护者独立审批并合并**。合并提交 `64030926fe7fb7a6dbb76bab980a10571beb199e`；原 Draft／待审批措辞属于实施前历史状态，不代表当前状态。

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

## 实际处置与后续顺序

1. B06a #51 已完成独立审批并合并，merge commit `9925c9e22c024f574ffbfc8e3ff7a99be5696e9f`。
2. B06b #52 已完成独立审批并合并：审定 head `2f40cd699af68c76f75293c86fc1059d5d27221c`，merge commit `64030926fe7fb7a6dbb76bab980a10571beb199e`。
3. B06b 最终 head 的 Windows 完整 CI [#42193923821](https://github.com/luzay-max/DecisionAtlas/actions/runs/42193923821) **SUCCESS**，PostgreSQL 17 CI [#42193923865](https://github.com/luzay-max/DecisionAtlas/actions/runs/42193923865) **SUCCESS**；合并后 main Windows CI [#42332050347](https://github.com/luzay-max/DecisionAtlas/actions/runs/42332050347) **SUCCESS**（API 69、Web 105、Engine 591 passed / 9 skipped、Playwright 6），PostgreSQL 17 CI [#42332050182](https://github.com/luzay-max/DecisionAtlas/actions/runs/42332050182) **SUCCESS**。
4. B06b 只完成现有 `/query/why` 的 Engine → BFF → Web 类型契约；它没有模型化其他宽泛 dict 响应，也没有建立全局错误 DTO 或完成环境变量策略。
5. 下一项为独立 B06c：对现有 Decisions 列表、详情和审核响应建模，复用同一生成基础设施；保留引用、审核状态、nullable／缺省字段和权限语义。之后再分别处理 Imports/Auth/Team（B06d）及错误格式／环境校验（B06e）。

#34 不迁移；#36 继续禁用；#47 integration-only，绝不合并。无私有仓库、付费模型、生产部署或凭据变更。

技术依据：[FastAPI response model](https://fastapi.tiangolo.com/tutorial/response-model/)、[openapi-typescript Node API](https://openapi-ts.dev/node)、[openapi-fetch API](https://openapi-ts.dev/openapi-fetch/api)。
