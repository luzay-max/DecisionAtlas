# 2026-07-13 Fresh Public Repository Import Update

## 本次目标

证明 DecisionAtlas 不依赖复用旧 workspace，也能从一个此前未导入的随机公开 GitHub 仓库完成真实导入、产品核心链路、人类浏览器操作和发布证据归档。

## 实际结果

- 分支：`mimo`。
- 随机池种子：`20260710-fresh-01`。
- 最终仓库：`python-trio/sniffio`。
- 预检：`workspace_exists=false`。
- 导入结果：`fresh_import`，job `79e4f3f9-16ee-407b-80cd-2c91276b6bf7` 成功。
- 导入 artifact：147 条，包括 17 issues、40 PRs、89 commits、1 doc。
- extraction：shortlist 4，screened-in 1，最终 candidate 0。
- Chrome：dashboard、Review、Why Search、Drift、返回 dashboard 均完成，console error 0。
- Why/Drift：诚实返回 `evidence_limited`，没有伪造引用或漂移。
- durable evidence：`docs/evidence/readiness/2026-07-13-fresh-public-sniffio-import-rehearsal/`。
- readiness：`warning`，0 blockers；warning 来自 accepted baseline 缺失、hosted/operator-guided 和既有 release lanes。

## 发现并修复的问题

1. `pytest-dev/pluggy` 首次真实导入受到无效全局 GitHub token 影响，公开仓库请求返回 401。现在公开访问会验证可选全局 token，并仅在公开 401/403 时匿名回退；owner-scoped private token 和 installation token 不回退。
2. `pallets/itsdangerous` 导入遇到 GitHub 502。现在 502/503/504 与传输中断共用既有有界重试预算，不会无限重试。
3. readiness history 原先无法把 fresh import 当作独立证据族。现在可显式归档 JSON/Markdown，并在 index/trend 中显示状态、repo、workspace、artifact 数量、core-loop 和 browser 结果。

## 测试与验证

- import/token/retry/fresh collector：36 tests passed。
- readiness history：6 tests passed。
- OpenSpec strict：84 items passed。
- stack health：web/API/engine 均 HTTP 200。
- guardrail：`caution`；保留 active-change 和 drift 提示，未伪装为 clean pass。
- Chrome Playwright + DOM-CUA：真实页面人工路径通过。
- 独立 Browser/Computer connector 本轮不可调用；Chrome 同时完成语义浏览器操作和 DOM-CUA 人类式点击，并在证据中如实标注。

## 证据

- `fresh_public_repo_import_rehearsal.json/md`
- `full_chain_random_repo_release_rehearsal.json/md`
- `random_repo_warning_lane_reduction.json/md`
- `chrome-sniffio-dashboard.png`
- `chrome-sniffio-why-search.png`
- `chrome-sniffio-drift.png`

## 当前边界与下一步

导入可靠性链路已经真实通过，但 `sniffio` 没有产生 candidate/accepted decision，因此核心价值链仍是 warning。下一刀应优化 sparse repository 的 decision conversion 与 accepted baseline 形成率，并用另一个未导入、决策信号更强的真实仓库做 fresh regression。真实客户控制主机验证仍是独立外部条件，不能由本机 smoke 代替。
