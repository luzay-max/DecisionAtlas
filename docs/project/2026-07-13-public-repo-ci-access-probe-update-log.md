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
- 修复 E2E 中 Why Search 页面错误的 `Repo:` 断言，改为验证真实 GitHub citation 的文本与 href。
- 允许通过 `PLAYWRIGHT_REAL_PUBLIC_REPO` 覆盖稳定默认仓库，便于在保留真实数据的前提下重复演练。

## 验证

- GitHub client + import preflight：33 passed。
- engine full：388 passed。
- 真实匿名 probe：pallets/flask = true。
- 本地首次 Playwright 已越过原 CI preflight，导入 1157 artifacts。
- 本地第二轮因首次真实 job 仍运行而触发 active import conflict；保留该真实数据，不做破坏性清理。
- 本地使用随机公开仓库 pallets/itsdangerous 完成真实核心浏览器链路：1 passed。
- GitHub Actions run 29380845943 全绿：Node、typecheck、388 项 engine、benchmark 和 12/12 browser smoke 全部通过。

## 边界

- fallback 只证明匿名 clone reachability，不提供 private access。
- 后续 API 请求若持续限流，import 仍会按 provider/network failure 诚实失败。
- OpenSpec 主规格已同步并完成归档。
