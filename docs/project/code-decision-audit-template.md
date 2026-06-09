# Code Decision Audit Template

[Home](../../README.md) | [Self-Hosted Commercial Baseline](self-hosted-commercial-baseline.md) | [Self-Hosted Readiness](self-hosted-readiness-checklist.md) | [Real Repository Validation](real-repository-validation-baseline.md)

---

Use this template for a first paid pilot or customer evaluation. It converts DecisionAtlas evidence into a customer-readable handoff without requiring runtime license enforcement.

## Generate From Evidence

Use the report builder when release, hosted readiness, benchmark, and handoff evidence already exists and the customer needs a bounded, readable audit summary:

```powershell
python scripts/ci/collect_code_decision_audit_report.py `
  --customer "Sample Team" `
  --repository "owner/repo" `
  --workspace "demo-workspace" `
  --release-evidence-json .tmp/release-evidence.json `
  --hosted-readiness-json .tmp/hosted-operator-readiness.json `
  --benchmark-trend-json .tmp/real-repo-benchmark-coverage-trend.json `
  --coverage-rehearsal-json .tmp/real-repo-benchmark-coverage-rehearsal.json `
  --team-handoff-json .tmp/team-handoff-report.json `
  --readiness-history-index-json docs/evidence/readiness/index.json `
  --license-support-json templates/self-hosted-entitlement.example.json `
  --output-json .tmp/code-decision-audit-report.json `
  --output-markdown .tmp/code-decision-audit-report.md
```

The generated report preserves `warning`, `blocking`, `operator_guided`, `known_limitation`, and `not_provided` states. It is intentionally bounded: do not attach secrets, raw private repository contents, raw model output, or local-only logs.

## 1. Engagement Summary

- Customer / team:
- Repository or workspace:
- Evaluation date:
- DecisionAtlas version / commit:
- Deployment mode: Community / Team Self-hosted / Enterprise Self-hosted evaluation
- Operator:
- Evidence package:

## 2. Scope

In scope:

- Repository artifacts analyzed:
- Public/private repository access path:
- Workspaces evaluated:
- Why-search questions tested:
- Drift checks performed:
- Governance documents imported:
- Evidence commands run:

Out of scope:

- Billing
- Hosted multi-tenancy
- Marketplace or self-service OAuth installation
- Hosted secret vault
- Permanent buyout licensing
- Broad code-quality audit unrelated to decision memory
- Security penetration test unless separately agreed

## 3. Deployment And Evidence

Deployment summary:

- Web URL:
- API URL:
- Engine URL:
- Database mode:
- Redis mode:
- Provider mode:
- Private repository access mode:

Validation evidence:

| Evidence | Status | Path / link | Notes |
| --- | --- | --- | --- |
| OpenSpec strict validation |  |  |  |
| Governance guardrail |  |  |  |
| Canonical pre-release |  |  |  |
| Release evidence |  |  |  |
| Hosted/operator readiness |  |  |  |
| Benchmark comparison |  |  |  |
| Readiness evidence history |  |  |  |

State vocabulary:

- `pass`: current evidence supports the claim.
- `warning`: usable but needs disclosure or follow-up.
- `blocking`: do not claim readiness until resolved or excluded.
- `operator_guided`: operator action or customer input is still required.
- `known_limitation`: cannot validate in the current environment; rerun condition is known.
- `not_provided`: optional evidence was omitted and is not a hidden pass.

## 4. Decision Map Summary

Summarize the repository's discovered decision memory.

| Area | Decision / candidate | Status | Source evidence | Notes |
| --- | --- | --- | --- | --- |
| Architecture |  | candidate / accepted / rejected / superseded |  |  |
| Runtime / operations |  | candidate / accepted / rejected / superseded |  |  |
| Data / storage |  | candidate / accepted / rejected / superseded |  |  |
| Release / governance |  | candidate / accepted / rejected / superseded |  |  |

Key observations:

- 
- 
- 

## 5. Accepted Decision Evidence

List the highest-value accepted decisions and why they matter.

| Decision | Why it matters | Evidence quality | Source refs | Follow-up |
| --- | --- | --- | --- | --- |
|  |  | strong / reviewable / thin / missing |  |  |

Evidence quality notes:

- Strong evidence includes source references, rationale, and enough context to answer why.
- Reviewable evidence needs human confirmation.
- Thin evidence should not be used as a strong customer claim.

## 6. Why-Search Examples

| Question | Result status | Citation quality | Summary | Follow-up |
| --- | --- | --- | --- | --- |
|  | pass / warning / evidence_limited | strong / partial / missing |  |  |

Recommended customer-facing examples:

- Use questions that a maintainer would naturally ask.
- Prefer examples with source-backed citations.
- Disclose evidence-limited answers rather than presenting them as failures or passes.

## 7. Drift Findings

| Drift area | Status | Evidence | Impact | Recommended action |
| --- | --- | --- | --- | --- |
|  | pass / warning / review_required / evidence_limited / blocking |  |  |  |

Interpretation:

- Drift is conservative and intentionally narrow.
- `review_required` means a human should inspect the signal.
- Evidence-limited drift should guide follow-up import, review, or source selection work.

## 8. Governance Guardrail

Guardrail result:

- Agent status:
- Diff status:
- Drift status:
- Advisory only:
- Recommended next actions:

Disclosure:

- `continue` supports normal review.
- `caution` requires explicit follow-up or handoff disclosure.
- `pause` requires human decision before positive readiness claims.

## 9. Benchmark And Readiness Trend

Benchmark comparison:

- Repositories:
- Improved:
- Regressed:
- Operationally blocked:
- Product-limited:
- Notes:

Readiness evidence history:

- Latest entry:
- Release status:
- Hosted readiness status:
- Benchmark regressions:
- Benchmark blockers:
- Operator-guided lanes:
- Not-provided evidence:

Do not treat `operator_guided`, `known_limitation`, or `not_provided` as pass.

## 10. Limitations

Current limitations observed in this evaluation:

- 
- 
- 

Standing product limitations to disclose when relevant:

- This is a self-hosted/private-deployment baseline, not full hosted SaaS.
- Billing, Marketplace, self-service OAuth, hosted multi-tenancy, and hosted secret vault are not included.
- Private repository credentials remain in the customer's environment.
- Imported workspace quality depends on repository signal quality and provider configuration.
- Generated `.tmp` reports are scratch output unless archived into readiness evidence history.

## 11. Recommendations

Immediate next actions:

1. 
2. 
3. 

Suggested pilot path:

1. Run DecisionAtlas on one representative repository.
2. Review and accept/reject high-value candidate decisions.
3. Run why-search and drift checks against real team questions.
4. Generate release evidence, hosted readiness, benchmark comparison, and readiness history.
5. Decide whether Team Self-hosted or Enterprise Self-hosted packaging fits the customer's operating model.

## 12. Commercial Fit

| Need | Community | Team Self-hosted | Enterprise Self-hosted |
| --- | --- | --- | --- |
| Local proof of value | yes | yes | yes |
| Private repository use | operator-guided / limited | yes | yes |
| Evidence history | manual / limited | yes | yes |
| Support | community/self-guided | paid support boundary | assisted deployment/custom support |
| Offline/private deployment | manual | possible | expected |
| Custom reporting | no | limited | yes |

Recommended tier:

- Community / Team Self-hosted / Enterprise Self-hosted:
- Rationale:
- Open commercial questions:
