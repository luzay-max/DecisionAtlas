# DecisionAtlas Commercial Use Cases

[Home](../../README.md) | [Sales Page Draft](commercial-sales-page-draft.md) | [One-Page Brief](commercial-one-page-brief.md) | [Code Decision Audit](code-decision-audit-template.md)

---

## Use Case 1: Code Decision Audit

### Buyer

A technical lead or consulting team needs to understand a real repository before a refactor, acquisition review, migration, or maintenance handoff.

### Workflow

1. Deploy DecisionAtlas in a customer-controlled environment.
2. Import one public or private repository.
3. Review and accept the strongest decision candidates.
4. Ask why-search questions that a maintainer would naturally ask.
5. Run drift checks for decisions and governance rules.
6. Generate a Code Decision Audit report with release evidence and limitations.

### Output

- Decision map.
- Accepted decision evidence.
- Why-search examples.
- Drift findings.
- Release/readiness evidence.
- Recommended next actions.

### Success Signal

The customer can explain why important parts of the codebase exist and which decisions need review, without exposing raw private repository contents outside their environment.

## Use Case 2: Team Self-hosted Governance Workflow

### Buyer

A small engineering team wants admin/reviewer/viewer collaboration around private repositories without moving credentials into a hosted SaaS.

### Workflow

1. Admin deploys the self-hosted stack.
2. Admin creates reviewer and viewer accounts.
3. Admin binds repository access using customer-controlled credentials.
4. Reviewers process decision candidates, governance rules, and drift alerts.
5. Viewers inspect accepted decisions, why-search answers, timeline, and evidence.
6. The team exports a handoff report for release or planning review.

### Output

- Role-scoped workspace access.
- Review and audit trail.
- Governance rule lifecycle evidence.
- Team handoff report.
- Readiness evidence history.

### Success Signal

The team can split responsibilities without giving every user mutation rights, while keeping private repository credentials and model provider keys inside the self-hosted environment.

## Use Case 3: Release Evidence Handoff

### Buyer

A product or platform owner needs a repeatable release handoff that shows whether decision, governance, benchmark, and readiness evidence is clean enough to claim.

### Workflow

1. Run the canonical release baseline.
2. Generate release evidence JSON/Markdown.
3. Run hosted/operator readiness or mark it operator-guided when URLs are not supplied.
4. Run fixed-pool or random real GitHub repository benchmark rehearsal when relevant.
5. Archive readiness evidence history.
6. Generate team handoff and Code Decision Audit reports.

### Output

- Release evidence.
- Hosted/operator readiness.
- Benchmark comparison or trend evidence.
- Readiness history.
- Team handoff report.
- Customer-readable limitations.

### Success Signal

The release discussion moves from "I think it works" to a dated evidence package that preserves `pass`, `warning`, `blocking`, `operator_guided`, `known_limitation`, and `not_provided` states.

## Deferred Capabilities

These use cases do not require billing, hosted multi-tenancy, Marketplace or self-service OAuth installation, hosted secret vault, runtime license enforcement, or managed SaaS operations.
