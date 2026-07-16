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
| OpenSpec 开发流程 | complete | 多个 archived changes；`openspec validate --all --strict` 最近通过 83 项 | 每次后续迭代继续维护任务书 | 每个新功能独立 change |
| CodeGraph 辅助开发 | partial | 已在实现前用于前端流程和结构定位 | 不是所有历史 change 都有 CodeGraph 记录 | 后续结构性代码任务继续强制先查 CodeGraph |
| 真实浏览器人类流程 | complete | `2026-07-03-real-browser-workflow-rehearsal`；Playwright 1 passed；Mimo/team browser 9 passed | 还不是 live GitHub import 成功证明 | `live-public-repo-browser-import-rehearsal` |
| 真实 GitHub repo 验证 | partial | real repo benchmark、public GitHub import rehearsal、browser 中使用 `openai/openai-cookbook` 引用、`pallets/flask` imported browser rehearsal、`multi-repo-live-diagnosis-rotation` 多仓库轮换诊断、full-chain 随机仓库演练（`n8n`、`rich`）、warning lane reduction 归因、real repo core-loop quality 降噪 | `rich` 已建立 1 条 accepted baseline 并完成真实 Chrome review/why/drift 验证；但该 workspace 是复用导入，baseline 仍为 thin，随机真实仓库仍有 warning | `fresh-random-public-repo-import-rehearsal` |
| 核心闭环：导入 -> 审核 -> why -> drift -> guardrail | partial | demo/browser flow、benchmark、guardrail、drift specs、`imported-workspace-core-loop-rehearsal` collector/browser evidence、multi-repo diagnosis JSON/Markdown、full-chain release rehearsal、action category counts | `rich` 精确 Why 查询和漂移重评已通过，但默认诊断仍有弱引用 warning；客户主机 proof 仍含 operator-guided 边界 | `fresh-random-public-repo-import-rehearsal` |
| 治理知识质量 | complete | rule lifecycle、stale/superseded、source evidence、guardrail specs | 后续可继续降噪，但近期主能力已覆盖 | 后续按问题开小 change |
| readiness evidence history | complete | release/hosted/benchmark/external install/customer-host v2/full-chain/continuity/handoff/audit 证据归档、one-command release rehearsal 归档 | 需要每次 release 都跑一次 rehearsal 并观察趋势 | 按 release 节奏持续运行 |
| self-hosted 包和商业边界 | complete | package baseline、license/support boundary、commercial sales kit、handoff/audit docs、customer-host v2 rehearsal 管线 | 真实客户机器模板仍需由外部环境填写 | 客户试用时归档真实模板 |
| 备份/恢复/升级 | complete | backup/restore/upgrade rehearsal、real scratch rehearsal | 还没有真实生产数据迁移承诺；应保持边界 | 后续按客户需求扩展 |
| 团队账号和权限 | complete | team self-hosted rehearsal、browser role checks、workspace member specs、review audit UX panel、viewer read-only browser rehearsal | 后续只有客户需要时再扩展更复杂组织管理 | 按客户反馈开新 change |
| 登录/主账号/子账号路线 | partial | login、team account、role separation、workspace member assignment、review read-only boundary | 还不是完整 GitLab 式组织管理平台；近期够 self-hosted 小团队 | 客户反馈后再开组织管理 change |
| 发布证据和客户报告 | complete | release evidence、Code Decision Audit、team handoff、readiness history、`release-rehearsal-one-command-evidence`、review audit UX hardening、customer-host v2 evidence、full-chain random repo release evidence、random repo warning lane reduction | 后续需要把 product-controlled warning lane 逐步降噪，并用真实外部主机替换示例模板 | 客户试用时持续归档 |
| Docker / 本地一键启动 | partial | `start-real-stack.bat/.ps1`、clean install rehearsal、package verifier、customer-host v2 template/evidence | 还需更多外部机器和失败恢复证据；当前 smoke 仍是示例模板 + 本机证据 | 客户试用时持续归档 |
| 商业化/产品化计划 | complete | 2026-05-09 商业化计划、sales enablement kit、proposal kit | 后续按客户反馈更新价格/交付包 | 客户反馈后再开 change |
| 后续产品路线 | complete | `docs/plans/2026-07-03-decisionatlas-post-full-chain-product-roadmap.md` | 路线执行仍依赖真实外部试用证据 | `pilot-customer-trial-package` |
| 真实外部主机试用证据门槛 | complete | `real-external-host-trial-evidence` collector、readiness history family、smoke archive | 当前 smoke 仍是示例模板 warning；真实客户/外部机器 proof 需要外部环境填写模板 | `pilot-customer-trial-package` |
| 试用客户交付包 | complete | `pilot-customer-trial-package` collector、`.tmp` bundle、pytest | 当前 bundle 是 warning；需要真实外部主机证据替换模板后再生成 | `improve-real-repo-core-loop-quality` |
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

