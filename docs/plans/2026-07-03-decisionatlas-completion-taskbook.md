# DecisionAtlas 完整链路完成度任务书

日期：2026-07-03  
定位：把 2026-05-08 / 2026-05-09 总计划转成当前可执行、可验收、可继续迭代的任务书。  
原则：所有实现继续走 OpenSpec；所有完成状态必须有测试、归档、浏览器演练、真实仓库证据或交付证据支撑。

## 状态定义

- `complete`：已有代码/文档/证据实现，并通过对应测试或 OpenSpec 严格校验。
- `partial`：已有实现，但证据范围不足，例如只覆盖本地、mock、operator-guided、非客户机器、或缺少真实仓库趋势。
- `missing`：计划中需要，但当前没有足够实现或验证。
- `not-now`：明确延期，不作为近期完整 self-hosted 产品前置条件。

## 当前总判断

DecisionAtlas 已经具备“可运行、可演示、可生成治理证据、可自托管交付准备”的主体能力，但距离“完整链路产品”仍有三类缺口：

- 真实仓库闭环还需要更强的持续趋势和多仓库诊断证据。
- 用户侧任务书、发布侧证据、商业侧材料已经存在，但还需要统一成稳定的 release rehearsal 入口。
- self-hosted 交付已可验证，但外部非本人机器/客户控制环境仍应继续积累证据。

## 完成度矩阵

| 主线 | 当前状态 | 已有证据 | 仍缺什么 | 下一步 OpenSpec |
|---|---|---|---|---|
| OpenSpec 开发流程 | complete | 多个 archived changes；`openspec validate --all --strict` 最近通过 71 项 | 每次后续迭代继续维护任务书 | 每个新功能独立 change |
| CodeGraph 辅助开发 | partial | 已在实现前用于前端流程和结构定位 | 不是所有历史 change 都有 CodeGraph 记录 | 后续结构性代码任务继续强制先查 CodeGraph |
| 真实浏览器人类流程 | complete | `2026-07-03-real-browser-workflow-rehearsal`；Playwright 1 passed；Mimo/team browser 9 passed | 还不是 live GitHub import 成功证明 | `live-public-repo-browser-import-rehearsal` |
| 真实 GitHub repo 验证 | partial | real repo benchmark、public GitHub import rehearsal、browser 中使用 `openai/openai-cookbook` 引用、`pallets/flask` imported browser rehearsal、`multi-repo-live-diagnosis-rotation` 多仓库轮换诊断、full-chain 随机仓库演练（`n8n`、`rich`） | 随机真实仓库仍有 warning，需要持续积累多轮趋势和改进导入质量 | 真实试用/下一次 release 继续归档 |
| 核心闭环：导入 -> 审核 -> why -> drift -> guardrail | partial | demo/browser flow、benchmark、guardrail、drift specs、`imported-workspace-core-loop-rehearsal` collector/browser evidence、multi-repo diagnosis JSON/Markdown、full-chain release rehearsal | 部分真实仓库仍可能是 warning/evidence_limited，需要后续用真实试用反馈降噪 | 真实试用后按问题开 change |
| 治理知识质量 | complete | rule lifecycle、stale/superseded、source evidence、guardrail specs | 后续可继续降噪，但近期主能力已覆盖 | 后续按问题开小 change |
| readiness evidence history | complete | release/hosted/benchmark/external install/customer-host v2/full-chain/continuity/handoff/audit 证据归档、one-command release rehearsal 归档 | 需要每次 release 都跑一次 rehearsal 并观察趋势 | 按 release 节奏持续运行 |
| self-hosted 包和商业边界 | complete | package baseline、license/support boundary、commercial sales kit、handoff/audit docs、customer-host v2 rehearsal 管线 | 真实客户机器模板仍需由外部环境填写 | 客户试用时归档真实模板 |
| 备份/恢复/升级 | complete | backup/restore/upgrade rehearsal、real scratch rehearsal | 还没有真实生产数据迁移承诺；应保持边界 | 后续按客户需求扩展 |
| 团队账号和权限 | complete | team self-hosted rehearsal、browser role checks、workspace member specs、review audit UX panel、viewer read-only browser rehearsal | 后续只有客户需要时再扩展更复杂组织管理 | 按客户反馈开新 change |
| 登录/主账号/子账号路线 | partial | login、team account、role separation、workspace member assignment、review read-only boundary | 还不是完整 GitLab 式组织管理平台；近期够 self-hosted 小团队 | 客户反馈后再开组织管理 change |
| 发布证据和客户报告 | complete | release evidence、Code Decision Audit、team handoff、readiness history、`release-rehearsal-one-command-evidence`、review audit UX hardening、customer-host v2 evidence、full-chain random repo release evidence | 后续需要把 warning lane 逐步降噪，并用真实外部主机替换示例模板 | 客户试用时持续归档 |
| Docker / 本地一键启动 | partial | `start-real-stack.bat/.ps1`、clean install rehearsal、package verifier、customer-host v2 template/evidence | 还需更多外部机器和失败恢复证据；当前 smoke 仍是示例模板 + 本机证据 | 客户试用时持续归档 |
| 商业化/产品化计划 | complete | 2026-05-09 商业化计划、sales enablement kit、proposal kit | 后续按客户反馈更新价格/交付包 | 客户反馈后再开 change |
| 后续产品路线 | complete | `docs/plans/2026-07-03-decisionatlas-post-full-chain-product-roadmap.md` | 路线执行仍依赖真实外部试用证据 | `real-external-host-trial-evidence` |
| SaaS billing / Marketplace / 多租户 | not-now | 计划明确暂缓 | 不作为近期完整 self-hosted 产品要求 | 暂不做 |

