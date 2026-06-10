# DecisionAtlas One-Page Product Brief

[Home](../../README.md) | [Sales Page Draft](commercial-sales-page-draft.md) | [Use Cases](commercial-use-cases.md) | [Pilot Delivery Kit](pilot-customer-delivery-kit.md)

---

## Problem

Most software teams lose decision memory as code changes. Architecture choices, tradeoffs, and governance rules become scattered across commits, docs, issues, and tribal knowledge. New maintainers can see what changed, but not always why.

## What DecisionAtlas Does

DecisionAtlas is a self-hosted decision-governance product. It imports selected repositories, extracts decision candidates, gives reviewers a workflow for accepting or rejecting them, answers why-search questions with citations, detects bounded drift, and produces customer-readable evidence.

## Evidence It Produces

- Accepted decision timeline.
- Why-search answers with source references.
- Drift alerts and follow-up status.
- Governance rule lifecycle evidence.
- Release evidence JSON/Markdown.
- Readiness evidence history.
- Team handoff report.
- Code Decision Audit report.

## Deployment

The current product route is self-hosted/private deployment. Private repository credentials and model provider keys stay on the customer-controlled host. Community supports local evaluation; Team Self-hosted adds team workflow and private repository evaluation; Enterprise Self-hosted adds assisted deployment and support expectations.

## Commercial Fit

| Buyer Need | Fit |
| --- | --- |
| Try on a public repository | Community |
| Evaluate one private repository | Team Self-hosted pilot |
| Run across several workspaces with admin/reviewer/viewer roles | Team Self-hosted |
| Need offline/private network deployment and operator support | Enterprise Self-hosted |

## Boundaries

Current materials do not claim billing, hosted multi-tenancy, Marketplace or self-service OAuth installation, hosted secret vault, runtime license enforcement, or managed SaaS operations. Non-clean evidence states such as `warning`, `operator_guided`, `known_limitation`, and `not_provided` must remain visible in handoff material.

## First Pilot Outcome

A successful first pilot proves that one representative repository can be imported, reviewed, queried, checked for drift, and summarized into a Code Decision Audit with release/readiness evidence attached.
