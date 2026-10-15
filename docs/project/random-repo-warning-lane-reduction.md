# Random Repo Warning Lane Reduction

日期：2026-07-04

## 目的

`random-repo-warning-lane-reduction` 不是把 warning 变成 pass，而是把随机真实仓库 release evidence 里的 warning 拆成可执行分类：

- `product_controlled`：产品流程、导入质量、review/why/drift/guardrail evidence 可以继续改进。
- `operator_guided`：hosted/customer/browser/operator proof 需要真实人工或客户环境补证。
- `external_dependency`：provider、GitHub API、网络或可用性导致，需要重跑或披露。
- `not_provided`：可选 evidence 没有提供。
- `blocking`：必须先修复的阻塞。

## 本次真实证据

输入 evidence：

- `.tmp/multi-repo-live-diagnosis.json`
- `.tmp/full-chain-random-repo-release-rehearsal.json`
- `.tmp/release-rehearsal-evidence.json`
- `.tmp/real-external-host-trial-evidence.json`

输出 evidence：

- `.tmp/random-repo-warning-lane-reduction.json`
- `.tmp/random-repo-warning-lane-reduction.md`
- `docs/evidence/readiness/2026-07-04-random-repo-warning-lane-reduction-smoke/`

结果：

- 状态：`warning`
- 阻塞：`0`
- 真实随机仓库：`n8n`、`rich`
- 分类 lane：`14`
- 产品可修：`3`
- 人工/host 证明相关：`11`
- 外部依赖：`0`
- 缺失输入：`0`

## 怎么使用

每次 full-chain random repo release rehearsal 之后运行 reducer：

```powershell
python scripts\ci\collect_random_repo_warning_lane_reduction.py `
  --multi-repo-diagnosis-json .tmp\multi-repo-live-diagnosis.json `
  --full-chain-json .tmp\full-chain-random-repo-release-rehearsal.json `
  --release-rehearsal-json .tmp\release-rehearsal-evidence.json `
  --real-external-host-trial-json .tmp\real-external-host-trial-evidence.json `
  --output-json .tmp\random-repo-warning-lane-reduction.json `
  --output-markdown .tmp\random-repo-warning-lane-reduction.md
```

归档到 readiness history：

```powershell
python scripts\ci\collect_readiness_evidence_history.py archive `
  --label random-repo-warning-lane-reduction-smoke `
  --random-repo-warning-lane-reduction-json .tmp\random-repo-warning-lane-reduction.json `
  --random-repo-warning-lane-reduction-markdown .tmp\random-repo-warning-lane-reduction.md
```

## 后续开发判断

当前最高优先级不是继续扩功能，而是优先消掉 `product_controlled` warning：

- 改善真实仓库导入后的 candidate/review evidence。
- 改善 why answer support 与 drift follow-up 解释。
- 让 release rehearsal 明确区分“真实产品问题”和“客户主机 proof 未完成”。
