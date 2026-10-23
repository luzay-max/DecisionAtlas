# DecisionAtlas 历史计划归档索引（复核至 2026-10-23）

> 状态：**历史计划索引 / 当前维护**。
> 本次按照 `main@9bc32ce739db0bebeaeb928c6fc979dca34fe005` 的现有实现、OpenSpec 历史归档、Release Notes 和现行验收门槛整理；不把未合并 PR 当作已交付。
>
> **采用逻辑归档**：将已完成阶段明确标为 `ARCHIVED · phase-delivered`，**保留原文件路径和完整历史正文**，避免 README、OpenSpec、更新日志中的旧链接失效。物理移动和更改原版措辞不是这次操作；旧计划也不再作为当前工作指令。历史计划中写“complete”只反映当时的代码阶段，不代表客户环境、真实 LLM 提取或安全交付已验证。

## 一、已实现的阶段计划：归档完成

| 原计划（仍保留原路径） | 本次归档分类 | 已有实现依据 | 明确不包含的验收 |
| --- | --- | --- | --- |
| [2026-03-18 MVP 实施计划](../2026-03-18-decisionatlas-implementation-plan.md) | **ARCHIVED · MVP 核心代码阶段完成** | [项目 README](../../../README.md)、`apps/web/`、`apps/api/`、`services/engine/`，已有 Github import / decisions / review / why / drift 端点与测试 | 不声称 983 行计划每个原始任务逐项重新验收；不涵盖真实客户试点与生产运营 |
| [2026-03-18 v0.2 实施计划](../2026-03-18-decisionatlas-v0.2-implementation-plan.md) | **ARCHIVED · v0.2 功能基线实现** | [v0.2 Release Notes](../../project/release-notes-v0.2.md)、[v0.2.2 Release Notes](../../project/release-notes-v0.2.2.md)、导入 Job / full / incremental、runtime provider、demo 页面与部署文档 | 不等于所有第三方模型效果合格或 hosted/私有部署验收完成 |
| [2026-05-06 阶段 7：AI Agent Governance Integration](../2026-05-06-decisionatlas-stage-7-ai-agent-governance-integration-plan.md) | **ARCHIVED · 原定 Agent Guardrail / Runbook 阶段完成** | [Guardrail 使用说明](../../project/governance-agent-guardrail.md)、`services/engine/app/governance/agent_guardrail.py`、`scripts/governance/agent_guardrail.py` 与治理测试 | **不是标准 MCP Server 已交付**，也不代表 Claude/Codex 等真实 Agent Host 工作流已验收 |

### 完成计划的解读规则

1. `ARCHIVED` 表示该**明确阶段的主要代码能力已存在于当前 main**；不代表原文中全部扩展构想、环境依赖和非功能目标都通过了最新验证。
2. OpenSpec 自身的已完成 change 仍保留在 `openspec/changes/archive/`；不重复搬迁、不修改历史验收记录。
3. 发现旧计划中仍未交付的独立事项时，应在**当前计划 / 新 PR** 中登记，不能重新把整个已关闭 MVP/v0.2/Stage-7 阶段标为“进行中”。
4. 若验证发现实际能力并不存在，先引用代码/CI 证据更正该条归档分类，不凭文档标题和旧版完成率下结论。

## 二、历史或已被后续路线取代，但**不标记为全部完成**

以下文件保留在 `docs/plans/` 的原路径，仍可作为背景资料；它们包含未完成里程碑、研究建议、客户/运营门槛或跨阶段范围，**不因为发布时间早就算完成**。

