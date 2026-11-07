# B06a 独立技术复审

审查对象：[PR #51](https://github.com/luzay-max/DecisionAtlas/pull/51)，提交 `d759cee33b3cc70264713ff5de587b5aa0610f47`。基线 `main@6bcb6161dddb55ed00731c940ffd82b759c011b9`。

## 结论

**在“路由／方法契约基础设施”的限定范围内，技术复审通过；等待维护者独立审批，未合并。** 这不是对完整 B06、DTO 类型安全、生产部署或 B06b 的审批。

## 源码核对

- 6 个变更文件，未改业务路由、权限、数据模型或 worker 行为。
- Python 生成器直接读取 `create_app().openapi()`，按路径和方法排序；非空检查和 `--check` 防止遗漏／陈旧生成物。
- 41 个 Engine operation；BFF 清单包含 39 个，使用 `satisfies readonly BffEngineRoute[]` 约束 Engine 方法／路径。
- `buildServer().hasRoute` 验证清单中的 BFF 路由真实注册；清单中 Engine operation 无重复。
- `/health` 仍是 BFF 本地端点；Engine governance lifecycle 未暴露到 BFF。现有 pause/resume 路由被列入清单不意味着打开功能开关。
- 没有重复实现已有 API。B06a 不包含新业务端点。

## 独立核对的 CI

证据均来自上述同一提交的 Actions job 与日志，不仅依据 PR 描述：

| 检查 | 结果 | 证据 |
| --- | --- | --- |
| Windows 完整 CI | 成功 | [42156957337](https://github.com/luzay-max/DecisionAtlas/actions/runs/42156957337)，job 127693290678 |
| 生成物 freshness | 成功 | Windows job 的独立检查步骤 |
| API / Web 单测 | 60 / 104 通过 | Windows job 日志 |
| TypeScript | 成功 | Windows typecheck 步骤 |
| Engine | 581 通过，9 跳过 | Windows job 日志；跳过不计作通过 |
| MCP、离线证据、benchmark fixture | 成功 | Windows 对应步骤 |
| Playwright | 6 通过 | Windows job 日志 |
| PostgreSQL 17 已合并 schema | 成功 | [42156956986](https://github.com/luzay-max/DecisionAtlas/actions/runs/42156956986)，job 127693289868 |

认证并发专用 workflow 本次路径过滤未触发；不冒称本次跑了全部 PostgreSQL 专用 lane。B06a 未改认证实现。

## 非阻断限制与 B06b 方向

1. 清单与真正的 `fetch` 构造仍是两个位置。测试能发现“清单指向未注册路由”，不能证明 handler 调用了清单声明的上游。
2. 清单只做单向注册覆盖检查，新增加且未写入清单的 BFF 路由不会自动失败。后续应按 operation 消费生成客户端并逐步完成覆盖审计。
3. OpenAPI 中多个响应仍是宽泛 `dict`。把这样的 schema 直接生成 TypeScript 不会自动得到有意义的响应类型。
4. 文档中 `satisfies readonly EngineRoute[]` 的文字已落后于实际 `BffEngineRoute[]`，不影响代码；本复审按实际源码判定。

建议 B06b 先完成现有 Why 查询的纵向契约：真实响应模型、可再生 DTO、BFF 实际调用、Web 类型引用、字段漂移负向测试；随后逐端点推广，避免以新增接口数量替代契约完成度。

## 未改变的边界

#34 不执行迁移；#36 保持禁用；#47 保持 integration-only，不合并。B06a 和 B06b 分别审批；B06b Draft 以 B06a 分支为基线仅为了复用未合并的生成基础设施。B06a 获批合并后，B06b 必须更新至新的 main、重新完整 CI 并单独审批。
