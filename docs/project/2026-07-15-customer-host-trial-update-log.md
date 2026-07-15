# 2026-07-15 Customer Host Trial Update Log

## 本次目标

把 self-hosted 交付从本地脚本 smoke 推进到可重复的客户宿主试用 checklist，并用真实公共仓库和真实浏览器保留完整证据。

## 实现结果

- 新增 customer-host trial schema、脱敏模板、operator checklist 和 self-hosted package 内容校验。
- 证据 collector 支持 startup、health、admin login、team/workspace、repository import、review、Why、Drift、continuity、browser smoke 等核心 lane，同时兼容 legacy 输入。
- 外部绝对路径、secret marker、raw source/raw model output 继续被阻断或脱敏；本轮没有把凭据写入证据。

## 真实验证

- 本地真实 Docker stack 作为 isolated self-hosted host，状态明确为 `warning`，不是客户控制主机证明。
- 随机选择新鲜公共仓库 `hynek/structlog`，全量导入 1,169 个对象，生成 26 个候选决策。
- 真实 Chrome 验证 13 个全局和 workspace 页面跳转；Why Search 实际调用后返回 `review_required`、0 citations，说明 accepted baseline 缺失时系统会 fail-closed。
- hosted readiness 没有外部 URL，因此保存为 `operator_guided`；团队账号分配、私有仓库和客户主机操作仍保留为 operator/customer lane。

## 回归与证据

- engine `399 passed`；API `32 passed`；Web `83 passed`；typecheck、benchmark fixture、OpenSpec strict 全部通过。
- package verification 通过；clean install、continuity 为 warning/operator-guided，无 blocker。
- release evidence 三个必需门禁通过，整体 `warning`；guardrail 为 `caution`。
- 固定 live benchmark profile 为 4/5 通过，n8n 1 个失败；该结果没有被隐藏。
- 证据文件：`.tmp/customer-host-trial-evidence.json/md`、`.tmp/customer-host-trial-release-evidence.json/md`、`.tmp/customer-host-trial-hosted-readiness.json/md`、`.tmp/customer-host-trial-benchmark-comparison.json/md`、`.tmp/customer-host-trial-team-handoff.json/md`。
- readiness history：`2026-07-15-customer-host-trial-release-rehearsal`。
- OpenSpec change 已归档为 `2026-07-15-complete-real-customer-host-trial`；实现提交 `76decc8` 已推送。
- GitHub Actions run `29391492181` 成功，远端 Windows CI 的 Node、typecheck、engine、benchmark fixture 和 browser smoke 全部通过。

## 边界与下一步

本轮证明了“本地隔离自托管 + 真实公共仓库 + 浏览器核心链路 + 证据归档”可复现，但还没有证明客户服务器上的安装和公开 hosted URL。下一刀优先补独立 VM/测试服务器的客户控制主机证据，再处理 accepted baseline/Why/Drift warning reduction 和 n8n benchmark 失败定位。