### P7：真实外部主机试用证据门槛（本轮完成）

change：`real-external-host-trial-evidence`

目标：

- 防止示例模板、本机 smoke、placeholder 值被误认为真实客户控制主机 clean pass。
- 把 customer-host v2、full-chain random repo release、sanitized host input 汇总成一个更严格的 external trial gate。
- 支持 readiness history 归档和趋势对比。

验收证据：

- `scripts/ci/collect_real_external_host_trial_evidence.py`。
- `.tmp/real-external-host-trial-evidence.json/md`。
- `docs/evidence/readiness/2026-07-03-real-external-host-trial-evidence-smoke/`。
- `services/engine/tests/ci/test_real_external_host_trial_evidence.py` 与 readiness history 测试。
- 当前 smoke 状态：`warning`，host proof level：`template_or_placeholder`，0 blocking。

边界：

- 该 change 完成的是“真实外部主机证据验收门槛”，不是“真实客户机器已经 clean pass”。
- 下一次需要在非本人机器、客户 VM、朋友机器或独立服务器上填写 sanitized host input，再重新归档。

### P8：试用客户交付包（本轮完成）

change：`pilot-customer-trial-package`

目标：

- 把 pilot delivery kit、commercial proposal kit、real external host trial evidence、full-chain evidence 和 readiness history 汇总成一个 operator-facing 试用交付包。
- 输出 `.tmp` JSON/Markdown 和 bundle 目录，方便真实外部试用前检查材料和证据缺口。
- 保留 warning/operator-guided/not-provided，不伪装为 clean pass。

验收证据：

- `scripts/ci/collect_pilot_customer_trial_package.py`。
- `.tmp/pilot-customer-trial-package.json/md`。
- `.tmp/pilot-customer-trial-package/pilot-customer-trial-package/README.md`。
- `.tmp/pilot-customer-trial-package/pilot-customer-trial-package/operator-checklist.md`。
- `services/engine/tests/ci/test_pilot_customer_trial_package.py`。

边界：

- 当前 bundle 状态是 `warning`，0 blocking。
- 这证明试用包装配链路可用，但真实客户机器 proof 仍必须由真实外部环境替换模板证据。

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
3. `full-chain-random-repo-release-rehearsal`
4. `post-full-chain-product-roadmap`
5. `real-external-host-trial-evidence`
6. `pilot-customer-trial-package`
7. `reduce-random-repo-import-warning-lanes`
8. `improve-real-repo-core-loop-quality`
9. `improve-real-repo-why-drift-grounding`
10. `improve-real-repo-accepted-decision-baseline`
11. `review-candidates-into-accepted-baseline-flow`

上述 11 个 change 已完成，`rich` 已通过受控 review flow 从 0 条 accepted 提升到 1 条，并完成真实 Chrome Why/Drift 验证。下一步不建议继续扩展大功能，应优先证明全新随机公开仓库从零导入的完整链路，并推进真实外部试用：

- 用真实非本人机器替换示例 customer-host 模板，并通过 `real-external-host-trial-evidence` 归档。
- 每次试用或 release 都跑一次 full-chain random repo release rehearsal。
- 重新生成 `random-repo-warning-lane-reduction`，确认 `product_controlled` warning 继续下降。
- 新开 `fresh-random-public-repo-import-rehearsal`，随机选择未复用的公开 GitHub 仓库，从零完成 import -> review -> why -> drift -> guardrail -> release evidence。
- 重新生成 `pilot-customer-trial-package`，确认交付包 warning 来源可解释。
- 根据真实客户试用反馈，再决定是否开组织管理、安装恢复、GitHub private repo UX 或商业材料深化 change。

