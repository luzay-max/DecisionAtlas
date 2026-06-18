## Context

DecisionAtlas now has a strong self-hosted delivery foundation: package build and verification, clean install rehearsal, private-repo evidence templates, backup/restore/upgrade rehearsal, Code Decision Audit output, sales enablement material, and pilot customer delivery docs. The remaining commercial gap is the moment after a qualified evaluator says "what exactly do I buy and how do we judge success?"

The current repository intentionally avoids implemented billing, runtime license enforcement, hosted multi-tenancy, Marketplace OAuth, and customer-specific legal terms. This change keeps that boundary while adding a repeatable proposal kit that a solo maintainer can adapt for a paid pilot.

## Goals / Non-Goals

**Goals:**

- Provide customer-readable proposal, quote, acceptance checklist, support boundary, and renewal/upgrade path materials.
- Keep all numbers and terms as editable draft templates, not as a billing system or legal contract.
- Add machine-readable verification so package/customer handoff can prove the proposal kit is present and warning-preserving.
- Integrate the proposal kit into self-hosted package and pilot delivery references.

**Non-Goals:**

- No online billing, checkout, invoice generation, or payment processing.
- No runtime license enforcement, license server, entitlement activation, or seat metering.
- No legal contract generation or jurisdiction-specific terms.
- No SaaS multi-tenant organization model, hosted secret vault, Marketplace OAuth, or managed hosted operations.

## Decisions

1. **Use docs and verifier first, not product UI.**
   - Rationale: paid-pilot selling needs clear reusable material before it needs a UI workflow.
   - Alternative considered: add a web "Create proposal" page. Rejected because it expands scope into editable documents and customer-specific data handling before the proposal shape is validated.

2. **Keep commercial values as template assumptions.**
   - Rationale: prices, support windows, and pilot duration will change after first customer conversations. Templates keep the repository useful without hard-coding a business model.
   - Alternative considered: encode pricing tiers in runtime config. Rejected because runtime enforcement and billing are explicitly deferred.

3. **Verify evidence references, not customer-specific terms.**
   - Rationale: CI can check that the proposal kit references package verification, release evidence, readiness history, private-repo evidence boundaries, support limits, and acceptance criteria. CI cannot validate a negotiated customer contract.
   - Alternative considered: require complete signed proposal artifacts. Rejected because this repository must not store customer-specific legal or payment data.

4. **Package the proposal kit as public template material.**
   - Rationale: self-hosted operators need the same narrative and checklist during handoff. The package should include draft templates but exclude private customer-specific files.

## Risks / Trade-offs

- [Risk] Draft prices are mistaken for final legal offers. → Mitigation: every proposal material marks itself as a template and requires customer-specific review before sending.
- [Risk] Proposal docs overpromise unsupported SaaS capabilities. → Mitigation: verifier checks deferred capabilities remain visible.
- [Risk] Customer-specific payment or legal data gets committed. → Mitigation: docs instruct operators to keep filled proposals outside the repository; verifier rejects obvious payment/secret/customer-private markers.
- [Risk] Commercial docs drift from actual readiness evidence. → Mitigation: verifier requires references to release evidence, package verification, readiness history, private-repo evidence, and backup/restore/upgrade boundaries.
