## Context

DecisionAtlas 现在已有 self-hosted package builder/verifier、release evidence、hosted readiness、benchmark comparison、readiness history、public GitHub import rehearsal、team handoff report、license/support boundary。当前缺口不是缺少单点证据，而是缺少一个干净环境交付演练，把这些证据按 operator 视角串起来，并证明包不是只在开发机工作。

P6 应优先服务个人开发者可维护的自托管商业路线：客户拿到离线包后，能按文档完成试点前检查；如果没有真实服务 URL、provider token 或私有仓库凭证，报告必须如实记录，不把缺失包装成通过。

## Goals / Non-Goals

**Goals:**
- 提供一个可重复运行的 clean self-hosted install rehearsal 脚本，输出 JSON 和 Markdown。
- 在隔离 scratch 目录中复制或解包 self-hosted package，验证 package guide、README、env template、runbooks、validation scripts、license boundary、handoff entry 是否存在。
- 复用现有 package verifier 和已有 evidence 文件，不重写 release/readiness/benchmark/handoff 逻辑。
- 对缺失 evidence、local stack failure、operator-guided live checks 保持原始状态。
- 让 package README、operator runbook、handoff report 能引用 clean install rehearsal 作为交付证据。

**Non-Goals:**
- 不自动创建真实数据库、Redis、管理员账号或仓库 token。
- 不实现 SaaS billing、多租户托管、Marketplace、自助 OAuth、在线 license server 或 runtime license enforcement。
- 不把离线包变成加密/防篡改发行物。
- 不要求 CI 每次都启动完整长生命周期服务；真实服务探测保持可选。

## Decisions

### Decision: 新增薄层编排脚本，而不是扩展 package verifier

实现 `scripts/ci/rehearse_clean_self_hosted_install.py`，由它调用或读取 package verifier 输出、检查 clean package copy、汇总其他 evidence。

Rationale: package verifier 的职责是包结构正确；clean install rehearsal 的职责是“operator 是否能按交付材料试点”。拆开后更容易测试，也不会让 verifier 过度膨胀。

Alternative considered: 把所有检查塞进 `verify_self_hosted_package.py`。放弃原因是 verifier 会混入 runtime、handoff、benchmark 语义，难以维护。

### Decision: 使用 scratch copy 代表干净目录演练

默认把 package 复制到 `.tmp/clean-self-hosted-install/<label>/package-copy`，只在该目录做文件和文档入口验证。

Rationale: 单人项目需要低成本、可在 CI/本机重复运行的演练。真实新机器仍可按同一输出报告补跑，但不能让本机流程依赖人工 VM。

Alternative considered: 每次创建 Docker/VM 干净环境。放弃原因是当前项目交付目标先验证 operator 材料，不应引入高运维成本。

### Decision: 证据状态使用有界集合并保留非通过状态

报告使用 `pass`、`warning`、`blocking`、`operator_guided`、`not_provided`、`known_limitation`。缺失可选 evidence 不自动失败，但会影响最终 customer-ready 判断。

Rationale: 自托管交付经常有凭证、私仓、URL 不可用的情况。真实商业交付更需要诚实状态，而不是强行全绿。

Alternative considered: 缺任何 evidence 就 blocking。放弃原因是会阻断离线包结构验证，也不符合 operator-guided 场景。

### Decision: Markdown 面向 operator，JSON 面向 CI/趋势

JSON 保留路径、状态、source evidence、checks、blockers、recommended_next_actions；Markdown 提供摘要、检查项、证据家族、限制和下一步。

Rationale: 客户/操作者读 Markdown，自动化和后续 readiness history 读 JSON。

## Risks / Trade-offs

- [Risk] scratch copy 不是完整新机器验证 -> Mitigation: 报告命名为 clean install rehearsal，不宣称 VM/客户环境全自动通过；真实 URL/服务探测保持显式 evidence。
- [Risk] evidence 文件路径缺失导致误判 -> Mitigation: 所有输入路径先记录 `not_provided` 或 `blocking`，并列出 rerun 条件。
- [Risk] 重复生成 `.tmp` 污染工作区 -> Mitigation: 使用 label 隔离输出，脚本只清理自己控制的 `.tmp/clean-self-hosted-install/<label>`。
- [Risk] package 内文档过期但文件存在 -> Mitigation: 检查关键命令和路径引用，并在后续 P7/P10 继续做人读演练和升级恢复演练。

## Migration Plan

1. 新增 clean install rehearsal 脚本和测试。
2. 更新 self-hosted package README/runbook/guide，加入 clean rehearsal 命令。
3. 更新 handoff report collector，使其可引用 clean install rehearsal evidence。
4. 生成一次真实 `.tmp/clean-self-hosted-install-rehearsal.json/md`，并用浏览器打开 Markdown 进行 operator 可读性验证。
5. 归档 OpenSpec change，并同步主 specs。
