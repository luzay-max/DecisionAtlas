# DecisionAtlas 最终后续开发计划：自托管商业化闭环后的路线

日期：2026-06-10  
当前基线：`46cabd9 feat: add commercial sales enablement kit`  
状态：OpenSpec active changes 为 0；最近主线 CI 已通过；OpenSpec strict 当前为 `60 passed, 0 failed`。

## 1. 当前判断

DecisionAtlas 已经完成从“功能型个人/研发工具”到“小团队自托管决策治理产品”的第一轮商业化闭环。

现在已经不是“还缺一个大功能”的阶段，而是进入：

```text
可部署
  -> 可验证
  -> 可解释
  -> 可交付
  -> 可销售试点
  -> 可迭代续费
```

当前最重要的判断是：短期继续强化 self-hosted / 私有部署路线，不转向完整 SaaS。

## 2. 已完成的主线能力

### 2.1 5.8 优化计划完成情况

| 计划主线 | 当前状态 | 证据 |
| --- | --- | --- |
| 固化开发协议 | 已形成默认治理开发协议、guardrail、release evidence 入口 | `default-governance-development-protocol`、`release-evidence-automation`、`docs/project/release-checklist.md` |
| 提升知识质量 | 已具备 rule lifecycle、stale/superseded、source evidence 标准化基础 | `add-governance-rule-lifecycle-review`、`governance-markdown-ingest` specs |
| 固化真实验证 | 已有固定真实仓库池、coverage rehearsal、随机真实仓库验证路径 | `real-repo-benchmark-trend-pool`、`real-repo-benchmark-coverage-rehearsal` |
| 收敛对外交付 | 已有 hosted readiness、self-hosted package、clean install、handoff、audit report、sales kit | 2026-05-08 至 2026-06-10 archived changes |

### 2.2 5.9 商业化计划完成情况

| 商业化任务 | 当前状态 | 证据 |
| --- | --- | --- |
| Community / Team / Enterprise 边界 | 已完成 | `self-hosted-commercial-baseline.md`、license/support boundary |
| 离线自托管包 | 已完成 | `build_self_hosted_package.py`、package verifier |
| 干净安装演练 | 已完成 | `clean-self-hosted-install-rehearsal` |
| 团队账号与 workspace 权限 | 已完成基础闭环 | `team-account-workspace-permissions`、相关 web/API tests |
| 试点客户交付包 | 已完成 | `pilot-customer-delivery-kit` |
| Code Decision Audit 报告 | 已完成 | `collect_code_decision_audit_report.py` |
| 销售页 / 一页简介 / 3 个用例 | 已完成 | `commercial-sales-enablement-kit` |
| 随机真实仓库验证 | 已纳入验证习惯 | 最新随机仓库 `encode/httpx`，benchmark ready |

## 3. 当前真实证据

最近可复核证据包括：

- OpenSpec strict：`60 passed, 0 failed`
- GitHub Actions：`27249062656` passed
- Real stack browser smoke：home / review / drift 真实 Chromium 检查 passed
- Commercial sales material Chromium review：passed
- 随机真实 GitHub 仓库：`encode/httpx`
- `encode/httpx` public import rehearsal：`reused`，`benchmark_ready=true`
- `encode/httpx` live benchmark：`passed=True`，`review_ready`
- Package verification：pass
- Pilot kit verification：pass
- Code Decision Audit report generation：warning-preserving, customer-readable

这些证据说明项目已经能进行“可信试点”，但还没有达到“规模化自助销售”。

## 4. 剩余关键缺口

### 缺口 1：非本人机器的安装证据还不够强

已经有 clean install rehearsal，但仍主要在当前开发环境/本机路径中验证。下一阶段需要在更接近客户环境的机器或干净 VM 中重复跑。

### 缺口 2：私有仓库真实试点还没有形成可公开记录

public repo 验证已经比较强，但商业价值更依赖 private repo。当前不能把客户私有内容提交进仓库，因此需要建立脱敏证据模板和 operator-local evidence 流程。

### 缺口 3：付费试点流程还缺合同/报价/支持边界模板

功能边界和销售材料已经有，但正式报价仍需要：

- 试点报价模板
- 年费授权条款草稿
- 支持响应边界
- 续费/升级路径
- 客户验收 checklist

### 缺口 4：备份、恢复、升级仍需要实战证据

runbook 已经存在，但真正的客户信任来自演练：

- 数据库备份
- 恢复到新环境
- 版本升级
- 失败回滚
- evidence 对比

### 缺口 5：UI 还偏工程工具，不是完整商业产品

核心流程可用，但面向客户演示还需要：

- 首次启动引导
- 管理员 onboarding
- 样例 workspace 一键进入
- evidence/report 入口更集中
- 错误状态更少依赖日志解释

## 5. 后续开发路线

### P1：外部环境安装复测

目标：证明非开发者环境可以跑起来。

范围：

- 在干净 Windows 用户目录、干净 VM、或另一台机器运行 self-hosted package。
- 从 `.env`、Docker、migrations、seed、admin 初始化到 Web 页面检查。
- 生成 package verification、clean install rehearsal、release evidence、team handoff、Code Decision Audit。
- 用浏览器截图记录 home / review / drift / governance / evidence 页面。

验收标准：

- 外部环境能启动 Web/API/Engine。
- 至少一个 public repo 能完成 import 或明确 operator-guided。
- 能生成完整 evidence 包。
- 阻塞项被记录到 update log，不口头记忆。