## 当前最重要的下一批任务

### P0：真实仓库核心闭环加强

建议 change：`imported-workspace-core-loop-rehearsal`

目标：

- 选择至少一个真实 public GitHub repo。
- 证明从导入/复用 workspace 到 review、why-search、drift、guardrail 的链路可解释。
- 区分 live 成功、mock、operator-guided、provider failure。
- 输出 JSON/Markdown 证据，并能进入 readiness history。

验收证据：

- 后端或 CLI rehearsal 测试通过。
- 至少一个真实 public repo 运行证据。
- 浏览器或 Playwright 能打开对应 workspace 并走 review/search/drift。
- OpenSpec 全量通过。

### P1：多仓库轮换诊断（本轮完成）

建议 change：`multi-repo-live-diagnosis-rotation`

目标：

- 固定或随机选择多个 public GitHub repo。
- 记录 import setup、dashboard、review、why-search、drift、guardrail 状态。
- 允许 provider/network/local-stack 失败被分类，不把失败伪装成产品通过。
- 输出客户可读 JSON/Markdown，用于 release rehearsal 和 readiness history。

验收证据：

- `scripts/ci/collect_multi_repo_live_diagnosis.py`。
- `services/engine/tests/ci/test_multi_repo_live_diagnosis.py`。
- `.tmp/multi-repo-live-diagnosis.json/md` smoke evidence。
- `docs/project/multi-repo-live-diagnosis-rotation.md`。

### P2：一键 release rehearsal 汇总入口（本轮完成）

建议 change：`release-rehearsal-one-command-evidence`

目标：

- 把 guardrail、release evidence、hosted readiness、benchmark comparison、external install、continuity、handoff、audit、browser rehearsal 收进一个 operator 命令。
- 输出 `.tmp` 证据和可归档 readiness history。
- 支持默认发现已有证据、显式路径输入、可选 live multi-repo diagnosis。
- 保留 warning/operator-guided/not-provided，不伪装成 clean pass。

验收证据：

- `scripts/ci/collect_release_rehearsal_evidence.py`。
- `services/engine/tests/ci/test_release_rehearsal_evidence.py`。
- `.tmp/release-rehearsal-evidence.json/md` smoke evidence。
- `docs/evidence/readiness/*release-rehearsal-one-command/` durable archive。

### P3：审阅与审计 UX 加固（本轮完成）

change：`review-audit-ux-hardening`

目标：

- 让 reviewer/viewer/admin 的能力差异在 UI 中更清晰。
- 审阅记录、权限边界、下一步动作更接近小团队协作产品。

验收证据：

- `ReviewAuditPanel` 显示角色、权限边界、近期审阅上下文和空状态下一步。
- `apps/web/tests/review-audit-panel.test.tsx` 覆盖 reviewer/viewer/empty state。
- `apps/web/tests-e2e/team-self-hosted-rehearsal.spec.ts` 覆盖 viewer workspace 成员进入 review 后只读。
- 后端权限允许 viewer 读取候选队列，但继续禁止 viewer 提交 review mutation。

