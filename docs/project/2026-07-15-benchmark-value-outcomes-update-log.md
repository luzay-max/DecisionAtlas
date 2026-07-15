# 2026-07-15 Benchmark Value Outcomes Update Log

## 本次目标

修复真实 benchmark 中“产品结果变好但仍被判失败”的判定缺陷，避免通过给单个仓库加例外来掩盖问题。

## 实现结果

- 新增 `_assess_value_outcome`，根据现有 `VALUE_OUTCOME_RANK` 计算最低 product-value floor。
- 新增 bounded assessment：`exact`、`exceeds_floor`、`below_floor`、`operational`、`not_constrained`。
- `missing_workspace` 和 `operational_blocked` 不参与产品价值等级比较，继续保持 operational 语义。
- benchmark JSON 会记录 floor、floor rank 和 assessment，方便 release evidence 解释。

## 真实验证

- 固定 live benchmark：5/5 通过，n8n 从 false failure 变为 `useful_now` / `exceeds_floor` / allowed。
- n8n 当前真实指标：72 candidates、7 accepted、14 strong、thin ratio 0、Why/Drift gate 通过。
- Chrome 真实访问 `github-n8n-io-n8n` 的 Dashboard、Review、Why Search、Drift，4/4 通过，无 page error，没有执行写操作。
- focused benchmark tests：21 passed；engine：401 passed；API：32 passed；Web：83 passed；typecheck、fixture validation、OpenSpec strict `90/90` 通过。

## 证据与边界

- release evidence：`.tmp/monotonic-value-outcomes-release-evidence.json/md`，状态 `passed`。
- comparison：`.tmp/monotonic-value-outcomes-comparison.json/md`；trend：`.tmp/monotonic-value-outcomes-trend.json/md`。
- readiness history：`docs/evidence/readiness/2026-07-15-monotonic-value-outcomes/`。
- 本 change 只影响 benchmark/reporting 判定，不改变产品运行时门禁，也不把 operational failure 说成产品成功。

## 下一步

优先完成独立 VM/测试服务器上的客户控制主机试用，再根据真实 pilot 反馈选择 private-repo evidence、通知或升级回滚深化。
