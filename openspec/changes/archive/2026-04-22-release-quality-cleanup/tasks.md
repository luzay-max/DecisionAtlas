## 1. 收口 release baseline validation 入口

- [x] 1.1 审核并更新 `scripts/ci/pre-release.ps1`，确认它是当前 branch baseline 的 canonical 本地发布验证入口
- [x] 1.2 更新 `docs/project/release-checklist.md`，让 checklist 与 canonical release gate、offline benchmark fixture validation、以及 mandatory vs optional validation 的边界一致
- [x] 1.3 对齐任何相关的脚本或命令提示，确保 `uv` / `python -m uv` fallback 口径在 release baseline 中一致

## 2. 对齐 release-facing 文档

- [x] 2.1 更新 `README.md` 与 `docs/project/quick-start.md`，让它们指向同一条 release baseline validation 路径并保持 demo lane / imported lane 边界清楚
- [x] 2.2 更新 `docs/project/demo-script.md` 与 release-facing 说明，确保演示叙事与当前产品基线一致，不把 guided demo 与 imported real-repo 验证混淆
- [x] 2.3 更新 `docs/project/release-notes-v0.2.md`、`docs/project/real-repository-validation-baseline.md` 及必要的 roadmap / baseline 文档，使其反映当前 `v0.2.1` 基线和 curated benchmark 口径

## 3. 验证并收口发布基线

- [x] 3.1 运行 canonical release baseline validation，确认默认本地 gate 可执行并覆盖 demo 与 imported baseline 的要求
- [x] 3.2 修正文档或脚本中因验证暴露出的剩余不一致项，并记录哪些 live real-repo smoke checks 仍属于 operator-guided optional validation
- [x] 3.3 汇总本次 release-quality cleanup 的结果，确保主分支处于“可解释、可重复验证、可发布”的基线状态

## Validation Notes

- [x] Canonical baseline rerun on 2026-04-22 via `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ci\pre-release.ps1`
- [x] Validation-exposed fixes landed before closeout: pre-release now fails hard on non-zero command exit codes, imported drift status normalizes mixed datetime sources to UTC, and demo import mid-flight polling no longer sits on a 1-second test boundary
- [x] Live curated real-repo smoke checks remain operator-guided optional validation; default branch baseline remains the offline pre-release gate plus fixture-backed benchmark validation
