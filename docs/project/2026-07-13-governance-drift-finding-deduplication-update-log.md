# 2026-07-13 Governance Drift Finding Deduplication 更新日志

## 完成内容

- 建立并实施 OpenSpec change：deduplicate-governance-drift-findings。
- 通过 CodeGraph 追踪 detector -> guardrail API -> dashboard 的完整传播链。
- 为 GovernanceDriftSignal 增加 occurrence_count 和 source_count。
- 引入 type-aware semantic key、稳定代表选择、唯一 evidence 合并和 12 条 evidence 上限。
- 修复 issue 子串误判：decisions 不再因包含 issue 字符串而被识别为事故。
- 过滤 private issue text、no runtime errors、not a runtime failure 等非事故或否定语句。
- 增加 60% token coverage 门槛，避免大 diff 下的弱重合误报。
- dashboard 仅对 recurrence signal 显示重复次数与来源数。
- guardrail 保留 canonical signal 元数据，CLI/API/evidence 不再各自去重。

## 真实测量

- 当前仓库 repeated issue：28 -> 3。
- 减少 25 条，噪声下降 89.3%。
- 三条剩余 finding 语义不同，未被过度合并。
- recurrence fixture：2 occurrences、3 sources、1 canonical signal。
- Chrome 使用真实 pip-tools workspace 验证 recurrence 标签。
- DOM-CUA 点击治理审阅链接成功进入 Governance。
- console errors/warnings：0。
- fixture 文件在证据采集后删除。

## 自动验证

- drift detector：15 passed。
- drift detector + agent guardrail：36 passed。
- engine full：383 passed。
- monorepo pnpm test：2 packages passed，web 83 passed。
- lint/typecheck：passed。
- OpenSpec strict：86/86。
- guardrail：caution、advisory，无治理 blocker。

## 证据

- docs/evidence/readiness/2026-07-13-governance-drift-finding-deduplication/
- chrome-dashboard-recurrence.png
- guardrail-recurrence.json
- code_decision_audit.json / code_decision_audit.md

## 边界

- 本 change 不处理持久化 workspace drift alert disposition 去重。
- 本 change 不使用 embedding/fuzzy matching；语义键保持确定性和可解释。
- 当前正常仓库仍有三条不同的 repeated issue，需要人工判断是否处置。
- 下一刀进入 imported candidate precision/ranking，重点降低 pip-tools 28 条低置信候选的审阅负担。
