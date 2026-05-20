# Code Decision Audit Sample

## 1. Engagement Summary

- Customer / team: sample self-hosted evaluator
- Repository or workspace: `demo-workspace` plus prior `browser-use/browser-use` benchmark comparison evidence
- Evaluation date: `2026-05-20`
- DecisionAtlas version / commit: `ab248d9`
- Deployment mode: Team Self-hosted evaluation rehearsal
- Operator: local maintainer rehearsal
- Evidence package: `docs/evidence/readiness/2026-05-20-self-hosted-delivery-rehearsal/`

## 2. Scope

In scope:

- Self-hosted delivery rehearsal evidence.
- Seeded demo readiness check.
- Governance guardrail summary.
- Canonical pre-release baseline.
- Release evidence and hosted/operator readiness evidence.
- Real-repository benchmark comparison evidence for `browser-use/browser-use`.

Out of scope:

- Billing.
- Hosted multi-tenancy.
- Marketplace or self-service OAuth installation.
- Hosted secret vault.
- Permanent buyout licensing.
- Broad code-quality audit unrelated to decision memory.
- Security penetration test.

## 3. Deployment And Evidence

Deployment summary:

- Web URL: `http://localhost:3000`, `operator_guided` because probe returned connection refused.
- API URL: `http://localhost:3001`, `pass` because `/health` returned `ok=true`.
- Engine URL: `http://localhost:8000`, `operator_guided` because probe returned connection refused.
- Database mode: project environment supports seeded demo readiness.
- Redis mode: not separately verified in this rehearsal.
- Provider mode: not provided for this rehearsal.
- Private repository access mode: not provided for this rehearsal.

Validation evidence:

| Evidence | Status | Path / link | Notes |
| --- | --- | --- | --- |
| OpenSpec strict validation | `passed` | command output | `42 passed, 0 failed` |
| Governance guardrail | `passed` | `release_evidence.json`, `hosted_readiness.json` | `agent_status=continue`, diff `pass`, drift `clean` |
| Canonical pre-release | `passed` | `.tmp/pre-release-rehearsal-2026-05-20.log` | engine pytest `244 passed`; Playwright smoke `1 passed` |
| Release evidence | `warning` | `release_evidence.json` / `release_evidence.md` | optional targeted test summary `not_provided` |
| Hosted/operator readiness | `operator_guided` | `hosted_readiness.json` / `hosted_readiness.md` | Web, Engine, health, smoke, recovery need operator rerun |
| Benchmark comparison | `passed` | `benchmark_comparison.json` / `benchmark_comparison.md` | regressions `0`, operational blockers `0` |
| Readiness evidence history | `warning` | `entry.json`, `index.md`, `trend.md` | non-clean states preserved |

## 4. Decision Map Summary

| Area | Decision / candidate | Status | Source evidence | Notes |
| --- | --- | --- | --- | --- |
| Release / governance | Use self-hosted delivery rehearsal before customer handoff | candidate | OpenSpec change `rehearse-self-hosted-delivery` | Converts readiness from ad hoc claim to evidence package |
| Runtime / operations | Treat missing Web/Engine as `operator_guided` | accepted for this rehearsal | hosted readiness evidence | Avoids false pass |
| Evidence | Preserve release warning due to missing optional targeted tests | accepted for this rehearsal | release evidence | Required gates still passed |
| Benchmark | Use existing browser-use comparison as optional credibility evidence | accepted for this rehearsal | benchmark comparison evidence | No regressions or operational blockers |

## 5. Accepted Decision Evidence

| Decision | Why it matters | Evidence quality | Source refs | Follow-up |
| --- | --- | --- | --- | --- |
| Preserve non-clean evidence states | Prevents overclaiming readiness | strong | `entry.json`, `hosted_readiness.json` | Rerun Web/Engine/smoke lanes |
| Archive only explicit evidence | Avoids leaking scratch or sensitive data | strong | readiness history archive output | Continue excluding secrets and raw private content |
| Keep SaaS features out of this baseline | Maintains solo-maintainer scope | strong | self-hosted commercial baseline | Revisit only after self-hosted pilots |

## 6. Why-Search Examples

| Question | Result status | Citation quality | Summary | Follow-up |
| --- | --- | --- | --- | --- |
| Seeded demo walkthrough readiness | `pass` | seeded source-backed | Seeded demo lane is walkthrough-ready | Use UI smoke after Web/Engine are up |
| Browser-use benchmark why cases | `pass` | prior benchmark-backed | 3 why cases passed in comparison evidence | Rerun live benchmark when imported workspace is available |

## 7. Drift Findings

| Drift area | Status | Evidence | Impact | Recommended action |
| --- | --- | --- | --- | --- |
| Governance guardrail drift | `pass` | `agent_status=continue`, drift `clean` | No governance pause required | Continue normal review |
| Browser-use drift benchmark | `pass` | 3 drift cases passed in comparison evidence | No benchmark regression | Keep as regression evidence |

## 8. Governance Guardrail

Guardrail result:

- Agent status: `continue`
- Diff status: `pass`
- Drift status: `clean`
- Advisory only: `true`
- Recommended next actions: run required validation and continue normal review.

Disclosure:

- This guardrail supports normal review.
- It is advisory evidence, not a replacement for the canonical release baseline.

## 9. Benchmark And Readiness Trend

Benchmark comparison:

- Repositories: `1`
- Improved: `0`
- Regressed: `0`
- Operationally blocked: `0`
- Product-limited: `0`
- Notes: `browser-use/browser-use` remained `useful_now` and `why_ready`.

Readiness evidence history:

- Latest entry: `2026-05-20-self-hosted-delivery-rehearsal`
- Release status: `warning`
- Hosted readiness status: `operator_guided`
- Benchmark regressions: `0`
- Benchmark blockers: `0`
- Operator-guided lanes: `5`
- Not-provided evidence: `1`

Do not treat `operator_guided` or `not_provided` as pass.

## 10. Limitations

Current limitations observed in this evaluation:

- Web service on `localhost:3000` was not reachable during the probe.
- Engine service on `localhost:8000` was not reachable during the probe.
- Full hosted health and hosted guided-demo smoke were not clean because Web and Engine were missing.
- Reset/reseed recovery drill was not executed.
- Optional targeted test summary was not provided separately in release evidence.

Standing product limitations:

- This is a self-hosted/private-deployment baseline, not full hosted SaaS.
- Billing, Marketplace, self-service OAuth, hosted multi-tenancy, and hosted secret vault are not included.
- Private repository credentials remain in the customer's environment.
- Imported workspace quality depends on repository signal quality and provider configuration.
- Generated `.tmp` reports are scratch output unless archived into readiness evidence history.

## 11. Recommendations

Immediate next actions:

1. Start Web and Engine alongside API, then rerun `scripts/demo/health-check.ps1`.
2. Rerun `scripts/demo/smoke-check.ps1` after Web/API/Engine are reachable.
3. Rehearse reset/reseed recovery and archive a new readiness history entry.

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

- Team Self-hosted evaluation.
- Rationale: current evidence supports private-deployable pilot preparation, but Web/Engine/smoke/recovery lanes need a clean rerun before a strong customer walkthrough claim.
- Open commercial questions: pilot support scope, private repository access path, and handoff cadence.