### P12：全新随机公开仓库从零导入演练（本轮完成）

change：`fresh-random-public-repo-import-rehearsal`

目标：

- 从候选池确定性随机选择当前 owner scope 中不存在 workspace 的公开 GitHub 仓库。
- 证明 no-workspace preflight -> created full import -> terminal success -> core loop -> browser -> release/readiness evidence。
- 修复公开仓库 stale token 401 回退和 GitHub 502/503/504 有界重试。
- 将 fresh import 作为 readiness history 一等证据族。

验收证据：

- 真实仓库 `python-trio/sniffio`，预检 `workspace_exists=false`。
- fresh import job 成功，导入 147 artifacts。
- Chrome 完成 dashboard、Review、Why Search、Drift 和返回 dashboard，0 console errors。
- `docs/evidence/readiness/2026-07-13-fresh-public-sniffio-import-rehearsal/`。
- 42 个相关 pytest 通过；OpenSpec strict 84/84 通过。

边界：

- 当前 repository 产生 0 candidates / 0 accepted decisions，所以 Why 和 Drift 保持 `evidence_limited`。
- readiness 为 `warning`、0 blockers；这证明可靠导入和诚实降级，不等于核心决策质量已达 clean pass。
- 下一刀优先优化 sparse real repo 的 decision conversion，再用新的未导入仓库做回归。

### P13：Sparse 真实仓库决策转换（本轮完成）

change：`improve-sparse-repo-decision-conversion`

目标：

- 在 normal extraction 为 0 candidate 时执行有界、family-diverse sparse recovery。
- 保持 grounded quote、source ref、confidence 和人工审阅边界。
- 把 sparse eligibility、attempt、rejection 和 recovered metrics 纳入 import、fresh rehearsal 与 readiness history。
- 使用真实模型、fresh repository、Chrome 和 DOM-CUA 验证。

验收证据：

- 完整 engine pytest 376 passed；OpenSpec strict 85/85。
- fresh `jazzband/pip-tools`：no-workspace preflight，1207 artifacts，80 screenings，49 extraction calls，28 candidates。
- normal candidate 存在时 sparse lane 为 `skipped/candidate_present`，0 extra calls。
- `python-trio/sniffio` supplemental reanalysis：sparse 4 model calls、4 null、0 fabricated candidate。
- 人工接受 1 条 pip-tools decision；Why pass / 2 citations；Drift clean / 0 alerts。
- `docs/evidence/readiness/2026-07-13-sparse-repo-decision-conversion-rehearsal/`。

边界与下一步：

- pip-tools candidates 全部经过 parser salvage，首屏候选置信度偏低，下一步需要 precision/ranking/duplicate reduction。
- dashboard 重复显示大量 `repeated_postmortem_issue`，下一刀优先做 governance finding 去重。
- 真实外部客户主机 clean proof 仍未完成。

### P14：治理漂移 Finding 精度与去重（本轮完成）

change：deduplicate-governance-drift-findings

目标：

- 在 detector 边界过滤普通文本、否定结果和弱重合误报。
- 对真正等价的 repeated issue 使用稳定语义键合并。
- 保留 occurrence/source counts、唯一 evidence 和 advisory 边界。
- 让 guardrail、dashboard、CLI 和 readiness evidence 共享 canonical signal。

验收证据：

- 当前真实工作树 repeated issue 从 28 降为 3，噪声下降 89.3%。
- 两份临时等价历史问题合并为 1 条 signal，occurrence 2、source 3。
- Chrome 显示 recurrence 标签，DOM-CUA 成功进入 Governance，console 0 error/warning。
- engine 383 passed；web 83 passed；OpenSpec strict 86/86。
- docs/evidence/readiness/2026-07-13-governance-drift-finding-deduplication/。

边界与下一步：

- 正常仓库的三条 finding 语义不同，保留人工审阅。
- 下一刀执行 improve-imported-candidate-precision-ranking，降低 pip-tools 低置信、salvaged 和近重复 candidate 的审阅成本。

### P15：公开仓库 CI Access Probe 稳定性（已完成）

change：harden-public-repo-ci-access-probe

触发证据：

- GitHub Actions run 29221547589：Node、typecheck、engine、benchmark 通过。
- browser smoke 11/12，通过项无回归。
- pallets/flask metadata 被共享 runner 错误折叠为 credential_required。

