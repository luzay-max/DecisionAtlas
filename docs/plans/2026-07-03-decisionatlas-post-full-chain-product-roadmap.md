# DecisionAtlas Post-Full-Chain Product Roadmap

日期：2026-07-03

## 当前结论

DecisionAtlas 已经具备完整链路 rehearsal 能力：

- OpenSpec 驱动开发和归档。
- CodeGraph 辅助结构理解。
- 真实浏览器 self-hosted 团队流程。
- 随机真实 GitHub 仓库诊断。
- release rehearsal。
- customer-host v2 证据管线。
- readiness history 趋势归档。
- team/account/review 权限边界。

当前最高层证据是 `full-chain-random-repo-release-rehearsal`，状态为 `warning`，0 blocking。这个状态说明产品链路已经能跑通，但还不能声称“真实客户主机 clean pass”。

## 当前证据边界

| 事项 | 当前证据 | 判断 |
|---|---|---|
| 浏览器人类流程 | `team-self-hosted-rehearsal.spec.ts` passed | 可作为 self-hosted 演示流程 |
| 随机真实仓库 | `n8n-io/n8n`、`Textualize/rich` | 已纳入 full-chain，但仍 warning |
| release rehearsal | `.tmp/release-rehearsal-evidence.json/md` | 可重复生成，仍有 warning lane |
| customer-host v2 | 示例模板 + 本机 evidence | 管线可用，不等于真实客户主机 proof |
| readiness history | full-chain/customer-host/release 等已归档 | 可做趋势证据 |
| 商业化准备 | self-hosted 路线、交付边界、销售材料已有 | 可以准备小范围试用 |

## 第一阶段：真实外部试用证据

目标：把“示例模板 + 本机证据”替换为“真实非本人机器/客户控制环境证据”。

建议 OpenSpec：

- `real-external-host-trial-evidence`（已完成证据门槛；真实外部机器 proof 仍需外部环境执行）

要做：

- 在干净 VM、朋友机器、客户机器或独立服务器上启动项目。
- 使用真实环境填写 `templates/external-customer-host-rehearsal-v2.example.json` 的副本。
- 跑 health check、浏览器页面、team/review/evidence 流程。
- 生成 customer-host v2 evidence。
- 再跑 full-chain random repo release rehearsal。

验收：

- customer-host v2 不再只是 example template。
- full-chain 仍可 warning，但必须明确 warning 来源。
- readiness history 有真实外部环境条目。
- real external host trial evidence 不再是 `template_or_placeholder`。

## 第二阶段：warning lane 降噪

目标：把 full-chain 中可改进的 warning lane 分批消掉。

建议 OpenSpec：

- `reduce-random-repo-import-warning-lanes`
- `stabilize-release-rehearsal-warning-lanes`
- `improve-real-repo-core-loop-quality`

要做：

- 分析 `n8n`、`rich` 或后续随机仓库的 warning 原因。
- 区分 provider/network、导入耗时、候选不足、why evidence limited、drift warning、guardrail not_provided。
- 优先解决“产品可控”的 warning。
- 对 provider/network 类 warning 只做分类和重试策略，不伪装成功。

验收：

- 至少一轮 full-chain 里 warning 数下降。
- 真实仓库 selected repo、lane status、recommended next actions 可对比。

## 第三阶段：小团队协作产品化

目标：只在真实试用反馈证明需要时，扩展协作能力。

建议 OpenSpec：

- `team-review-workspace-activity-feed`
- `workspace-invite-and-role-audit`
- `decision-detail-collaboration-history`

要做：

- 增强 workspace 活动流。
- 明确管理员、reviewer、viewer 的操作记录。
- 改善 decision detail 的 review/drift/evidence 上下文。

暂不做：

- 大型企业组织树。
- 复杂 SSO。
- 多租户计费后台。

## 第四阶段：商业化交付试点

目标：面向小团队 self-hosted 试用，而不是先做 SaaS。

建议 OpenSpec：

- `pilot-customer-trial-package`
- `self-hosted-trial-operator-checklist`
- `paid-pilot-evidence-report`

要做：

- 整理试用包。
- 固化安装前/安装中/安装后 checklist。
- 生成客户可读的 Code Decision Audit 和 handoff 报告。
- 收集真实使用问题，反推产品改动。

暂不做：

- billing。
- Marketplace。
- 自助 OAuth。
- 完整 hosted multi-tenancy。

## 第五阶段：是否进入 hosted/SaaS

进入条件：

- 至少 2-3 次外部 self-hosted 试用证明安装和核心流程稳定。
- warning lane 大部分可解释，且关键 warning 有降噪计划。
- 有用户明确要求托管版，而不是只要求本地部署。
- 有能力承担数据安全、备份、运维、告警、成本和支持。

否则继续坚持：

- 离线/自托管包。
- 小团队账号。
- 手动 token。
- 管理员手动导入仓库。
- 客户本地数据自持。

## 近期执行顺序

1. `real-external-host-trial-evidence`（已完成门槛）
2. `pilot-customer-trial-package`（已完成试用包装配入口）
3. `reduce-random-repo-import-warning-lanes`
4. `improve-real-repo-core-loop-quality`
5. 按真实客户反馈决定是否做协作深化或 hosted 路线

## 当前不应声明完成的事项

- 真实客户控制主机 clean pass。
- 生产级备份/恢复 SLA。
- hosted SaaS readiness。
- 多租户隔离。
- 自动计费和 license enforcement。
- Marketplace 分发。

## 下一次 full-chain rehearsal 标准

每次试用或 release 前运行：

- 随机真实 repo diagnosis。
- release rehearsal。
- customer-host v2。
- browser self-hosted flow。
- full-chain bundle。
- readiness history archive。

只有当这些证据能解释清楚，才进入客户演示或付费试点。
