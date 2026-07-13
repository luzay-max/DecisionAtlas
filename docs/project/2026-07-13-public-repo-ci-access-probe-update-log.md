# 2026-07-13 Public Repository CI Access Probe 更新日志

## 触发原因

GitHub Actions run 29221547589 的 Node、typecheck、engine、benchmark 均通过，Playwright browser smoke 中 11/12 通过。唯一失败是公开仓库 pallets/flask 的 metadata 请求在共享 Windows runner 上被返回为不可达，系统错误地提示配置 private credentials。

## 修复

- 新建 OpenSpec change：harden-public-repo-ci-access-probe。
- GitHubClient 增加匿名 Git smart-HTTP info/refs 探测。
- metadata 失败但 Git probe 200 时继续公开导入。
- metadata 401/404 且 probe 失败时保持 credential_required。
- metadata 403/429/5xx 且 probe 无法确认时返回 network_failure。
- 不调用 shell git，不绕过 private repository authorization。
- 修复 E2E 中 pallets/flask 模糊文本 locator 的 strict violation。

## 验证

- GitHub client + import preflight：33 passed。
- engine full：388 passed。
- 真实匿名 probe：pallets/flask = true。
- 本地首次 Playwright 已越过原 CI preflight，导入 1157 artifacts。
- 本地第二轮因首次真实 job 仍运行而触发 active import conflict；保留该真实数据，不做破坏性清理。
- 最终验收以全新 GitHub Actions runner 的 browser smoke 为准。

## 边界

- fallback 只证明匿名 clone reachability，不提供 private access。
- 后续 API 请求若持续限流，import 仍会按 provider/network failure 诚实失败。
- GitHub Actions 通过后再完成 OpenSpec 归档。