实现与本地验证：

- 使用匿名 Git smart-HTTP info/refs 作为 metadata 失败后的 bounded fallback。
- 区分 credential_required 与 network_failure。
- 聚焦测试 33 passed；engine full 388 passed。
- pallets/flask 真实 probe=true，本地导入已达到 1157 artifacts。
- 使用随机公开仓库 pallets/itsdangerous 完成真实 Playwright 核心链路。
- GitHub Actions run 29380845943 全绿，browser smoke 12/12 passed。
- 主规格已同步，change 已归档；下一刀执行 improve-imported-candidate-precision-ranking。

### P16：Imported Candidate Precision Ranking（已完成）

change：improve-imported-candidate-precision-ranking

已完成：

- 候选 metadata、evidence-first score/tier、稳定排序和近重复代表。
- imported review API、队列摘要、卡片解释和人工 review action 保持可用。
- pip-tools 与新鲜 pallets/markupsafe 的真实 API 排序证据。
- 真实浏览器核心链路 1 passed，engine 392、web 83、API 32、OpenSpec strict 88 全部通过。
- 最终实现提交 2f57d70 已推送；归档后的导航竞态修复提交 22de990、f0b2836 已推送；GitHub Actions run 29385331090 全绿，browser smoke 12/12。

边界：

- before/after 对比的 before 是从实时候选 payload 重建的旧 confidence 排序，不是历史数据库快照。
- 不自动 accept、reject、merge 或删除候选。
- change 已归档；归档后发现的导入完成 refresh 导航竞态已修复并通过最终 CI；下一刀进入 sparse conversion 多仓库趋势。

### P17：Sparse Conversion Multi-Profile Trend（进行中，待归档）

change：`benchmark-sparse-conversion-trends`

已完成：

- benchmark snapshot 升级为兼容 schema v2，新增 `sparse_conversion`：normal/sparse attempts、candidate/recovered yield、rejection reasons、耗时和 provider mode。
- 固定 trend pool 增加 `small_sparse`、`docs_heavy`、`medium_decision_rich`、`stress` profile 与 zero-candidate/sparse expectation；legacy snapshot 仍按 `not_provided` 读取。
- comparison、coverage rehearsal、release evidence、hosted readiness、readiness history 和 team handoff 均保留 sparse movement，不改变 required gate 语义。
- 聚焦证据测试 57 passed；engine 397 passed；API 32、Web 83；typecheck、benchmark fixture、OpenSpec strict 88/88 通过。
- 真实 live provider 为 `openai_compatible`，embedding 为 `fake`；四个 fresh public repo 均完成成功导入和 live benchmark：
  `drisspg/transformer_nuggets`（small_sparse，sparse exhausted）、
  `harbor-framework/terminal-bench-science`（docs_heavy，candidate_present）、
  `sirkirby/unifi-mcp`（medium_decision_rich，candidate_present）、
  `LiPu-jpg/Openwrite`（stress，no_eligible_evidence）。
- 本地真实栈浏览器核心链路 1 passed，覆盖 dashboard、review 条件、Why、Drift、Evidence 跳转；完整 JSON/Markdown 证据已保存到 `docs/evidence/readiness/2026-07-15-benchmark-sparse-conversion-trends/`。

边界：

- 四仓库当前是首次纳入比较，因此 movement 是 `newly-evaluated`，还没有同池历史 release baseline；下一次同池运行才会产生真正 improved/regressed 趋势。
- hosted URL 和 recovery drill 仍为 `operator_guided`；本次不是外部客户主机交付证明。
- stress 仓库导入成功但没有 eligible evidence，保留为 `evidence_limited`，不人为提升为通过。

下一步：

- 归档并推送本 change，查询对应 GitHub Actions。
- 之后进入 `complete-real-customer-host-trial`，在独立 VM/外部主机完成 hosted/operator 交付闭环。

### P18：真实客户宿主试用闭环（本轮完成，外部客户证明待补）

change：`complete-real-customer-host-trial`

本轮完成：

