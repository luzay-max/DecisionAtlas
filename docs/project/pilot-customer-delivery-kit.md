# Pilot Customer Delivery Kit

[Home](../../README.md) | [Package Guide](self-hosted-package-guide.md) | [Clean Install Rehearsal](self-hosted-delivery-rehearsal.md) | [Team Handoff](team-handoff-reporting.md) | [License Boundary](self-hosted-license-and-support-boundary.md)

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
