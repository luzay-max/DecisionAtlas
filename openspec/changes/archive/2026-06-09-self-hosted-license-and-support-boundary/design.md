## Context

DecisionAtlas Team Self-hosted now has team accounts, multi-source repository import, review/audit history, offline package tooling, and handoff reporting. The next commercialization step is not a license server; it is a clear offline boundary that lets a customer understand what they may evaluate, what paid tiers include, what support covers, and what remains out of scope.

The target customer is a small team deploying DecisionAtlas on its own server. The first commercial packaging must remain compatible with offline/private deployment and must not add SaaS billing, marketplace OAuth, or runtime enforcement complexity.

## Goals / Non-Goals

**Goals:**

- Define Community, Team Self-hosted, and Enterprise Self-hosted boundaries.
- Provide customer-readable license/support docs and an optional offline entitlement template.
- Include boundary artifacts in self-hosted packages and handoff reports.
- Preserve the ability to run local evaluation without blocking core workflows.
- Make support and upgrade expectations explicit for pilots and paid deployments.

**Non-Goals:**

- Do not implement online license activation.
- Do not implement runtime feature locks or hard enforcement.
- Do not implement billing, subscription management, marketplace checkout, or SaaS tenancy.
- Do not provide legal advice; docs remain product/operational boundary material and can later be reviewed by counsel.

## Decisions

1. Use documentation and manifest evidence before enforcement.

   Rationale: the product is still early and self-hosted/offline. Strong enforcement would slow pilots and create support burden before pricing and customer demand are proven.

   Alternative considered: add a license key check to application startup. Rejected because it risks blocking local evaluation and complicates offline recovery.

2. Provide a structured entitlement template.

   Rationale: customers and operators need a concrete place to record tier, deployment scope, support dates, seats/workspaces, and exclusions, without exposing secrets or requiring a license server.

   Alternative considered: prose-only docs. Rejected because package verification and handoff reports need machine-readable status.

3. Treat missing entitlement as non-blocking for evaluation but warning for clean customer handoff.

   Rationale: Community/evaluation should run without friction, but paid/customer claims should disclose whether entitlement/support boundary was attached.

   Alternative considered: fail package verification when entitlement is missing. Rejected because it would make open/local evaluation unnecessarily brittle.

## Risks / Trade-offs

- Boundary docs may be mistaken for legal terms -> Label them as product/operational terms and recommend formal contract/legal review for paid customers.
- Non-enforcement can allow unlicensed use -> Accept this early-stage trade-off to keep self-hosted pilots simple and rely on support/upgrade value.
- Tier boundaries may change -> Version the template and docs, and keep package manifest evidence explicit.
- Too much commercial detail can distract from product value -> Keep the first version focused on practical Community/Team/Enterprise differences and support expectations.
