# 2026-10-21 历史计划审查与逻辑归档索引

> 归档方法：**只读历史存档，保留原文件路径**，避免已有 README、OpenSpec 和更新日志的链接失效。本页不删除任何任务，不改写证据状态。

| 原计划 | 审查结论 | 档案状态与依据 |
| --- | --- | --- |
| [2026-03-18 初版蓝图](../2026-03-18-decisionatlas-project-blueprint.md)、[实施计划](../2026-03-18-decisionatlas-implementation-plan.md) | MVP 主体代码已交付，仍需持续维护 | Historical / phase-completed；参照 `README_zh-CN.md` 的核心能力和现有 apps/services 代码 |
| [2026-03-18 v0.2 实施计划](../2026-03-18-decisionatlas-v0.2-implementation-plan.md)、[2026-03-23 v0.2 后续](../2026-03-23-post-v0.2-next-steps.md) | 旧版本里程碑，不再作为当前执行清单 | Historical / superseded by v0.3 RC 与后续规划 |
| [2026-05-08 完成路线图](../2026-05-08-decisionatlas-completion-roadmap.md) | 部分范围已有 OpenSpec 归档及实现；外部客户验证未完成 | Historical / implementation mostly delivered, customer gates open |
| [2026-06-09 自托管商业化路线图](../2026-06-09-decisionatlas-post-self-hosted-commercialization-roadmap.md) | 自托管包、试点材料和团队权限有实现；非开发者/外部主机和私有试点仍缺证据 | Historical / partially completed |
| [2026-06-10 最终商业化后路线图](../2026-06-10-decisionatlas-final-post-commercialization-roadmap.md) | 当前战略基线仍有效；明确提出外部安装与真实 private repo 为未完成事项 | **Superseded as active task tracker**，继续保留为战略来源 |
| [2026-05-20 团队自托管开发计划](../2026-05-20-decisionatlas-team-self-hosted-development-plan.md) | 有团队权限代码与 E2E；客户部署仍需验证 | Historical / bounded implementation; external proof pending |

### 不归档成「全部完成」的事项
- Draft PR #1–#7 均不能算已合入 `main`；#4→#5→#6 还存在分支堆叠。
- 历史证据中的 `warning`、`operator_guided`、`not_provided` 必须原样保留。
- `docs/project/2026-06-18-update-log.md` 中备份/恢复/升级演练标注 `operator_guided` 且非真正数据库恢复，不能宣称已完成灾难恢复验收。
- 完整 SaaS、自助 GitHub OAuth、企业 SSO、客户私有仓库真实试点均未被历史报告证明。

### OpenSpec 归档处理
仓库 `openspec/changes/archive/` 已是历史 change 的官方存放位置；不重复移动，不重新标记已归档任务。后续若需要补正规变更 spec，应在新 change 下记录 delta，而不是修改已归档的历史结论。

**新的唯一活跃交付路线：** [2026-10-21 安全收口与价值验证计划](../2026-10-21-security-hardening-and-real-repo-validation-plan.md)。
