## Why

DecisionAtlas now has enough governance, benchmark, release evidence, hosted readiness, and evidence-history infrastructure to move from internal engineering maturity toward a sellable self-hosted product baseline. The next step should package the product for local/private deployment, clear tier boundaries, and customer-facing handoff instead of prematurely building billing, multi-tenant SaaS, Marketplace, or self-service OAuth.

## What Changes

- Define a self-hosted commercial baseline for DecisionAtlas with Community, Team Self-hosted, and Enterprise Self-hosted tiers.
- Add customer-facing local/private deployment guidance that explains required services, environment variables, provider credentials, private repository boundaries, verification steps, and recovery expectations.
- Add license, support, limitation, and upgrade-policy documentation for self-hosted usage.
- Add a customer-readable Code Decision Audit / governance report template that turns existing extraction, why-search, drift, governance, release evidence, hosted readiness, benchmark comparison, and readiness evidence history into a commercial handoff.
- Add a self-hosted release/readiness checklist that uses existing evidence commands without introducing SaaS billing, multi-tenant org management, Marketplace, self-service OAuth, or a permanent buyout license.
- Keep hosted managed service as a future optional direction, not a prerequisite for the current product baseline.

## Capabilities

### New Capabilities

- `self-hosted-commercial-baseline`: Defines the product, documentation, packaging, evidence, and operator requirements for a locally deployable / private-deployable commercial DecisionAtlas baseline.

### Modified Capabilities

- `platform-foundation`: Clarifies that the near-term product boundary is self-hosted commercial packaging with Community/Team/Enterprise tiers while full SaaS capabilities remain out of scope.

## Impact

- Documentation under `docs/project/` for self-hosted quick start, deployment boundary, license/support/limitation, upgrade/recovery, and customer handoff.
- Documentation under `docs/plans/` may be referenced but should not be the only operator-facing source.
- Possible README updates to point to the self-hosted commercial baseline and tier boundaries.
- Possible examples/templates for Code Decision Audit and readiness evidence handoff.
- No runtime SaaS billing, no Marketplace integration, no self-service OAuth, no new multi-tenant administration, no secret vault implementation, and no permanent buyout licensing workflow.
