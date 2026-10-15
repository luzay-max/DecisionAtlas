## Context

DecisionAtlas currently exposes most core pages through a global sidebar and homepage quick actions. The product already supports login, account scope, team permissions, repository import/reuse, workspace dashboard, review queue, why search, timeline, drift, governance, settings, and evidence. The missing layer is interaction sequencing: users can reach features, but the UI does not consistently explain which action comes next for a given role and workspace state.

The exploration compared the current flow against common complex-app patterns:

- GitLab anchors review work inside project context and centralizes discussion, CI, approval, and history around merge requests.
- Jira-style navigation separates global essentials from project/work navigation.
- Linear's model makes workspace, team, issue, project, and views explicit so users understand where work lives.
- Complex SaaS applications need clear information scent, recoverable paths, role-appropriate entry points, and stable object context.

## Goals / Non-Goals

**Goals:**

- Make workspace the primary context for day-to-day product use.
- Make role-specific next actions obvious after login.
- Move repository import from an advanced homepage control into a guided operational flow.
- Make decision detail the primary object page for review, evidence, source references, drift, and history.
- Make Evidence Center usable as a release/operator readiness surface.
- Preserve existing functionality while improving flow and navigation.

**Non-Goals:**

- Redesign visual style, typography, or color system.
- Replace the current auth model.
- Add billing, marketplace, multi-tenant SaaS operations, or hosted OAuth.
- Rebuild backend import, review, drift, or evidence APIs.
- Remove existing legacy URLs in the first implementation pass.

## Decisions

- Use a workspace-centered information architecture.
  - Current routes such as `/review?workspace=slug` can keep working, but new navigation should prefer object-centered paths or at least make the active workspace explicit on every workspace tool page.
  - Rationale: users should feel they are moving within one workspace, not jumping among unrelated tools.

- Separate global navigation from workspace navigation.
  - Global links: Home, Team, Settings, Evidence, Governance.
  - Workspace links: Dashboard, Review, Search, Timeline, Drift, Decisions.
  - Rationale: this matches common SaaS patterns where account/admin areas and current project/workspace areas are distinct.

- Introduce role-aware entry points without hiding recovery paths.
  - Admin: setup/import/team/system readiness.
  - Reviewer: pending decision review.
  - Viewer: decision discovery/search/evidence.
  - Operator: release evidence/readiness.
  - Rationale: a single homepage cannot efficiently serve every role once the product becomes collaborative.

- Treat repository import as a wizard-like task.
  - Flow: source input -> access check -> existing workspace decision -> import mode -> progress -> workspace dashboard -> review next step.
  - Rationale: this is the commercial self-hosted product's first-value path and should not be hidden behind advanced controls.

- Make decision detail the hub for one decision.
  - The detail page should connect source evidence, review status, review history, related drift alerts, timeline position, and next actions.
  - Rationale: review/search/drift/timeline are different views over decisions; users need a stable object page when they drill in.

## Risks / Trade-offs

- Route migration can break existing links -> Keep current query-based URLs as compatibility paths and update navigation/tests gradually.
- Role-aware navigation can hide important tools -> Keep global search/recovery links and show permission explanations instead of dead ends.
- Import wizard scope can expand into backend work -> Use existing lookup/import APIs first; defer backend changes unless the UI reveals missing states.
- Evidence Center can become another dashboard dumping ground -> Organize it by operator questions: "Can we release?", "What changed?", "What evidence is missing?", "What trend is worse?".

## Migration Plan

1. Document current and target flows in the plan file.
2. Add tests for current critical paths before changing navigation.
3. Introduce a clearer workspace shell and role-aware landing decision while keeping legacy URLs.
4. Move repository import into a dedicated flow using existing APIs.
5. Expand decision detail as the cross-view object page.
6. Reframe Evidence Center around release/operator readiness.
7. Update browser smoke tests to cover admin, reviewer, viewer, and operator paths.

## Open Questions

- Should canonical workspace routes become `/workspaces/[slug]/review` style immediately, or should the first pass keep query-based URLs and only improve labels/context?
- Should Evidence Center be global first, workspace first, or both?
- Should reviewers have a personal "My review queue" across all workspaces, or should they always enter through one workspace?
