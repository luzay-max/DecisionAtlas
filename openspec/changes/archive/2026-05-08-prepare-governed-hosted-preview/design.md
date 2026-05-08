## Context

DecisionAtlas already has the pieces needed for a credible hosted preview: seeded demo recovery, hosted health/smoke scripts, governance Markdown ingest, accepted-rule review, governance diff/drift checks, an agent guardrail protocol, and a real-repository value benchmark. The gap is orchestration. The current hosted preview guidance validates service availability and the stable demo lane, but it does not yet make the governance loop a first-class external preview story or a quick operator readiness check.

Stage 12 should therefore be a readiness and narrative integration slice. It should not turn hosted preview into production SaaS, and it should not introduce enforcement by default. It should make an operator able to answer: can I show the stable guided demo, can I recover it if state drifted, can I show the governance loop safely, and can I disclose optional real-repository evidence without making unsupported claims?

## Goals / Non-Goals

**Goals:**

- Define a governed hosted preview checklist that can be run or reviewed shortly before an external walkthrough.
- Keep `demo-workspace` as the stable public lane while adding a bounded governance second act.
- Include governance Markdown ingest, accepted-rule review, and agent guardrail summary in operator guidance.
- Record how to interpret `continue`, `caution`, and `pause` during hosted preview preparation.
- Keep optional real-repository value benchmark reports as credibility evidence, not as a prerequisite for the public walkthrough.
- Preserve mandatory release-gate separation from hosted preview and governance advisory checks.

**Non-Goals:**

- No billing, full organization administration, secret vault, marketplace/OAuth self-service, or multi-user review workflow.
- No default CI enforcement of governance guardrail results.
- No hosted environment provisioning system or new deployment topology.
- No automatic acceptance of governance rules from Markdown.
- No requirement that external hosted checks pass in local development without hosted URLs.

## Decisions

1. Treat stage 12 as an operator readiness layer, not a runtime mode.

   The existing architecture already supports local and hosted operator commands. Adding a new `preview` runtime abstraction would hide the real dependencies operators need to understand. The change should strengthen docs, readiness reports, and targeted smoke checks around existing scripts. Alternative considered: add a one-command hosted preview script. Rejected for this slice because hosted URLs, credentials, and provider state are environment-specific and should remain explicit.

2. Keep the public walkthrough and governance walkthrough as two connected acts.

   The public act remains `demo-workspace`: dashboard, review, why-search, timeline, drift. The governance act can follow after the stable demo: import governance Markdown, review rule drafts, accept a bounded rule, run agent guardrail, explain advisory output. Alternative considered: make governance the first public story. Rejected because the seeded guided demo is still the safest way to orient a new viewer before showing AI-native governance.

3. Classify hosted readiness evidence using existing status vocabulary.

   Use `pass`, `blocking`, `non-blocking`, `known limitation`, and `operator-guided` rather than inventing a new scoring system. This keeps stage 12 aligned with existing hosted preview reports. Alternative considered: compute a single readiness score. Rejected because a single score hides whether a failure blocks the public walkthrough or only affects optional lanes.

4. Make guardrail caution/pause disclosure part of preview readiness.

   A hosted preview that demonstrates governance must not hide advisory concerns. `continue` can proceed with normal validation, `caution` must be disclosed or addressed, and `pause` must be shown as a human-decision signal rather than silently remediated. Alternative considered: require guardrail `continue` before every demo. Rejected because `caution` can be legitimate when a known drift signal is documented and non-blocking.

5. Keep real-repository value reports optional and local-report oriented.

   Stage 11 added JSON and Markdown live reports under `.tmp/`. Stage 12 should document how operators can use those reports as optional credibility artifacts, while preserving the stable public walkthrough even when live repositories, providers, GitHub, or network are unavailable. Alternative considered: make live real-repo validation part of the hosted pre-demo minimum. Rejected because it would turn an optional confidence layer into a flaky demo gate.

## Risks / Trade-offs

- [Risk] The governed preview story overstates production readiness. Mitigation: repeat non-goals in hosted preview, release checklist, and demo script; keep production SaaS claims out of scope.
- [Risk] Operator guidance becomes too long to use before a demo. Mitigation: separate a short pre-demo checklist from deeper troubleshooting and keep the 10-minute readiness path explicit.
- [Risk] Guardrail `caution` or `pause` looks like a failure to external viewers. Mitigation: frame it as the product's human-decision boundary and record whether it blocks the preview.
- [Risk] Governance Markdown ingest demo accidentally implies automatic policy enforcement. Mitigation: require the walkthrough to show drafts as human-reviewed and guardrail as advisory.
- [Risk] Optional real-repo reports become stale committed evidence. Mitigation: keep generated reports in `.tmp/` and tell operators to attach or summarize dated results externally.

## Migration Plan

- Update hosted preview and operator documentation additively.
- Add or update readiness report/checklist examples without changing deployment topology.
- Add targeted validation or script coverage only where existing commands need protection.
- Keep rollback simple: if the governed preview story proves too broad, retain the stable demo checklist and remove optional governance/real-repo sections from the external walkthrough.
