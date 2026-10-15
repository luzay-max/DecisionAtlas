## Context

DecisionAtlas now has self-hosted package materials, pilot delivery docs, commercial proposal docs, private-repo evidence templates, real external host trial evidence, full-chain random repo release evidence, and readiness history. The remaining gap before an external trial is operational assembly: the operator needs one generated package that says what to send, what to run, what evidence exists, and what is still not proven.

## Goals / Non-Goals

**Goals:**
- Generate `.tmp/pilot-customer-trial-package.json` and `.tmp/pilot-customer-trial-package.md`.
- Generate a bundle directory containing a README, operator checklist, and evidence manifest.
- Reference existing required customer materials and source evidence artifacts.
- Preserve warning, blocking, operator-guided, and not-provided states.
- Keep private customer agreements, credentials, repository content, and legal terms outside the repository.

**Non-Goals:**
- Do not create a hosted SaaS onboarding flow.
- Do not run Docker, imports, browser tests, migrations, or release commands from the package generator.
- Do not generate customer-specific legal/commercial terms or license enforcement.
- Do not claim real customer host pass unless supplied evidence proves it.

## Decisions

- Add a standalone Python collector under `scripts/ci/`.
  - Rationale: matches existing evidence tools and can run offline in CI or by an operator.
  - Alternative considered: extend `verify_pilot_customer_delivery_kit.py`; rejected because the verifier checks static docs, while this package composes dynamic evidence.

- Output both top-level `.tmp` evidence and a bundle directory.
  - Rationale: `.tmp` JSON/Markdown supports CI and logs; the directory gives an operator a concrete handoff folder to inspect or copy into a private customer channel.

- Keep source evidence optional but visible.
  - Rationale: current local smoke cannot prove real customer readiness. Missing evidence must remain explicit instead of blocking every local run.

- Treat missing required docs as blocking.
  - Rationale: a trial package without the required customer-facing materials is incomplete regardless of runtime evidence.

## Risks / Trade-offs

- Operators may treat a warning package as customer-ready -> The Markdown and recommended next actions will call out non-clean lanes and proof boundaries.
- The generated folder could be mistaken for a release artifact -> It will remain under `.tmp` by default and document that customer-specific material belongs in a private channel.
- More evidence files increase maintenance surface -> The collector reuses existing paths and summaries rather than duplicating source artifacts.
