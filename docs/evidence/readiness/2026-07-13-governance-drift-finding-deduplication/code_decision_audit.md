# Governance Drift Finding Deduplication Evidence

- Generated: 2026-07-13T11:17:19.9242273+08:00
- Change: deduplicate-governance-drift-findings
- Status: **passed**
- Real workspace: github-jazzband-pip-tools / jazzband/pip-tools

## Measured Outcome

- Repeated-issue findings before precision correction: **28**
- Distinct findings after precision correction: **3**
- Noise reduction: **25 findings / 89.3%**
- The three remaining findings have different semantic identities and were not over-merged.

## Canonical Recurrence Rehearsal

Two temporary, explicit historical-issue documents described the same dashboard drift-duplication failure with wording and order differences.

- API result: one canonical signal
- Occurrences: **2**
- Unique sources: **3** (two historical sources plus current context)
- Chrome label: **重复 2 次 · 3 个来源**
- DOM-CUA navigation to Governance: passed
- Browser console errors/warnings: 0
- Temporary documents removed after capture

## Verification

- Engine: **383 passed**
- Governance-focused engine: **36 passed**
- Monorepo Vitest: **2 packages passed**, web **83 passed**
- Guardrail banner: **2 passed**
- Lint/typecheck: passed
- OpenSpec strict: **86/86**

## Boundaries

- The rehearsal fixture validates canonical grouping without persisting synthetic governance content.
- Normal repository state remains drift_detected with three distinct historical issue signals.
- The guardrail remains advisory and currently reports caution.
- No secrets, private repository content, or raw model output are archived.