难度：中等。主要风险是环境差异、Docker、端口、Windows 权限。

### P2：私有仓库脱敏试点流程

目标：让 Team Self-hosted 的核心价值被真实 private repo 验证。

范围：

- 定义 private repo evidence 的脱敏模板。
- 记录 token 粘贴、访问验证、导入、review、why-search、drift 的 operator-local 流程。
- 生成不含代码内容、不含 token、不含客户敏感信息的 summary evidence。
- 把 Code Decision Audit 报告中的 private repo 边界写清楚。

验收标准：

- 至少一个 private repo 在本地/客户控制环境跑通。
- 可提交的证据只包含状态、计数、路径类别、截图裁剪或脱敏摘要。
- 不泄露 token、源码、私有 issue/PR 原文。

难度：中等偏高。风险是敏感信息边界和客户环境不可控。

### P3：备份、恢复、升级演练

目标：让客户敢长期使用和升级。

范围：

- PostgreSQL 备份脚本/文档演练。
- Redis 状态边界说明。
- `.env` / entitlement custody checklist。
- 从备份恢复到新目录或新数据库。
- 升级前后运行 readiness evidence 对比。
- 失败回滚模板。

验收标准：

- 可以从备份恢复关键 workspace。
- 升级失败时能回滚并说明证据状态。
- handoff report 能引用备份/恢复/升级 evidence。

难度：中等偏高。风险是数据一致性和迁移兼容性。

### P4：客户试点成交材料

目标：从“能展示”走到“能报价”。

范围：

- Code Decision Audit 服务报价模板。
- Team Self-hosted 年费报价模板。
- Enterprise Self-hosted 部署服务报价模板。
- 支持范围和响应时间说明。
- 试点验收 checklist。
- 续费/升级建议模板。

验收标准：

- 可以给第一个客户发出完整试点 proposal。
- 客户能理解交付物、价格、边界、风险和下一步。
- 仍不承诺 billing、SaaS、多租户、Marketplace、自助 OAuth。

难度：低到中等。难点不在代码，而在边界表达和避免过度承诺。

### P5：产品 UI 演示路径打磨

目标：降低试点演示成本。

范围：

- 首次进入页面展示部署/管理员/导入下一步。
- Dashboard 聚合 review、why-search、drift、evidence、handoff 的入口。
- 报告生成入口从脚本逐步收敛为 operator-readable guide 或 UI action。
- 错误状态增加可执行恢复建议。

验收标准：

- 10 分钟 demo 不依赖开发者解释目录结构。
- 新用户知道下一步点哪里。
- 错误状态能直接指向 operator action。

难度：中等。风险是 UI 工作容易扩散，必须围绕 demo/pilot 路径做。

### P6：长期趋势与发布证据自动化深化

目标：把真实仓库验证和 evidence 变成持续信号。

范围：

- 固定池 + 随机池并行。
- 每次 release 记录 import/readiness/benchmark/drift 趋势。
- 对比上一次 release 的变化。
- 将趋势摘要自动进入 release evidence / handoff / audit report。

验收标准：

- 每次 release 能回答：质量变好、变差、还是数据不足。
- 随机真实仓库验证不再只是一次性日志。
- 非 clean 状态不会被包装成 pass。

难度：中等。风险是指标噪声和 provider/network 不稳定。

## 6. 推荐下一刀

建议下一个 OpenSpec change：

```text
private-repo-pilot-evidence-template
```

原因：

- public repo、package、sales material 已经相对完整。
- 商业价值最关键的证明是 private repo。
- 但 private repo 不能直接提交原始证据，所以必须先把脱敏 evidence 模板和边界设计好。

最小范围：

- 新增 private repo pilot evidence template。
- 增加 verifier，检查是否包含 token/source redaction 声明。
- 用 operator-guided 示例生成 JSON/Markdown。
- 浏览器打开示例报告确认可读。
- 不接入 billing，不接入 SaaS，不接入 hosted secret vault。

## 7. 明确后置项

以下继续后置，不进入下一阶段主线：

- SaaS billing
- hosted multi-tenancy
- Marketplace / self-service OAuth
- hosted secret vault
- online license server
- runtime license enforcement
- enterprise SSO
- connector marketplace
- 完整 GitLab 替代品方向

这些不是永远不做，而是必须等 self-hosted 试点成交和真实客户反馈证明需求后再做。

## 8. 成功标准

未来 4-8 周的成功标准：

- 至少 1 次非本人环境 self-hosted 安装复测。
- 至少 1 个 private repo 脱敏试点证据包。
- 至少 1 份可发送给客户的报价/试点 proposal。
- 每次重要变更继续走 OpenSpec propose/apply/archive。
- 每次重要变更继续保留 pytest / OpenSpec / browser / real repo evidence。
- update log 记录所有关键测试和阻塞。
- 不把 warning/operator_guided/not_provided 说成 pass。

## 9. 总结

DecisionAtlas 当前不需要重新定义产品方向。正确路线仍然是：

```text
自托管决策治理产品
  + Code Decision Audit 服务切入
  + Team Self-hosted 年费
  + Enterprise 私有部署支持
  + 未来视客户需求再考虑 hosted managed service
```

下一阶段不是做更多“大平台功能”，而是拿真实环境、真实私有仓库、真实报价材料验证是否有人愿意为这个结果付费。