| 历史计划 | 当前分类 / 保留理由 |
| --- | --- |
| [2026-03-18 v0.1 项目蓝图](../2026-03-18-decisionatlas-project-blueprint.md) | **架构历史基线**；设计文档，非可整体打勾的实施清单，README 仍引用 |
| [2026-03-18 v0.3 Backlog](../2026-03-18-decisionatlas-v0.3-backlog.md) | **部分落地**；GitHub/权限等有实现，GitLab/Gitee 完整导入仍属未合并 Draft |
| [2026-03-20 分支与真实数据探索](../2026-03-20-branching-and-live-data-exploration.md) | **已被后续计划取代的研究记录**；原文明确为 `Explore`，不是交付证明 |
| [2026-03-23 Post-v0.2 Next Steps](../2026-03-23-post-v0.2-next-steps.md) | **历史阶段路线**；部分后续特性已有实现，不能用来证明真实宿主/客户验证 |
| [2026-04-22 季度路线](../2026-04-22-decisionatlas-quarterly-roadmap.md) | **历史路线**；包含真实仓库价值、发布和 hosted 相关条件，不能整份判定完成 |
| [2026-04-24 后续开发计划](../2026-04-24-decisionatlas-next-development-plan.md) | **大部分代码阶段已推进**；真实质量与 hosted 外部验收仍有边界 |
| [2026-04-27 v0.3 后续路线](../2026-04-27-decisionatlas-v0-3-next-roadmap.md) | **v0.3 RC 基础已交付**；实际生产凭据、外部 hosted 试点与完整环境核验不能顺带打勾 |
| [2026-04-29 下一阶段总计划](../2026-04-29-decisionatlas-next-master-plan.md) | **多阶段历史路线**；前期 Governance Stage-7 已实现，后续扩展/真实验证另行评估 |
| [2026-05-06 Post-Stage-7 Master Plan](../2026-05-06-decisionatlas-post-stage-7-master-plan.md) | **历史迭代路线**；Stage-8+ 的工作流与质量验收不能仅由 Stage-7 代码推断 |
| [2026-05-08 完成路线图](../2026-05-08-decisionatlas-completion-roadmap.md) | **历史优化清单 / 部分落地**；真实仓库、客户交付和治理质量门槛未宣称完成 |
| [2026-05-08 Post-Stage-7 Master Plan](../2026-05-08-decisionatlas-post-stage-7-master-plan.md) | **历史优化建议**；可靠性与独立人类价值评价仍需证据 |
| [2026-05-09 商业化与产品化计划](../2026-05-09-decisionatlas-commercialization-productization-plan.md) | **部分交付**；产品包/商业材料存在，但试点客户、定价与真实签约不能称已实现 |
| [2026-05-20 Team Self-hosted 计划](../2026-05-20-decisionatlas-team-self-hosted-development-plan.md) | **基础代码落地 / 外部验收未完**；团队账号与 workspace 权限已实现，GitLab/Gitee 导入以及公司部署仍有限制 |
| [2026-06-09 Self-hosted 商业化路线](../2026-06-09-decisionatlas-post-self-hosted-commercialization-roadmap.md) | **部分交付 / 后续运营路线**；干净安装、私有试点与灾备的真实客户证据仍需补齐 |
| [2026-06-10 最终后续商业化路线](../2026-06-10-decisionatlas-final-post-commercialization-roadmap.md) | **被现行安全与真实价值计划取代的战略资料**；外部试点、灾备和 UI 等仍开放 |

## 三、当前进行中 / 待审核：严禁误归档为完成

- **唯一现行安全及价值验收主线**：[2026-10-21 安全收口与真实仓库价值验证](../2026-10-21-security-hardening-and-real-repo-validation-plan.md)。其中真正的非作者人类审核、Why/Drift 样本分、客户私有环境许可等仍存在未完成门槛。
- **证据质量改进提案**：[PR #11](https://github.com/luzay-max/DecisionAtlas/pull/11)（计划评审中，未合并）。
- **README 精修**：[PR #13](https://github.com/luzay-max/DecisionAtlas/pull/13)（评审中，未合并）。
- **跨项目 MCP 总体计划**：[PR #14](https://github.com/luzay-max/DecisionAtlas/pull/14)（Draft、未合并）。
- **GitLab/Gitee 连接器及公开导入集成**：[PR #15](https://github.com/luzay-max/DecisionAtlas/pull/15)、[PR #16](https://github.com/luzay-max/DecisionAtlas/pull/16)（Draft、未合并，#16 依赖 #15）。
- **MCP 只读 Spike**：[PR #17](https://github.com/luzay-max/DecisionAtlas/pull/17)（Draft、未合并，维护者已要求暂时搁置；本次不做任何修改或联调）。

参考真实数据证据：[pallets/click 公共导入试点](../../validation/2026-10-21-pallets-click-value-pilot.md) 和 [8 条 FakeProvider 候选独立核查](../../validation/2026-10-21-pallets-click-eight-candidate-independent-audit.md)（**0 接受 / 7 拒绝 / 1 不确定**，不是独立人类金标准，也不是实际 LLM 质量分）。

## 四、维护约定

- 每个归档项保留最小追踪元信息：阶段范围、当前代码/报告依据、尚未覆盖的验收及复核日期。
- 不从原计划里删除尚未完成的条目，也不从历史中移除当时的警告、`not_run`、`operator_guided` 等状态。
- 新的阶段计划只有在**已合入 main、范围实现、必要 CI 与人工验收符合该阶段定义**后才能移入“已实现”表。
- 本次是纯文档归档，不修改生产代码、不改变 PR #11/#13–#17 状态、不更改版本发布宣称，也不合并。
