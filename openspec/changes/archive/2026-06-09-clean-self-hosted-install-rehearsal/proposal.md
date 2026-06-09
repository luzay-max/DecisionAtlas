## Why

DecisionAtlas 已经具备自托管包、验证器、handoff report、license boundary 和发布证据，但这些仍主要证明“开发机能生成交付物”。下一步需要证明一个操作者在干净目录或干净机器上可以按包内文档完成安装前检查、证据归档和阻塞项识别，避免把本地环境偶然成功误判为客户可交付。

## What Changes

- 新增干净自托管安装演练能力，生成 `.tmp/clean-self-hosted-install-rehearsal.json/md`。
- 演练应在隔离 scratch 目录中复制或解包 self-hosted package，验证包内 README、环境模板、runbook、验证脚本、license/support boundary 和 handoff 入口是否可用。
- 演练应接受已有 release evidence、hosted readiness、benchmark comparison、readiness history、package verification、handoff report、public repo import 等证据路径，并把缺失或非干净状态保留为 `not_provided`、`operator_guided`、`warning`、`blocking` 或 `known_limitation`。
- package verifier 和 self-hosted rehearsal 文档需要明确：没有 clean install rehearsal evidence 时，不应宣称外部 operator 可独立试点。
- team handoff report 可以引用 clean install rehearsal evidence，作为客户交付/试点准备度的一部分。
- 不引入 billing、多租户 SaaS、Marketplace、自助 OAuth、在线 license server 或 runtime license enforcement。

## Capabilities

### New Capabilities
- `clean-self-hosted-install-rehearsal`: 定义干净目录/干净机器自托管安装演练、证据输出、状态保留和 operator 可读报告。

### Modified Capabilities
- `offline-self-hosted-release-package`: package 交付合同需要包含 clean install rehearsal 入口和证据期望。
- `self-hosted-delivery-rehearsal`: 自托管交付演练需要把 clean install rehearsal 作为 package handoff readiness 的关键证据。
- `team-handoff-reporting`: handoff report 需要能引用 clean install rehearsal evidence，并保留缺失或非通过状态。

## Impact

- Affected scripts: `scripts/ci/` package/release/readiness/handoff evidence tooling.
- Affected docs: self-hosted package guide、operator runbook、commercialization/productization plans/update log.
- Affected specs: 新增 clean install rehearsal spec，并更新 package、delivery rehearsal、handoff reporting spec。
- Affected tests: 增加 clean rehearsal JSON/Markdown 生成、状态保留、缺失输入、package copy/isolation 的 pytest 覆盖。
- No external service dependency is required; live stack probing remains optional and must not hide local stack failures.
