# 2026-07-10 更新日志：真实仓库候选决策转 accepted baseline

## 本次完成

- 为真实导入工作区增加 dry-run-first 的候选决策检查和受控 accept 脚本。
- 对 `Textualize/rich` 的 `github-textualize-rich` 工作区执行真实审阅：候选数从 35 降到 34，accepted 从 0 增加到 1。
- accepted 决策为 `#241 Don't use windows legacy terminal support when ctypes is not available`，保留管理员、审阅理由和 3 条 GitHub 来源证据。
- 使用 Chrome 按真实用户路径检查 Review -> Decision Detail -> Why Search -> Drift。
- Why Search 实际发起 AI/检索调用，返回 accepted 决策和 GitHub 引用。
- 手动点击重新评估漂移，完成时间更新为 `2026-07-10T01:51:23.734929+00:00`，结果无漂移，浏览器控制台无错误。
- 归档 full-chain、warning reduction、review baseline 和 Chrome 截图证据。

## 验证结果

- pytest：23 passed。
- OpenSpec：84 passed，0 failed。
- full-chain：warning，0 blocking。
- warning reduction：11 个 operator-guided、3 个 product-controlled、0 blocking。
- guardrail：diff check pass；由于历史 drift/advisory 记录保持 caution，未将其伪装成 pass。

## 当前边界

- 本次数据来自真实公开仓库 `Textualize/rich`，不是 demo fixture。
- 本次复用了此前完成导入的 workspace，没有重新从 GitHub 全新导入。
- accepted baseline 只有 1 条，强度仍为 thin。
- customer-host 证据仍包含示例/本机边界，不能宣称真实客户主机已完全通过。

## 下一步

建议新开 `fresh-random-public-repo-import-rehearsal`：随机选择新的公开 GitHub 仓库，从零完成导入、分析、候选审阅、Why Search、Drift、guardrail 和 release evidence，避免复用已有 workspace，并将结果纳入趋势证据。
