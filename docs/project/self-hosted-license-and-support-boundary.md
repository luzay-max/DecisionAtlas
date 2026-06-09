# Self-Hosted License and Support Boundary

[Home](../../README.md) | [Self-Hosted Package](self-hosted-package-guide.md) | [Team Handoff](team-handoff-reporting.md)

---

This document defines DecisionAtlas self-hosted product and support boundaries for evaluation, paid small-team use, and enterprise private deployment. It is product/operational guidance, not legal advice. Paid customer contracts can replace or extend this document.

## Tier Summary

| Tier | Intended use | Deployment scope | Support boundary | Upgrade access | Runtime enforcement |
| --- | --- | --- | --- | --- | --- |
| Community | Local evaluation, demos, individual exploration | Local or internal non-production use | Community/best-effort docs only | Public releases when available | None |
| Team Self-hosted | 5-30 person team using private server deployment | One customer-controlled deployment unless contract says otherwise | Paid setup/support window, upgrade guidance, recovery runbook support | Included during active support term | None in this stage |
| Enterprise Self-hosted | Larger/private deployment with stricter operations | Contract-defined private deployment scope | Custom support, deployment assistance, recovery rehearsal, security review support | Contract-defined upgrade path | None in this stage unless separately agreed |

## What Paid Support Covers

- Initial self-hosted package walkthrough.
- Environment and startup guidance.
- Readiness evidence and handoff report interpretation.
- Upgrade and rollback guidance for supported revisions.
- Recovery runbook guidance for DecisionAtlas application state.
- Triage of DecisionAtlas defects reproducible on a supported revision.

## What Paid Support Does Not Cover By Default

- Git hosting, CI/CD, issue tracking, or code review replacement.
- Customer GitHub/GitLab/Gitee account administration.
- Customer network, firewall, proxy, Docker, PostgreSQL, Redis, or OS administration outside DecisionAtlas-specific guidance.
- SaaS billing, hosted multi-tenancy, Marketplace/self-service OAuth, hosted secret vault, or enterprise SSO.
- Runtime license enforcement, license server operation, or online activation.
- Legal review, procurement language, or customer contract drafting.

## Evaluation Boundary

Community/local evaluation remains non-blocking. Missing entitlement evidence should not stop the application from running. It should be disclosed in package verification and team handoff reports before a clean paid-customer claim is made.

## Entitlement Record

Use `templates/self-hosted-entitlement.example.json` as an offline template for pilots or paid deliveries. Keep customer-specific entitlement files on the operator-controlled host or in a private delivery folder. Do not include repository tokens, `.env` values, private source archives, payment data, or personal secrets.

## Deferred Commercial Capabilities

These remain intentionally deferred:

- SaaS billing and subscription management.
- Hosted multi-tenancy.
- Marketplace or self-service OAuth installation.
- Enterprise SSO.
- Hosted secret vault.
- Runtime license enforcement or online activation.
