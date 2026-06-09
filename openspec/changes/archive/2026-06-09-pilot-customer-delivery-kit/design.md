## Context

当前 DecisionAtlas 已经能完成自托管包构建、package verification、clean install rehearsal、release evidence、hosted readiness、benchmark comparison、team handoff report、license/support boundary。缺口在客户交付表达：外部试点客户不应该通过阅读源码和零散文档来理解产品价值、部署流程、版本边界、反馈方式和延期能力。

P7 以低维护成本为原则，把现有 evidence 和 runbook 组织成一组客户可读材料，并提供验证器确保材料没有漏掉核心入口。

## Goals / Non-Goals

**Goals:**
- 新增客户可读交付材料：one-pager、10 分钟演示脚本、试点部署 checklist、交付邮件模板、FAQ、版本/支持边界对比表。
- 新增验证脚本，输出 JSON/Markdown，检查交付材料是否齐全并引用 self-hosted package、clean install rehearsal、handoff report、license/support boundary 和 deferred lanes。
- 将交付包纳入 self-hosted package docs 和商业基线要求。
- 保持所有材料不包含 secret、token、私有仓库内容或客户专属价格承诺。

**Non-Goals:**
- 不实现在线购买、billing、租户管理、Marketplace、自助 OAuth、企业 SSO、在线 license server、runtime license enforcement。
- 不生成真正合同、发票、报价系统或法务条款。
- 不引入新的前端页面或后端数据库模型。

## Decisions

### Decision: 用 Markdown 交付包而不是站点页面

P7 先在 `docs/project/pilot-customer-delivery-kit.md` 下建立总入口，并拆出邮件模板、演示脚本、FAQ、部署 checklist 和 tier comparison。

Rationale: 单人项目的优先级是可维护、可打包、可随 self-hosted package 一起交付。Markdown 能被包 builder 直接收录，也能在浏览器里打开验证。

Alternative considered: 做 marketing landing page。放弃原因是当前最急的是试点交付，不是公开获客站。

### Decision: 增加验证器而不是只靠人工检查

新增 `scripts/ci/verify_pilot_customer_delivery_kit.py`，检查 required docs、关键短语、deferred lanes、evidence references，并生成 `.tmp/pilot-customer-delivery-kit-verification.json/md`。

Rationale: 交付材料也会漂移。验证器能保证后续改文档不会误删部署、证据、版本边界或反馈闭环。

Alternative considered: 只写 checklist。放弃原因是 checklist 容易过期且不可进入 CI 或 release evidence。

### Decision: Package builder 收录交付材料

将 P7 文档和验证脚本加入 self-hosted package allowlist，让客户拿到包时也能看到试点交付路径。

Rationale: 试点客户的第一触点通常是离线包；如果交付材料不在包里，就仍然依赖维护者口头说明。

## Risks / Trade-offs

- [Risk] 文档像营销材料但不能指导实际部署 -> Mitigation: 每份材料必须引用 package guide、clean install rehearsal、handoff report 或 license boundary。
- [Risk] 版本/支持边界被理解成正式合同 -> Mitigation: FAQ 和对比表明确这是试点/产品化说明，不替代合同。
- [Risk] 文档过多增加维护成本 -> Mitigation: 一个总入口加少量模板，验证器只检查关键入口，不强制复杂格式。
- [Risk] 没有真实客户反馈时内容偏假设 -> Mitigation: 明确“试点反馈表”和“延期能力”作为后续客户输入收集点。

## Migration Plan

1. 新增 P7 文档和验证脚本。
2. 更新 package builder/verifier 和 self-hosted package guide，使包内包含交付材料。
3. 生成一次交付包验证 JSON/Markdown。
4. 用浏览器打开总入口或验证报告，确认可读性。
5. 同步 specs、归档 change、提交并跑 CI。
