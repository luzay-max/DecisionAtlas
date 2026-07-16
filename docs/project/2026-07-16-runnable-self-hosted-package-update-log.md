# 2026-07-16 可运行自托管包更新日志

## 本次目标

把此前偏向文档交付的 self-hosted package 改造成可以在源码仓库之外独立安装、启动和验证的运行包，并保留真实客户主机证明边界。

## 已完成

- 包 manifest 升级为 schema 2，使用显式 allowlist 纳入 Node workspace、Web/API、Python engine、Alembic migrations、prompts、Compose 和 bounded smoke assets。
- verifier 对缺失 lockfile、运行源码、Compose、prompts、smoke entry point 和 runtime metadata fail closed；旧结构包不再被误认为 runnable proof。
- 新增 isolated runnable rehearsal：复制到系统临时目录、安装冻结依赖、安装 Chromium、启动 Engine/API/Web、执行 imported workspace browser loop。
- Windows Docker 启停脚本固定 Compose project name 为 `decisionatlas`，避免包目录改名后容器冲突。
- Playwright 默认不再复用端口上任意已有服务；smoke 数据库每轮重建，owner scope/auth 环境固定，避免本机状态污染 CI。
- 新增 GitHub-hosted Windows package rehearsal workflow，并上传脱敏 JSON/Markdown 证据。
- readiness history 新增 package verification、clean install 和 runnable package 三类证据。

## 验证结果

- Canonical pre-release：通过。
- Engine：409 passed。
- Web：83 passed；API：32 passed；typecheck：通过。
- Playwright：12/12 passed。
- OpenSpec strict：90/90 passed。
- Package verifier：`pass`，276 files，0 blockers。
- Runnable package rehearsal：`pass`，6/6 stages，proof level 为 `independent_host_package_smoke`。
- Clean install rehearsal：0 blockers，因外部客户证据缺失保持 `warning`。
- Release evidence：`warning`；hosted readiness：`operator_guided`，符合没有 hosted URL/客户主机的事实。

## 真实仓库与模型

- 使用随机公开仓库 `githits-com/githits-cli`。
- Provider mode 为 live `openai_compatible`；未记录 API key 或原始私有内容。
- 导入完成：98 artifacts、37 screened in、30 candidates。
- 可见 Google Chrome 完成 review、Why、Drift、Evidence；Why 返回 2 citations，浏览器报告为 `pass`。
- Browser/Computer 插件运行时不可用，因此不把插件控制声明为通过；真实可见 Chrome 由 Playwright 驱动完成。

## 提交与证据

- 实现提交：`46027d0 Make self-hosted package independently runnable`
- Readiness entry：`docs/evidence/readiness/2026-07-16-runnable-self-hosted-package/`
- GitHub Actions：待本分支推送并创建 PR 后记录最终 run id 与结果。

## 下一步

1. 在客户或独立测试 VM 上执行同一 package，补齐 customer-controlled-host proof。
2. 输出可分发 zip/tar、SHA-256、SBOM 和版本清单，减少手工目录交付。
3. 增加 pnpm/uv/browser 依赖缓存或离线镜像边界，验证受限网络安装。
4. 用 3-10 人 pilot 验证私有仓库、reviewer/viewer 分工、升级、回滚和恢复。
