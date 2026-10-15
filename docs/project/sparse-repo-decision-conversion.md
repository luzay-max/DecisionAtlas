# Sparse Repository Decision Conversion

## 运行逻辑

```text
normal shortlist
  -> screening
  -> full extraction
  -> per-artifact recovery
  -> created candidate?
       yes -> sparse skipped / candidate_present
       no  -> bounded sparse selector
                -> family-diverse max 4
                -> grounded extraction
                -> candidate or explicit rejection reason
```

## 不变量

- 只在 normal extraction 创建 0 candidate 时触发。
- 不选择已有 source ref 或已经做过 full extraction 的 artifact。
- 默认最多 4 个模型尝试，预算为 0 时明确跳过。
- recovered candidate 必须有原文可定位 quote 和 source ref。
- recovered candidate 始终处于 `candidate`，不能自动 accepted。
- provider failure 和 null output 不使 artifact import 失败。
- 0 candidate 必须保持 `insufficient_evidence`，不能伪造 clean baseline。

## Summary 字段

- `sparse_recovery_status`: `not_evaluated`、`skipped`、`attempted`、`recovered` 或 `exhausted`
- `sparse_recovery_skip_reason`: `candidate_present`、`disabled_budget`、`no_eligible_evidence` 或 `all_attempts_rejected`
- `sparse_recovery_eligible_artifacts`
- `sparse_recovery_attempted_artifacts`
- `sparse_recovery_model_attempts`
- `sparse_recovery_recovered_candidates`
- `sparse_recovery_evidence_families`
- `sparse_recovery_rejection_reasons`

## 真实基线

- `jazzband/pip-tools`: normal extraction 创建 28 candidates，sparse 正确跳过且 0 extra calls。
- `python-trio/sniffio`: normal extraction 0 candidate，sparse 调用 4 次，全部 null，保持 insufficient evidence。
- 两条路径共同证明“该触发时触发、不该触发时不增加成本、没有证据时不制造决策”。