### P4：外部客户主机演练 v2（本轮完成）

change：`external-customer-host-rehearsal-v2`

目标：

- 继续强化非本人机器、自托管包、Docker、本地启动、恢复路径证据。
- 生成客户可读 install evidence。

验收证据：

- `scripts/ci/collect_external_customer_host_rehearsal_v2.py`。
- `templates/external-customer-host-rehearsal-v2.example.json`。
- `.tmp/external-customer-host-rehearsal-v2.json/md`。
- `docs/evidence/readiness/2026-07-03-external-customer-host-rehearsal-v2-smoke/`。
- `services/engine/tests/ci/test_external_customer_host_rehearsal_v2.py` 与 readiness history 测试。
- `team-self-hosted-rehearsal.spec.ts` 浏览器流程通过。

边界：

- 当前 smoke 使用示例模板和本机已有证据，证明 v2 证据管线可用。
- 真实客户控制机器 proof 仍需要客户/外部环境填写模板并再次归档。

### P5：完整链路随机真实仓库 release 演练（本轮完成）

change：`full-chain-random-repo-release-rehearsal`

目标：

- 把随机真实 GitHub repo、多仓库诊断、release rehearsal、customer-host v2、浏览器流程和 readiness history 汇成一个顶层证据。
- 保留 warning/operator-guided/non-pass 状态，不伪装为 clean pass。

验收证据：

- `scripts/ci/collect_full_chain_random_repo_release_rehearsal.py`。
- `.tmp/full-chain-random-repo-release-rehearsal.json/md`。
- `docs/evidence/readiness/2026-07-03-full-chain-random-repo-release-rehearsal-smoke/`。
- 随机真实仓库：`n8n-io/n8n`、`Textualize/rich`。
- 浏览器流程：`team-self-hosted-rehearsal.spec.ts` passed。
- pytest 覆盖 full-chain collector 和 readiness history。

边界：

- 当前 full-chain 状态是 `warning`，0 blocking。
- 这证明完整链路 evidence 入口可用，但真实仓库导入质量、release warning lane、customer-host template-only 仍需后续真实试用持续改进。

### P6：post-full-chain 后续产品路线（本轮完成）

change：`post-full-chain-product-roadmap`

目标：

- 把 full-chain 之后的项目推进路线写清楚。
- 明确当前 warning 边界和下一阶段真实外部试用优先级。
- 避免在没有客户证据前提前投入 billing、Marketplace、多租户、hosted SaaS。

验收证据：

- `docs/plans/2026-07-03-decisionatlas-post-full-chain-product-roadmap.md`。
- 下一批候选 OpenSpec：`real-external-host-trial-evidence`、`reduce-random-repo-import-warning-lanes`、`improve-real-repo-core-loop-quality`、`pilot-customer-trial-package`。

## 当前不应该优先做

- billing。
- Marketplace。
- 自助 OAuth。
- 完整 SaaS 多租户。
- hosted managed service 运维平台。
- 永久买断授权。

这些只有在 self-hosted 可销售闭环和真实客户反馈稳定后才进入新路线。

## 后续每刀完成标准

每个后续 change 必须满足：

- 有 OpenSpec proposal/design/spec/tasks。
- 有明确测试或 rehearsal 命令。
- 如果涉及 UI，至少有一个浏览器级验证。
- 如果涉及仓库导入或分析，优先使用真实 GitHub public repo，并标明 live/mock/operator-guided 边界。
- 更新 `docs/project/YYYY-MM-DD-update-log.md`。
- 归档 OpenSpec change。
- 提交 git。
- 必要时更新本任务书。

## 近期执行顺序

1. `review-audit-ux-hardening`
2. `external-customer-host-rehearsal-v2`

`review-audit-ux-hardening`、`external-customer-host-rehearsal-v2`、`full-chain-random-repo-release-rehearsal` 与 `post-full-chain-product-roadmap` 已完成。下一步不建议继续扩展大功能，建议进入真实外部试用准备：

- 用真实非本人机器替换示例 customer-host 模板并归档。
- 每次试用或 release 都跑一次 full-chain random repo release rehearsal。
- 根据真实客户试用反馈，再决定是否开组织管理、安装恢复、GitHub private repo UX 或商业材料深化 change。