- 新增版本化 customer-host trial 输入契约、核心 lane、路径脱敏、source evidence 边界、operator checklist 和 self-hosted package 模板。
- 使用当前真实本地 Docker stack 执行完整 operator checklist，并随机选择新鲜公共仓库 `hynek/structlog`：全量导入 1,169 个对象，生成 26 个候选决策。
- 使用真实 Chrome 验证 Home、Team、Settings、Evidence、workspace Dashboard、Review、Why、Timeline、Drift 共 13 个页面/跳转；Why Search 实际调用后在无 accepted baseline 时返回 `review_required`、0 citations，保持 fail-closed。
- 生成 `.tmp/customer-host-trial-evidence.json/md`、release evidence、hosted readiness、benchmark comparison、continuity、team handoff，并归档到 `docs/evidence/readiness/2026-07-15-customer-host-trial-release-rehearsal/`。

验证结果：

- engine：399 passed；API：32 passed；Web：83 passed；typecheck 通过；benchmark fixture 通过；OpenSpec strict 通过。
- package verification 通过；clean install 和 real continuity rehearsal 为 warning/operator-guided，无 blocker。
- release evidence 为 `warning`，三个必需门禁通过；guardrail 为 `caution`，保留治理历史提醒。
- hosted readiness 为 `operator_guided`，因为本轮没有外部 hosted URL；不能把本地 Docker 结果称为客户主机证明。
- 固定 live benchmark profile 为 4/5 通过，n8n 1 个 profile 失败；该失败已保留在 live report，不能只报告通过项。
- OpenSpec change 已归档；实现提交 `76decc8` 已推送，GitHub Actions run `29391492181` 全绿，包含 Node、typecheck、engine、benchmark fixture 和 browser smoke。

未完成边界：

- 尚未在客户控制的独立 VM/服务器完成外部安装证明。
- reviewer/viewer 账号实际分工、私有仓库 token 粘贴、外部 hosted URL、真实恢复演练仍需 operator/customer 参与。
- 新鲜 `hynek/structlog` workspace 尚未接受候选决策，因此 Why/Drift warning 是当前系统的正确保护行为。

下一步优先级：

1. 找一台独立 VM 或测试服务器，按同一 checklist 运行一次真正客户控制主机试用，补齐 external install/customer-host proof。
2. 在新鲜公共仓库上接受 1-3 条高质量候选，复跑 Why/Drift，形成 warning reduction 与 accepted baseline evidence。
3. 针对 n8n benchmark 失败定位是数据质量、阈值还是运行依赖，再决定修复或调整 profile；不要先放宽门槛。
4. 外部 host proof 稳定后，再做 hosted URL 公开演示、恢复流程和操作员交付；billing、多租户、Marketplace、自助 OAuth 继续后置。

### P19：Benchmark Value Outcome 单调判定（本轮完成）

change：`make-benchmark-value-outcomes-monotonic`

完成内容：

- 修复 benchmark 对 `expected_value_outcomes` 的 exact-membership 误判：更强的 product outcome 现在按 `VALUE_OUTCOME_RANK` 识别为 `exceeds_floor`，不是失败。
- `missing_workspace`、`operational_blocked` 保持独立 operational 分支，不能因为“更强”规则被提升为产品通过。
- 报告新增 `value_outcome_assessment`、`minimum_product_value_floor` 和 rank，解释为什么结果是 exact、exceeds_floor、below_floor、operational 或 not_constrained。
- n8n 真实 profile 从原来的 false failure 修复为 `useful_now`、`exceeds_floor`、allowed；固定 live benchmark 从 4/5 恢复为 5/5。

验证证据：

- focused benchmark tests：21 passed；engine：401 passed；API：32 passed；Web：83 passed。
- typecheck、benchmark fixture、OpenSpec strict `90/90` 通过。
- 真实 Chrome 访问 `github-n8n-io-n8n` 的 Dashboard、Review、Why Search、Drift，4/4 页面通过，无 page error、无数据变更。
- release evidence：`passed`；readiness history：`2026-07-15-monotonic-value-outcomes`。

边界与下一步：

- 本 change 只修正 benchmark/reporting 语义，不降低候选质量、Why、Drift 或导入门槛。
- readiness history 仍会显示 optional evidence `not_provided`，这是证据完整度提示，不是 benchmark 失败。
- 下一刀回到真实客户闭环：独立 VM/测试服务器、私有仓库脱敏试用和客户反馈；暂不做 SaaS billing、多租户或 Marketplace。

