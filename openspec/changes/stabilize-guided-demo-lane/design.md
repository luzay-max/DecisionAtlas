## Context

DecisionAtlas already has the pieces for a compelling MVP walkthrough: a seeded demo workspace, review flow, why-search, timeline, and drift. The problem is not capability coverage but presentation. The homepage currently exposes guided-demo actions, provider controls, and live-analysis exploration at the same visual level, while downstream pages behave like independent tools instead of a connected walkthrough.

This change is intentionally product-shaping rather than capability-expanding. It touches homepage framing, workspace navigation, dashboard guidance, and step-level page messaging across multiple surfaces. The design must preserve the stable seeded walkthrough while making it obvious that live analysis and provider switching are advanced or experimental paths that do not redefine existing demo results.

## Goals / Non-Goals

**Goals:**
- Make the guided demo the primary and most obvious product path.
- Turn dashboard, review, why-search, timeline, and drift into one connected walkthrough with clear step order and next actions.
- Add stage-aware and completion-aware demo guidance so users know what happened and what to do next.
- Demote provider switching and live repository analysis to advanced or experimental controls with clear boundary copy.
- Extend provenance messaging so review and advanced-entry surfaces do not blur demo and live analysis.

**Non-Goals:**
- Improving live repository analysis accuracy, provider reliability, or network behavior.
- Replacing seeded demo data with live extraction output.
- Adding authentication, multi-user state, or long-lived walkthrough persistence.
- Redesigning core data models beyond any minimal read-model additions needed for guided demo status.

## Decisions

### 1. Treat the MVP as two lanes, with only one primary lane
The product will explicitly present:
- a primary `Guided Demo` lane centered on `demo-workspace`
- a secondary `Advanced / Experimental` lane for provider switching and live analysis

This keeps the stable walkthrough intact while still preserving advanced exploration for internal or curious users.

Alternatives considered:
- Keep all controls visible and rely on copy alone. Rejected because users naturally treat visible controls as first-class actions.
- Remove live analysis entirely from MVP surfaces. Rejected because the capability is still valuable, just not as the main path.

### 2. Model the walkthrough as an ordered step flow across existing pages
The walkthrough will be expressed as a fixed sequence:
1. Prepare demo workspace
2. Review candidate decisions
3. Ask a why-question
4. Inspect accepted timeline
5. Inspect drift

Each page should expose:
- the current step
- the purpose of the step
- the next recommended action

This is a UX model first, not a backend workflow engine.

Alternatives considered:
- Leave each page independent and rely on the demo script. Rejected because the product itself should carry the walkthrough.
- Add a brand-new dedicated walkthrough shell page. Rejected for MVP because the current page structure already maps well to the demo sequence.

### 3. Keep demo progress lightweight and mostly client-visible
Demo guidance should prefer existing read-model signals where possible, such as import status, candidate count, and accepted count. For purely presentational progression such as "step completed" or "next step highlighted", the UI may use lightweight client-side state rather than introducing heavyweight workflow persistence.

This keeps the design proportional to the MVP and avoids turning guided demo state into a new backend subsystem.

Alternatives considered:
- Persist full walkthrough progress in the backend. Rejected as too heavy for a public demo lane.
- Use only static copy with no stateful progression cues. Rejected because users still need feedback after actions complete.

### 4. Use boundary messaging instead of pretending advanced controls are part of the walkthrough
Provider mode controls and live analysis entry points should live behind clearly labeled advanced or experimental affordances. Whenever the user opens that area, the UI should explain that these controls may produce unstable, repo-specific, or non-demo results and do not retroactively change seeded walkthrough content.

Alternatives considered:
- Rebrand provider toggle as part of the demo. Rejected because that would misrepresent the meaning of historical demo results.
- Hide advanced features completely. Rejected because the product still benefits from showing that exploration is possible.

## Risks / Trade-offs

- **[Risk] Demo progress feels artificial if it ignores actual data state** → Mitigation: tie readiness cues to existing import and decision signals where possible, and use client-side step state only for presentational continuity.
- **[Risk] Advanced controls become too hidden for power users** → Mitigation: keep them accessible through an explicit advanced section rather than removing them.
- **[Risk] Added guidance copy creates visual clutter** → Mitigation: centralize walkthrough framing into reusable components such as a progress header, next-step card, and advanced-boundary notice.
- **[Risk] Review and why-search still feel disconnected if only buttons are added** → Mitigation: each page should explain both "why this step exists" and "what to do next," not just offer navigation.
- **[Risk] Demo import progress remains imperfect because backend jobs are still coarse-grained** → Mitigation: map existing stage information into a simple stepper first and avoid promising more precision than the pipeline actually exposes.
