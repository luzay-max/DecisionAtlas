# Fresh Public Repository Import Rehearsal

## 用途

该演练用于证明一个公开 GitHub 仓库在当前 owner scope 中不存在 workspace 时，可以完成全新导入，并将下游 Review、Why Search、Drift、guardrail 和浏览器状态组合成可审计证据。

## 运行前提

- 使用 `pnpm run dev:real` 或 `scripts/dev/start-real-stack.bat` 启动 web、API、engine、PostgreSQL 和 Redis。
- 候选池中的仓库必须是公开仓库。
- `.env` 可配置 `GITHUB_TOKEN`，但证据文件不得包含 token。
- 候选仓库已有 workspace 时必须跳过，不能把复用误报为 fresh import。

## 基本命令

```powershell
python scripts/ci/collect_fresh_public_repo_import_rehearsal.py `
  --candidate-file examples/live-benchmarks/fresh-repositories.json `
  --seed 20260710-fresh-01 `
  --output-json .tmp/fresh-public-repo-import-rehearsal.json `
  --output-markdown .tmp/fresh-public-repo-import-rehearsal.md
```

浏览器验证完成后，可用 collector 的 augment 参数写入 browser status/summary。最终通过 `collect_readiness_evidence_history.py archive` 的 `--fresh-public-repo-import-json` 和 `--fresh-public-repo-import-markdown` 显式归档。

## 判定规则

- `fresh_import`：预检不存在 workspace，随后 full import 以 created 路径进入并成功终止。
- `reused_not_eligible`：候选已有 workspace，无论历史 job 成功还是失败，都不能作为 fresh 证据。
- `warning`：导入成功但核心产品链证据不足，或 browser/guardrail/release lane 非 clean。
- `blocking`：候选耗尽、stack/provider 不可用、job 失败或超时且没有成功候选。
- 0 candidate 不等于 import failure，但意味着尚未证明 accepted-baseline 核心价值。

## 2026-07-13 基线

`python-trio/sniffio` 从 `workspace_exists=false` 到导入 147 artifacts 成功；Chrome 路径通过。最终 0 candidate、0 accepted decision，因此 Why/Drift 保持 evidence-limited，readiness 状态为 warning、0 blockers。