### P20：可运行自托管源码包（本轮完成）

change：`make-self-hosted-package-runnable`

完成内容：

- self-hosted package 从文档/脚本 handoff 升级为 runnable source-tree handoff，显式包含 Node workspace、Web/API、engine、migrations、prompts、Compose 和 bounded browser smoke。
- verifier 对缺失运行资产和 legacy structure-only package fail closed，并继续排除 secrets、cache、database、build output 和本机 scratch。
- package 在 Windows 系统临时目录外部副本完成冻结依赖安装、Chromium 安装、Engine/API/Web 启动和 imported workspace 浏览器链路。
- 新增 GitHub-hosted Windows package rehearsal workflow；readiness history 纳入 package verification、clean install 和 runnable package evidence。
- Playwright smoke 改为默认自建隔离服务和新数据库，修复复用本地旧服务导致的非确定性。

真实证据：

- 随机公开仓库 `githits-com/githits-cli`：98 artifacts、37 screened in、30 candidates。
- 可见 Chrome 完成 review、Why、Drift、Evidence；Why 2 citations，浏览器报告 pass。
- package verifier pass，276 files；runnable rehearsal 6/6 pass；clean rehearsal 0 blocker。
- canonical pre-release 全通过：engine 409、Web 83、API 32、Playwright 12/12、OpenSpec strict 90/90。
- readiness entry：`docs/evidence/readiness/2026-07-16-runnable-self-hosted-package/`。
- GitHub Actions：普通 CI run `29483070963`、package rehearsal run `29483070983` 全部 success；独立 runner artifact 已上传。
- OpenSpec change 已同步主规格并归档为 `2026-07-16-make-self-hosted-package-runnable`。

边界与下一步：

- 当前 proof 为 `independent_host_package_smoke`，不是 customer-controlled-host proof。
- 依赖默认需要联网下载，尚未生成签名压缩包、checksum 或 SBOM。
- 下一刀按 `2026-07-16-decisionatlas-next-development-plan.md` 先做客户控制主机真实安装，再做正式 release artifact 和离线缓存。

### P21：版本化自托管 Release Artifact（本轮完成）

change：`publish-versioned-self-hosted-artifacts`

完成内容：

- 从 allowlist runnable package 确定性生成单一版本根目录的 ZIP 与 tar.gz，并生成 `release-artifacts.json`、`SHA256SUMS` 和 CycloneDX 1.6 SBOM。
- verifier 在解压前 fail closed 校验 checksum、size、成员一致性、重复/大小写冲突、路径穿越、绝对路径、反斜杠、symlink/special file、禁止目录和 SBOM 结构。
- ZIP 与 tar.gz 均在隔离临时目录解压并再次通过 package verifier；`--extract-verified-to` 只在全部校验通过后保留安全 ZIP 解压结果。
- GitHub Windows package rehearsal workflow 生成并上传版本化发布物和脱敏 JSON/Markdown 证据，不自动创建公开 GitHub Release。
- readiness history 新增 `versioned_self_hosted_release_artifacts` 证据族，并保存 checksum、SBOM、publication 和 verification 报告。

真实证据：

- 实现提交 `3cc30a2`，版本 `0.4.0-artifact-preview`，278 files，CycloneDX 311 components（npm 278、PyPI 33）。
- 随机公开仓库 `aristanetworks/j2lint`；从下载式外部临时目录完成 verify、safe extract、依赖安装、Engine/API/Web 启动和 imported workspace 核心链路。
- 可见 Google Chrome headed 流程通过，保留 Playwright trace；Chrome 插件初始化失败，因此不把插件控制声明为通过。
- Canonical pre-release 通过：engine 424、Web 83、API 32、Playwright 12/12；OpenSpec strict 90/90；专项 release artifact tests 14 passed。
- readiness entry：`docs/evidence/readiness/2026-07-16-versioned-self-hosted-release-artifacts/`，release artifact 0 blocker。

边界与下一步：

- checksum 只证明相对可信 manifest 的完整性，尚无 cryptographic signing 和 vulnerability analysis。
- 发布物不含依赖缓存，受限网络/离线安装仍需 approved cache change。
- 当前 proof 为 `independent_runner_release_artifact`，`is_customer_controlled=false`；下一步仍优先补真实客户控制 VM/服务器证据。
