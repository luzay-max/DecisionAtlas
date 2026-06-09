# Pilot Customer FAQ

[Pilot Kit](pilot-customer-delivery-kit.md) | [Tier Comparison](pilot-tier-comparison.md) | [License Boundary](self-hosted-license-and-support-boundary.md)

---

## What does DecisionAtlas do?

DecisionAtlas imports selected repository evidence, extracts candidate software decisions, supports why-search over those decisions, tracks governance rules and drift alerts, and generates release/handoff evidence.

## Where does our code go?

In the self-hosted pilot, repository contents and credentials stay on the customer-controlled host. Generated handoff reports should include bounded summaries and source references, not raw private repository dumps.

## How are private repositories accessed?

Private access is configured by an administrator/operator using the supported provider path. Token material is write-only and should remain backend-side. If access cannot be validated, the evidence must show `operator_guided`, `provider_failure`, `unauthorized`, or another bounded non-pass state.

## What roles exist?

The current small-team model uses:

- admin: accounts, workspace access, imports, credentials, review/governance
- reviewer: decision and drift review
- viewer: read-only decisions, why-search, evidence, drift status

Self-service signup, invitations, SSO, and hosted tenant administration are deferred.

## What evidence should we expect?

Expect package verification, release evidence, hosted/operator readiness, benchmark comparison when available, clean install rehearsal, readiness history, and team handoff report. Non-pass states must remain visible.

## Does this replace GitHub, GitLab, CI, or PR review?

No. DecisionAtlas is not a Git hosting or CI/CD replacement. It adds decision memory, governance drift visibility, and evidence handoff on top of existing repositories.

## How are backups and upgrades handled?

The operator backs up PostgreSQL and `.env` before upgrades. Redis is treated as recoverable runtime/cache state unless the deployment explicitly persists queue state differently. Upgrade and rollback are covered in the operations runbook.

## Is there billing or online license enforcement?

No. Billing, online license server, and runtime license enforcement are deferred. Current tier boundaries are product/support packaging boundaries, not runtime gates.

## What if the pilot needs more time?

Use the pilot extension path: preserve current readiness evidence, record unresolved blockers, define the next repository or workflow to evaluate, and agree whether the extension is self-guided, Team Self-hosted support, or Enterprise-assisted.

## What makes a pilot successful?

A pilot is successful when the team can deploy the package, import at least one meaningful repository, review decisions/drift, generate evidence, and decide whether the result is useful enough to continue.
