## Context

DecisionAtlas has moved beyond internal prototype status: it has local release validation, governance guardrails, real-repository benchmark comparison, release evidence, hosted readiness evidence, and durable readiness evidence history. The current commercial/productization plan changes the near-term target from "complete SaaS platform" to "sellable self-hosted / private deployment product."

The project already has deployment, hosted preview, release checklist, and readiness evidence documentation, but those documents are engineering/operator-oriented. They do not yet form a coherent customer-facing packaging baseline that explains what a Community user can run, what a Team Self-hosted buyer gets, what Enterprise adds, how evidence becomes a commercial handoff, and which SaaS capabilities are intentionally deferred.

## Goals / Non-Goals

**Goals:**

- Create a coherent self-hosted commercial baseline that can be understood by a prospective customer or implementation operator.
- Define Community, Team Self-hosted, and Enterprise Self-hosted boundaries without adding runtime license enforcement in this change.
- Provide a customer-facing install/evaluation path that starts from existing local deployment and validation commands.
- Convert existing release evidence, hosted readiness, benchmark comparison, governance guardrail, and readiness evidence history into a reusable customer handoff story.
- Document private repository, provider credential, backup/recovery, upgrade, limitation, and support boundaries.
- Preserve the current single-operator / owner-scope architecture as the self-hosted baseline rather than introducing full SaaS administration.

**Non-Goals:**

- Do not add billing.
- Do not implement Marketplace or self-service OAuth installation.
- Do not implement multi-tenant SaaS org administration.
- Do not implement a secret vault or hosted credential custody.
- Do not add permanent buyout license workflow.
- Do not add hosted managed service operations.
- Do not rewrite the core import, extraction, why-search, drift, or governance algorithms.

## Decisions

### Treat self-hosted as the near-term product boundary

DecisionAtlas should be packaged as a deployable software product first. The baseline should make local/private deployment understandable and supportable before adding hosted SaaS complexity.

Alternative considered: start billing and SaaS administration now. Rejected because the current commercial plan prioritizes a solo-maintainable product path and the codebase already documents billing, Marketplace, self-service OAuth, secret vault, and full SaaS administration as out of scope.

### Use documentation and evidence packaging before license enforcement

This change should define edition boundaries, support boundaries, and evidence handoff artifacts without implementing license checks in runtime code. This keeps the first commercial slice low-risk and avoids blocking product validation on licensing infrastructure.

Alternative considered: add runtime license validation immediately. Rejected because early customers need deployable clarity and confidence first; license enforcement can follow once pricing and packaging are validated.

### Build around existing commands and evidence

The self-hosted baseline should reuse current commands:

- local/real stack startup and shutdown
- hosted/demo health, smoke, reset, and reseed checks
- release evidence generation
- hosted readiness generation
- benchmark comparison
- readiness evidence history
- governance guardrail

This avoids inventing a second product workflow separate from the tested engineering workflow.

### Separate commercial tiers from SaaS scope

Community, Team Self-hosted, and Enterprise Self-hosted should be described as packaging/support tiers, not as a promise that full SaaS capabilities already exist. SaaS concepts such as billing, hosted tenancy, Marketplace OAuth, and secret vault remain future optional work.

### Make Code Decision Audit the first customer-facing handoff

The most realistic first monetization motion is not "buy a platform blindly"; it is "run DecisionAtlas on a real repository and receive a decision governance report." The template should reuse existing evidence outputs and make the result readable to buyers, operators, and technical evaluators.

## Risks / Trade-offs

- **Risk: Documentation overpromises product maturity.** → Mitigation: every customer-facing doc must disclose limitations and deferred SaaS capabilities.
- **Risk: Edition boundaries look like real license enforcement.** → Mitigation: state that this change defines packaging/support boundaries only; runtime enforcement is out of scope.
- **Risk: Self-hosted setup still depends on operator skill.** → Mitigation: include validation checklist, recovery commands, and readiness evidence generation in the packaging baseline.
- **Risk: Private repo guidance accidentally implies hosted credential custody.** → Mitigation: clearly document that credentials stay in the customer's self-hosted environment and that no secret vault is implemented.
- **Risk: Commercial reporting becomes detached from tested evidence.** → Mitigation: base Code Decision Audit on existing JSON/Markdown evidence commands and readiness evidence history.

## Migration Plan

No data migration is required.

Implementation should update documentation and templates first, then run documentation-facing validation and OpenSpec validation. Existing local and hosted operator commands remain unchanged.

## Open Questions

- Should the first public-facing edition names be `Community`, `Team Self-hosted`, and `Enterprise Self-hosted`, or should they use simpler names before launch?
- Should pricing appear in repository docs, or remain in private sales material until validated with initial users?
- Should runtime license enforcement be proposed only after the first paid pilot, or sooner as a lightweight local license file?
