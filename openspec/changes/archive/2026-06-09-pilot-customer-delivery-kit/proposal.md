## Why

DecisionAtlas 已经具备自托管包、clean install rehearsal、handoff evidence 和 license/support boundary，但外部试点客户仍需要一组“不看源码也能理解和执行”的交付材料。P7 的目标是把技术证据转成试点销售/交付可用的产品化包，降低单人维护者沟通成本。

## What Changes

- 新增试点客户交付包能力，覆盖一页式产品说明、10 分钟演示脚本、试点部署 checklist、交付邮件模板、客户 FAQ、Community / Team Self-hosted / Enterprise Self-hosted 对比表。
- 新增交付包验证脚本，检查客户材料是否齐全、是否引用 self-hosted package、clean install rehearsal、handoff report、license/support boundary、延期能力和明确 deferred lanes。
- self-hosted commercial baseline 需要要求客户交付材料引用试点 evidence，而不是只描述产品边界。
- self-hosted package docs 需要引用试点客户交付包，方便从包交付进入试点评估。
- 不引入 billing、多租户 SaaS、Marketplace、自助 OAuth、在线 license server、强 runtime license enforcement 或企业 SSO。

## Capabilities

### New Capabilities
- `pilot-customer-delivery-kit`: 定义试点客户交付材料、验证证据、客户可读边界和试点评估反馈闭环。

### Modified Capabilities
- `self-hosted-commercial-baseline`: 商业基线需要要求试点交付材料引用 evidence、支持边界、定价/版本边界和延期能力。
- `offline-self-hosted-release-package`: 自托管包需要引用试点客户交付包作为外部评估入口。

## Impact

- Affected scripts: `scripts/ci/` 增加交付包验证器。
- Affected docs: `docs/project/` 新增客户交付材料并更新 package/commercial docs。
- Affected specs: 新增 `pilot-customer-delivery-kit`，更新商业基线和自托管包 spec。
- Affected tests: 增加交付包验证器测试。
- No runtime API, database migration, or external dependency change is required.
