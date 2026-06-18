# Paid Pilot Acceptance Checklist

[Proposal Kit](pilot-commercial-proposal-kit.md) | [Quote Template](pilot-paid-quote-template.md) | [Support And Renewal](pilot-support-renewal-upgrade-boundary.md)

---

Use this checklist to decide whether a paid self-hosted pilot has met its evidence-backed acceptance criteria. This is a product and delivery checklist, not a legal acceptance certificate.

## Required Setup Criteria

- [ ] Customer or operator can start Web, API, Engine, PostgreSQL, and Redis.
- [ ] Admin account is initialized.
- [ ] Reviewer/viewer roles are explained when team workflow is in scope.
- [ ] Environment variables and provider keys remain on the customer-controlled host.
- [ ] Repository token custody remains with the customer/operator.

## Required Evidence Criteria

- [ ] Package verification JSON/Markdown exists.
- [ ] Clean self-hosted install rehearsal is attached or explicitly marked `operator_guided` / `not_provided`.
- [ ] Release evidence JSON/Markdown exists.
- [ ] Hosted/operator readiness JSON/Markdown exists.
- [ ] Readiness evidence history entry exists.
- [ ] Real-repo benchmark comparison evidence exists.
- [ ] Public GitHub import rehearsal evidence exists when public-repo value is claimed.
- [ ] Private-repo pilot evidence verification exists when private-repo value is claimed.
- [ ] Backup/restore/upgrade rehearsal evidence exists before clean continuity claims.
- [ ] Team handoff report exists when multi-account team workflow is claimed.
- [ ] Code Decision Audit report is prepared for customer review.

## Required Product Outcome Criteria

- [ ] At least one selected repository is imported or the blocker is documented.
- [ ] At least one decision candidate is reviewed, or evidence explains why reviewable candidates were not produced.
- [ ] Why-search is demonstrated against accepted decisions or explicitly marked evidence-limited.
- [ ] Drift review is demonstrated or explicitly marked review-required / not-provided.
- [ ] Governance guardrail status is recorded as continue, caution, or pause.

## Acceptance Decision

| Decision | Meaning |
| --- | --- |
| Accepted | Evidence supports the agreed pilot outcome. |
| Accepted with limitations | Core outcome is useful, but some lanes remain warning, operator-guided, known-limitation, or not-provided. |
| Extend pilot | More repository scope, evidence cleanup, or operator support is needed. |
| Not accepted | Blocking evidence prevents the paid pilot from meeting the agreed outcome. |

## Do Not Accept As Clean Pass When

- Backup/restore/upgrade evidence is missing but continuity readiness is claimed.
- Private-repo evidence is missing but private-repo value is claimed.
- Provider tokens, repository tokens, `.env` values, source code, private issue excerpts, payment data, or signed legal terms are present in committed artifacts.
- Billing, hosted multi-tenancy, Marketplace OAuth, hosted secret vault, online license server, or runtime license enforcement is implied as implemented.
