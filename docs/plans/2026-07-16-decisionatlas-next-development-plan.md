# DecisionAtlas 后续开发计划（2026-07-16）

## 当前里程碑

DecisionAtlas 已具备“可运行源码包”能力：交付包包含完整运行输入，可在维护者仓库之外安装依赖、启动 Engine/API/Web，并用真实公开仓库执行浏览器核心链路。当前缺口不再是“能否运行”，而是“能否被陌生客户稳定拿走、安装、升级和长期维护”。

当前证据等级：

```text
本机源码运行                 已完成
本机隔离 package-copy 运行   已完成
GitHub 独立 runner 回归       已完成，run 29483070983
客户控制 VM/服务器运行        未完成
2-3 个真实团队持续 pilot       未完成
```

## P0：客户控制主机真实安装证明

建议 change：`prove-runnable-package-on-customer-host`

目标：

- 在非开发者日常工作站的独立 VM、测试服务器或试用客户服务器上接收实际交付包。
- 由目标主机操作员完成依赖安装、首次启动、管理员登录、健康检查和停止/重启。
- 导入一个公开仓库和一个客户允许的私有仓库，完成 reviewer/viewer 分工、审阅、Why、Drift、Evidence。
- 记录耗时、失败点、恢复动作、主机类别和脱敏版本信息。

验收：

- `is_customer_controlled=true` 或明确的独立第三方 operator ownership。
- 核心 lane 无 blocking；所有 warning 有责任人和复跑条件。
- 不读取开发者源码仓库、`.tmp`、已有数据库或本机依赖目录。

难度：高。代码量中等，主要风险是环境、操作员协作和证据真实性。

## P1：正式可分发 Release Artifact

建议 change：`publish-versioned-self-hosted-artifacts`

目标：

- 从 allowlist package 生成版本化 zip/tar.gz。
- 生成 SHA-256、文件清单、SBOM 和版本/commit 信息。
- 在 GitHub Release 或受控交付目录发布，不要求客户 clone Git 仓库。
- 验证解压路径含空格、非默认盘符和目录改名。

验收：

- 下载、checksum 校验、解压、启动、smoke 全链路自动化。
- 发布物不含 `.env`、token、数据库、缓存、测试结果和本机路径。
- 回滚时能重新取得上一版本发布物。

难度：中等。技术确定性高，但安全清单和发布可重复性要求严格。

## P2：受限网络与离线依赖边界

建议 change：`support-approved-offline-dependency-cache`

目标：

- 定义 pnpm store、uv wheel/cache、Playwright browser 和容器镜像的允许缓存格式。
- 提供“联网准备缓存、离线安装消费缓存”的双阶段流程。
- 明确不把任意开发者缓存直接打进客户包，避免供应链和体积失控。

验收：

- 在阻断公网的临时环境完成安装和启动。
- 缓存有 checksum/SBOM，缺失依赖时 fail closed 并给出准确诊断。
- 在线源码包和离线增强包使用同一运行 manifest。

难度：中高。主要风险是 Windows/Python/Node/浏览器/容器多套依赖体系的一致性。

## P3：3-10 人真实团队 Pilot

建议 change：`run-small-team-private-repo-pilot`

目标：

- 管理员手动创建账号并分发 reviewer/viewer 权限。
- 管理员在服务器端粘贴私有仓库 token，浏览器不回显、不持久化到 evidence。
- reviewer 完成候选审阅和 drift disposition；viewer 只读决策、Why、Timeline 和 Evidence。
- 收集审阅耗时、候选接受率、Why 命中率、误报和操作员支持工单。

验收：

- 至少一个真实团队连续使用 1-2 个 release 周期。
- 权限越权、token 泄露、workspace scope 混淆为零。
- pilot 反馈进入 OpenSpec、benchmark 和 readiness history，而不是只留在聊天记录。

难度：高。功能基础已有，真正难点是权限边界、数据安全和持续反馈。

## P4：升级、回滚与可观测性产品化

建议 changes：

- `productize-self-hosted-upgrade-rollback`
- `add-operator-diagnostics-bundle`

目标：

- 版本升级前自动备份、检查 schema、输出升级计划。
- 失败时恢复数据库和上一版本 artifact。
- 一键导出脱敏诊断包：版本、健康、迁移、队列、错误分类，不包含 token/私有源码。

难度：高。必须在真实 pilot 暴露的故障基础上推进，不能只做理想化脚本。

## 暂缓范围

在客户主机证明和至少 2-3 个稳定 pilot 前继续暂缓：

- billing 和在线支付
- hosted SaaS 多租户
- Marketplace 和自助 OAuth
- 企业 SSO 与复杂组织层级
- 在线 license server 和强制运行时授权

## 执行顺序

```text
客户主机证明
  -> 版本化发布物/checksum/SBOM
  -> 受限网络离线缓存
  -> 小团队私有仓库 pilot
  -> 升级/回滚/诊断产品化
```

每一步都必须保留 `pass`、`warning`、`blocking`、`operator_guided`、`not_provided` 的真实状态，不能用本机 smoke 替代客户证据。
