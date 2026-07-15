# DecisionAtlas 最新优化总计划

日期：2026-05-08  
当前基线：`bb5753a test: include governance guardrail in release gate`  
说明：本文件基于 OpenSpec 已归档 changes 和 git 历史重新整理，不再沿用之前的阶段式路线图。

## 结论

DecisionAtlas 已经从“搭建能力”进入“优化可靠性、可解释性和可交付性”的阶段。当前 OpenSpec active changes 为 0，说明主线能力已经收敛到已实现状态。接下来不该继续重复造功能，而应围绕四件事推进：

- 让开发协议稳定。
- 让治理知识更准。
- 让真实验证可量化。
- 让对外交付可复现。

## 已实现能力盘点

这些能力已经在 OpenSpec 归档和 git 历史中出现，不是规划项：

- `b6d324f` / `dc8e00c`：治理 diff checker 和 drift detection 已具备结构化信号能力。
- `4d49354` / `5024a8b` / `2026-05-07-integrate-governance-guardrail-into-agent-workflow`：AI agent governance guardrail 已接入工作流。
- `3cef8c7` / `2026-05-07-harden-governance-workflow-and-demo-reset`：demo reset、workflow hardening、可复现性基础已建立。
- `78fd14c` / `2026-05-07-improve-governance-knowledge-quality-loop`：知识质量循环已开始优化。
- `0d87fc3` / `2026-05-07-build-real-repository-value-benchmark`：真实仓库 benchmark 已可用于验证，不再只依赖 seed demo。
- `f5bcd0e` / `2026-05-08-prepare-governed-hosted-preview`：hosted preview 准备工作已完成。
- `41deedd` / `2026-05-08-prototype-governance-enforcement-preview`：enforcement preview 已有原型。
- `bb5753a`：guardrail interface 已纳入 canonical release gate。

## 当前短板

现在最缺的不是新功能，而是统一性和稳定性：

- 还没有把治理检查固化成默认开发协议。
- 规则、决策、证据的表达还不够标准化。
- 真实仓库 benchmark 需要稳定基线和趋势对比。
- hosted preview 还缺少完整 operator 运行手册和恢复路径。
- `continue / caution / pause` 的边界还需要再收紧，避免把 advisory 信号误当黑箱裁判。

## 后续优化主线

### 1. 固化开发协议

把治理检查变成日常开发习惯，而不是临时脚本。

- 统一 preflight / postflight 步骤。
- 定义 `continue / caution / pause` 的语义。
- 输出机器可读和人类可读两种治理摘要。
- 让 OpenSpec、任务、diff、drift、测试结果在同一视图里收口。

### 2. 提升知识质量

把治理文档变成更高质量的输入，而不是更多文本。

- 降低普通描述被误抽成规则的概率。
- 强化 decision / standard / postmortem / anti-pattern 的区分。
- 为 accepted rules 增加 source excerpt、rationale、stale 标记、superseded 标记。
- 优先减少噪声，再谈扩量。

### 3. 固化真实验证

让项目价值用固定数据集和回归指标说话。

- 固定一组真实仓库作为 benchmark。
- 记录 import success、artifact density、accepted decision quality、why-search 命中质量、drift signal 有效性。
- 每次核心改动都能比较“之前 / 之后”。
- 把 benchmark 从一次性演示变成回归门槛。

### 4. 收敛对外交付

把本地能力整理成可恢复、可讲清、可演示的版本。

- 统一 demo reset、启动、验证、恢复流程。
- 补齐 operator guide 和 release checklist。
- 维持 advisory-first，严格模式只做 opt-in。
- 明确边界：这是治理与决策辅助系统，近期产品化目标是 self-hosted / 私有部署可销售交付，不是完整 SaaS 平台。
- 补齐 Community / Team Self-hosted / Enterprise Self-hosted 的能力边界、license/support/limitation 说明和客户可读报告模板。

## 推荐执行顺序

1. 开发协议固化
2. 知识质量提升
3. 真实验证固化
4. 对外交付收敛

## 当前优先级

当前最值得先做的是“开发协议固化”。原因很直接：能力已经存在，但没有默认工作流，后续优化的收益会被手工步骤和状态漂移吃掉。

## 不做的事

短期不优先：

- 多租户 SaaS 化
- billing / Marketplace / 自助 OAuth
- 默认 CI 强阻断
- 大规模 connector 扩张
- 复杂权限平台
- 永久买断授权
- 重新造一套与 OpenSpec 重复的计划系统

## 成功标准

- 新的 AI-assisted 开发任务会自动带上治理上下文。
- 真实仓库 benchmark 可以稳定回归。
- drift / diff / guardrail 的输出一致、可解释、可复核。
- demo 可以重启、恢复、演示，不依赖记忆。
- self-hosted 部署可以按文档在非本人机器上跑通。
- 对外销售边界清楚：Community 免费试用、Team 年度授权、Enterprise 私有部署和支持。
- 后续计划是“优化主线”，不是重复上一轮阶段目标。

## 2026-07-15 实施校准

本计划中“收敛对外交付”和“固化真实验证”已经推进到本地隔离宿主试用阶段，但尚未完成客户控制主机证明：

- 已完成真实公共仓库导入、Chrome 核心页面链路、release evidence、hosted readiness、benchmark comparison 和 readiness history 的可重复输出。
- hosted URL、客户控制 VM、真实团队账号分工、私有仓库 token、外部恢复演练仍是未完成的交付条件。
- 因此下一阶段不是扩展 billing、多租户或 Marketplace，而是用独立 VM/测试服务器完成一次不带模板标记的 external customer-host proof。
- 新鲜仓库尚无 accepted baseline，Why/Drift 的 `review_required` 是预期保护行为；应先接受少量高质量决策，再测 warning reduction。
- live benchmark 仍存在 n8n 失败 profile，必须先定位原因再决定修复或阈值调整。
