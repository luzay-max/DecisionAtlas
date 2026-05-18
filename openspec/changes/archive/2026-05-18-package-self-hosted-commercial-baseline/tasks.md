## 1. Self-Hosted Product Boundary

- [x] 1.1 Review current README, quick start, deployment, hosted readiness, release checklist, commercial plan, and completion roadmap for overlapping self-hosted guidance.
- [x] 1.2 Define Community, Team Self-hosted, and Enterprise Self-hosted capability/support boundaries in a customer-facing document.
- [x] 1.3 Document deferred capabilities: billing, full SaaS org management, hosted multi-tenancy, Marketplace/self-service OAuth, hosted secret vault, and permanent buyout licensing.

## 2. Customer-Readable Deployment Path

- [x] 2.1 Create or update a self-hosted quick-start guide that explains prerequisites, services, environment variables, startup commands, verification URLs, and shutdown.
- [x] 2.2 Document provider configuration and backend-only credential handling for self-hosted deployments.
- [x] 2.3 Document private repository setup, permission boundary, validation steps, and troubleshooting categories.
- [x] 2.4 Link README and deployment docs to the self-hosted commercial baseline without replacing existing engineering docs.

## 3. Validation, Recovery, And Evidence

- [x] 3.1 Add a self-hosted release/readiness checklist that references OpenSpec strict validation, governance guardrail, pre-release validation, release evidence, hosted readiness, benchmark comparison, and readiness evidence history.
- [x] 3.2 Document backup, restore, upgrade, reset, reseed, and rollback expectations for self-hosted operators using existing supported commands where possible.
- [x] 3.3 Ensure readiness evidence guidance preserves warning, blocking, operator-guided, known-limitation, and not-provided states.

## 4. Commercial Handoff Templates

- [x] 4.1 Create a Code Decision Audit / governance report template for customer evaluations.
- [x] 4.2 Include decision map summary, accepted decision evidence, why-search examples, drift findings, governance guardrail status, release evidence, benchmark comparison, readiness history, limitations, and recommended next actions in the template.
- [x] 4.3 Document how a first paid pilot can use the template without requiring runtime license enforcement.

## 5. Specs, Tests, And Validation

- [x] 5.1 Update relevant docs/spec references so self-hosted packaging is clearly distinct from future hosted SaaS work.
- [x] 5.2 Run documentation/link sanity checks where available.
- [x] 5.3 Run `openspec validate package-self-hosted-commercial-baseline --type change --strict`.
- [x] 5.4 Run `openspec validate --all --strict`.
