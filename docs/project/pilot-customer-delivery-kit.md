# Pilot Customer Delivery Kit

[Home](../../README.md) | [Package Guide](self-hosted-package-guide.md) | [Clean Install Rehearsal](self-hosted-delivery-rehearsal.md) | [Team Handoff](team-handoff-reporting.md) | [Private Repo Evidence](private-repo-pilot-evidence-template.md) | [License Boundary](self-hosted-license-and-support-boundary.md) | [Commercial Proposal](pilot-commercial-proposal-kit.md) | [Sales Page](commercial-sales-page-draft.md) | [One-Page Brief](commercial-one-page-brief.md) | [Use Cases](commercial-use-cases.md)

---

Use this kit when preparing DecisionAtlas for a small-team self-hosted pilot, paid evaluation, or customer proof-of-value handoff.

## One-Page Product Explanation

DecisionAtlas is a self-hosted decision-governance product for software teams that need to understand why a codebase changed, which decisions are still supported by evidence, and where architecture or governance drift needs review.

It is not a Git hosting product, CI/CD platform, or PR review replacement. It complements existing repositories by importing selected source/docs, extracting decision candidates, surfacing why-search answers, tracking governance rules, and producing release/handoff evidence.

## Target Customer

- Small engineering teams with private repositories.
- Teams that need architecture decision memory without adopting a full enterprise governance suite.
- Operators who prefer customer-controlled self-hosted deployment over SaaS credential custody.
- Technical leads who need bounded evidence before accepting, rejecting, or revisiting decisions.

## Pilot Outcome

A successful pilot should prove:

- The operator can deploy the self-hosted package using the package guide.
- An admin can initialize the workspace, configure repository access, and create reviewer/viewer accounts.
- Reviewers can process candidate decisions and drift alerts.
- Viewers can read decisions, why-search answers, and evidence without mutation rights.
- Release evidence, clean install rehearsal, and team handoff reports can be generated and reviewed.

## Pilot Materials

| Material | Path | Purpose |
| --- | --- | --- |
| Demo script | `docs/project/pilot-demo-script.md` | Run a 10-minute customer walkthrough. |
| Deployment checklist | `docs/project/pilot-deployment-checklist.md` | Prepare and verify self-hosted setup. |
| FAQ | `docs/project/pilot-customer-faq.md` | Answer customer adoption and risk questions. |
| Tier comparison | `docs/project/pilot-tier-comparison.md` | Explain Community, Team, and Enterprise boundaries. |
| Delivery email template | `docs/project/pilot-delivery-email-template.md` | Send a bounded handoff note with evidence links. |
| Commercial proposal kit | `docs/project/pilot-commercial-proposal-kit.md` | Prepare paid pilot proposal, quote assumptions, acceptance, support, renewal, and upgrade material. |
| Sales page draft | `docs/project/commercial-sales-page-draft.md` | Explain the buyer-facing self-hosted route. |
| One-page product brief | `docs/project/commercial-one-page-brief.md` | Summarize problem, product, evidence, deployment, and commercial fit. |
| Commercial use cases | `docs/project/commercial-use-cases.md` | Describe Code Decision Audit, Team Self-hosted Governance Workflow, and Release Evidence Handoff. |
| Private repo pilot evidence template | `docs/project/private-repo-pilot-evidence-template.md` | Capture sanitized private-repo proof without committing tokens, source content, issue text, or customer identifiers. |

## Evidence To Attach

Before claiming pilot readiness, attach or explicitly disclose missing evidence:

- Package manifest: `.tmp/self-hosted-package/decisionatlas-self-hosted/manifest.json`
- Package verification: `.tmp/self-hosted-package-verification.json` and Markdown
- Clean install rehearsal: `.tmp/clean-self-hosted-install-rehearsal.json` and Markdown
- Release evidence: `.tmp/release-evidence.json` and Markdown
- Hosted/operator readiness: `.tmp/hosted-operator-readiness.json` and Markdown
- Benchmark comparison: `.tmp/real-repo-benchmark-comparison.json` and Markdown
- Team handoff report: `.tmp/team-handoff-report.json` and Markdown
- License/support boundary: `docs/project/self-hosted-license-and-support-boundary.md`
- Commercial proposal kit verification: `.tmp/pilot-commercial-proposal-kit-verification.json` and Markdown when paid pilot outreach is part of the claim
- Private repo pilot evidence verification: `.tmp/private-repo-pilot-evidence-verification.json` and Markdown when private-repo validation is part of the claim

## Paid Pilot Proposal Handoff

Use [Pilot Commercial Proposal Kit](pilot-commercial-proposal-kit.md) when a pilot moves from technical evaluation into paid pilot discussion. The kit links the buyer-facing proposal, quote assumptions, acceptance checklist, support response boundary, renewal path, and upgrade path back to package verification, release evidence, hosted/operator readiness, readiness evidence history, real-repo benchmark, private-repo evidence, and backup/restore/upgrade evidence.

Filled customer-specific quote values, legal terms, payment instructions, customer identifiers, repository names, and private evidence must stay outside the public repository. If proposal evidence is not ready, preserve the relevant `operator_guided` or `not_provided` state instead of implying paid pilot readiness.

## Private Repository Pilot Evidence

Private-repo proof must be handled through [Private Repo Pilot Evidence Template](private-repo-pilot-evidence-template.md). Do not attach raw repository exports, raw issue/PR text, provider output, screenshots containing private code, token values, or customer identifiers.

If a pilot claim says a private repository has been evaluated, attach sanitized evidence generated in the customer-controlled environment or explicitly state that the lane remains `operator_guided` or `not_provided`. The committed example `docs/project/private-repo-pilot-evidence-example.md` demonstrates the safe shape only; it is not private-repo proof.

## Deferred Lanes

The current pilot package does not include:

- billing
- hosted multi-tenancy
- Marketplace or self-service OAuth
- hosted secret vault
- enterprise SSO
- online license server
- runtime license enforcement

Keep these lanes explicit in customer-facing material. Do not describe them as implemented.

## Pilot Feedback Loop

At the end of the pilot, record:

- repositories evaluated
- import outcome and blockers
- decision candidates accepted/rejected
- why-search examples that were useful or weak
- drift alerts accepted/resolved/false-positive
- missing evidence or operator-guided steps
- requested extension, support, or enterprise customization

Use the handoff report and readiness history as the source of truth for follow-up.
