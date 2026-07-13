# DecisionAtlas 后续开发总计划（2026-07-13）

## 当前产品判断

DecisionAtlas 已经具备可重复的自托管完整链路：

```text
部署/启动
  -> 登录与 owner scope
  -> 公共/私有 Git 仓库接入
  -> artifact 导入与索引
  -> 模型 screening/extraction
  -> candidate 人工审阅
  -> accepted baseline
  -> grounded Why Search
  -> Drift 评估
  -> guardrail / release / hosted / benchmark evidence
  -> 日期化 readiness history
```

当前主要问题已经从“链路缺失”转为“真实使用质量和交付可信度”：

- candidate 数量可能过多且置信度偏低，审阅成本高。
- governance findings 存在重复展示，噪声会淹没有效动作。
- sparse recovery 能诚实工作，但真实 recovered candidate 成功率仍缺少跨仓库趋势。
- 外部客户控制主机仍没有 clean proof。
- 私有仓库安装与团队协作已具备基础能力，但还缺真实 pilot 的持续反馈。

## 优先级路线

### P0：治理 finding 去重与 dashboard 降噪

建议 change：`deduplicate-governance-drift-findings`

目标：

- 相同 rule、historical issue 和 next action 在一次 guardrail 结果中只显示一条主 finding。
- 保留 occurrence count、最新时间和可展开证据。
- dashboard 默认只展示最高优先级的有限条目。
- CLI、API、UI 和 evidence 中保持同一去重语义。

验收：

- 当前 pip-tools dashboard 不再重复几十条 `repeated_postmortem_issue`。
- 不丢失 finding 总数与审计证据。
- API/组件/浏览器回归通过。

难度：中等，预计 1 个 change。

### P1：候选精度、排序与批量审阅

建议 change：`improve-imported-candidate-precision-ranking`

目标：

- 把 grounded refs、confidence、artifact family、salvage 状态和重复语义纳入 ranking。
- 对近重复 candidates 聚类，避免一次导入产生大量相似审阅项。
- 将 strong / partial / weak candidate 分层，默认优先展示 strong。
- 支持批量 reject weak/duplicate，但不支持批量 accept。
- 建立 candidate precision benchmark：accepted、rejected、duplicate、unsupported 比例。

验收：

- 用 pip-tools 28-candidate baseline 做回归。
- 首屏候选质量和人工审阅耗时明显改善。
- 不降低 source grounding。

难度：高，预计 2-3 个 changes。

### P2：Sparse conversion 多仓库趋势

建议 change：`benchmark-sparse-conversion-trends`

目标：

- 每个 release 随机选择至少一个 fresh repo。
- 记录 normal/sparse attempts、candidate yield、accepted yield、rejection reasons、模型成本和耗时。
- 至少覆盖 small sparse、medium decision-rich、docs-heavy 三类仓库。
- 比较模型或 prompt 版本时使用相同 seed/pool，避免伪趋势。

验收：

- readiness history 可查看最近 N 次 sparse conversion movement。
- 至少三种 repository profile 有真实 evidence。
- zero-candidate 和 provider failure 保持可见。

难度：中高，预计 1-2 个 changes。

### P3：真实外部客户主机闭环

建议 change：`complete-real-customer-host-trial`

目标：

- 在非本人机器、独立 VM 或试用客户服务器部署离线自托管包。
- 完成安装、首次登录、管理员建账号、公共/私有仓库导入、审阅、Why、Drift、备份恢复。
- 使用 sanitized host input 替换 template/placeholder evidence。
- 形成 operator runbook 的实际耗时、失败点和恢复记录。

验收：

- `real-external-host-trial-evidence` host proof 不再是 `template_or_placeholder`。
- 关键 lanes 无 blocking；operator-guided 项有责任人和操作记录。
- 不把本机 Docker smoke 当成客户 proof。

难度：高，主要依赖真实外部环境。

### P4：Pilot 团队产品化

建议 changes：

- `harden-private-repo-installation-flow`
- `improve-team-review-notifications`
- `productize-backup-upgrade-rollback`
- `pilot-feedback-evidence-loop`

目标：

- 管理员粘贴 token 或绑定 GitHub App 后可清晰诊断权限。
- reviewer/viewer 分工、审计、通知和 workspace scope 可用于 3-10 人团队。
- 升级失败可恢复，数据保留有可验证记录。
- pilot 反馈直接进入 OpenSpec 与 readiness evidence，而非散落在聊天或手工笔记。

难度：高，建议按真实客户阻塞顺序逐刀推进。

## 暂缓项目

在至少 2-3 个真实 self-hosted pilot 稳定使用前，继续暂缓：

- billing
- Marketplace
- hosted SaaS 多租户
- 自助 OAuth
- 大规模组织层级
- 永久买断授权系统

## 每个 change 的统一完成标准

- proposal/design/spec/tasks 完整且 strict valid。
- CodeGraph 影响分析先于实现。
- focused tests + package regression + strict validation。
- 涉及 UI 必须 Chrome/Browser 人工路径验证。
- 涉及仓库必须使用未复用的真实 GitHub repo 或明确说明 reuse。
- 涉及模型必须记录 provider mode、model、screen/extraction counts，不记录 key 或 raw private source。
- evidence 必须保留 warning/blocking/operator-guided/not-provided。
- 更新日志、任务书、readiness history、OpenSpec archive 和 scoped git commit。

## 已完成的 P0：治理 finding 精度与去重

deduplicate-governance-drift-findings 已完成：

- repeated issue 从 28 降为 3，减少 89.3%。
- 修复 issue 子串、普通策略说明、否定结果和弱重合误报。
- 等价 finding 使用 occurrence/source counts 合并，保留不同语义 finding。
- engine 383、web 83、OpenSpec 86/86 全绿。
- Chrome + DOM-CUA 真实 workspace 验证通过。

## 下一刀

立即执行 improve-imported-candidate-precision-ranking。当前 pip-tools 的 28 条 candidates 全部经过 parser salvage，首屏置信度偏低；下一阶段应先做 grounded/confidence/family/salvage 排序和近重复聚类，再考虑扩大模型或仓库规模。

完成该 change 后按顺序推进：

1. benchmark-sparse-conversion-trends。
2. complete-real-customer-host-trial。
3. 根据首批 2-3 个 self-hosted pilot 的真实阻塞选择 private repo、通知或升级回滚深化。