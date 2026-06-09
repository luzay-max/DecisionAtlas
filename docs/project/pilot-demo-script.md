# Pilot Demo Script

[Pilot Kit](pilot-customer-delivery-kit.md) | [Deployment Checklist](pilot-deployment-checklist.md) | [Team Handoff](team-handoff-reporting.md)

---

Use this script for a 10-minute DecisionAtlas self-hosted pilot walkthrough.

## 0:00-1:00 Positioning

Explain:

- DecisionAtlas helps teams recover decision memory from code, docs, and repository evidence.
- It surfaces candidate decisions, why-search answers, governance rules, drift alerts, and handoff evidence.
- The pilot is self-hosted: credentials and repository contents remain on the customer-controlled host.

Avoid claiming:

- SaaS billing
- hosted multi-tenancy
- Marketplace/self-service OAuth
- enterprise SSO
- online license server
- runtime license enforcement

## 1:00-2:30 Repository Setup

Show:

- admin-controlled repository setup
- provider/access mode boundary
- token material is write-only and should stay backend-side
- public repository import path when private access is not available

Evidence to reference:

- package guide
- private repository boundary
- public GitHub import rehearsal

## 2:30-4:00 Decision Review

Show:

- imported candidate decisions
- evidence/source references
- accept/reject/needs-review flow
- review history and actor attribution

Customer question to ask:

- Which decisions in this repository are currently tribal knowledge?

## 4:00-5:30 Why-Search

Show:

- asking why a decision exists
- source-backed answer
- support grading or limitation disclosure

Customer question to ask:

- Which "why" questions does your team answer repeatedly during onboarding or incidents?

## 5:30-7:00 Drift And Governance

Show:

- governance rules
- drift alerts
- acknowledge/resolve/false-positive handling
- rule lifecycle and stale/superseded boundary when applicable

Customer question to ask:

- Which architecture rules drift silently today?

## 7:00-8:30 Evidence And Handoff

Show generated or sample evidence:

- release evidence
- hosted/operator readiness
- benchmark comparison
- clean install rehearsal
- team handoff report

Explain that `warning`, `blocking`, `operator_guided`, `known_limitation`, and `not_provided` states are preserved rather than hidden.

## 8:30-10:00 Close And Next Steps

Confirm:

- pilot repository scope
- deployment owner
- expected review users
- private credential custody boundary
- required evidence before a paid pilot claim
- requested follow-up or extension

End with:

- delivery email template
- deployment checklist
- FAQ
- tier comparison
