# Runnable Self-Hosted Package Rehearsal

## 结论

DecisionAtlas 自托管交付物已从“文档和脚本集合”升级为可运行源码包。包在源码仓库之外的系统临时目录完成校验、依赖安装、Engine/API/Web 启动和浏览器核心链路，运行状态为 `pass`，6 个阶段全部通过。

本证据仍是 `independent_host_package_smoke`，不是客户控制服务器证明。Release evidence 为 `warning`、hosted readiness 为 `operator_guided`，原因是没有外部 hosted URL、客户主机和客户专属 entitlement，而不是包运行失败。

## 实际验证

- 实现提交：`46027d0`
- 包文件数：276
- 隔离包目录：Windows 系统临时目录下的 `package-copy`，不读取维护者仓库运行文件
- 随机公开仓库：`githits-com/githits-cli`
- 实际导入：98 artifacts，37 screened in，30 candidates
- 候选精度报告：`pass`；浏览器审阅后剩余 28 candidates，其中 22 strong、6 partial
- 可见 Google Chrome：review、Why、Drift、Evidence 导航通过
- Why：`ok`，2 条 citations
- Drift evaluation：通过
- Canonical pre-release：409 engine tests、83 web tests、32 API tests、12 Playwright tests 全通过
- OpenSpec strict：90/90

## 证据索引

- [Runnable package rehearsal](runnable_self_hosted_package_rehearsal.md)
- [Package verification](self_hosted_package_verification.md)
- [Clean install rehearsal](clean_self_hosted_install_rehearsal.md)
- [Release evidence](release_evidence.md)
- [Hosted readiness](hosted_readiness.md)
- [Benchmark comparison](benchmark_comparison.md)
- [Real repository core loop](githits-live-core-loop.md)
- [Candidate precision](githits-live-candidate-precision.md)
- [Chrome review screenshot](01-review-before.png)
- [Chrome Why screenshot](02-why-result.png)
- [Chrome Drift screenshot](03-drift.png)
- [Chrome Evidence screenshot](04-evidence.png)

## 未完成边界

- 未在客户控制的独立 VM/服务器上安装，因此不能声明 customer-controlled-host proof。
- 包安装仍需要联网下载依赖，或由操作员提供审核过的 pnpm/uv/browser 缓存。
- 未生成二进制安装器、签名压缩包、checksum 或 SBOM。
- billing、多租户、Marketplace、自助 OAuth、托管密钥库和运行时授权继续后置。
