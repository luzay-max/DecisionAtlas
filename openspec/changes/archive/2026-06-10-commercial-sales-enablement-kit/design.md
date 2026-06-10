## Overview

Add a small sales enablement layer on top of the existing self-hosted/pilot delivery kit. The materials should help a buyer understand what DecisionAtlas does, when it fits, what evidence it produces, and what is not included.

## Design Decisions

- Keep materials as Markdown under `docs/project/` so they are easy to package, review, and render.
- Treat sales enablement as verified delivery material, not a loose marketing draft.
- Require explicit limitation language: no billing, no managed SaaS, no Marketplace/self-service OAuth, no hosted secret vault, and no runtime license enforcement.
- Keep the use cases tied to the product's current strengths:
  - code decision audit for a real repository
  - team self-hosted governance workflow
  - release/readiness evidence handoff
- Package these files into the self-hosted bundle so a customer evaluator can review them offline.

## Artifacts

- `docs/project/commercial-sales-page-draft.md`
- `docs/project/commercial-one-page-brief.md`
- `docs/project/commercial-use-cases.md`

## Validation

- Pilot kit verifier checks presence and key buyer-facing references.
- Self-hosted package builder includes the materials.
- Self-hosted package verifier requires the materials.
- Tests cover verifier behavior and package inclusion.
- Browser/Chromium review opens the docs and verifies readable headings/key sections.

## Non-Goals

- No billing implementation.
- No hosted SaaS conversion.
- No marketplace/OAuth self-service implementation.
- No runtime license enforcement.
- No legal contract generation.
