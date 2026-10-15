## Context

The product direction is GitLab-like small-team self-hosting: an admin imports repositories and assigns accounts, reviewers inspect decisions, and viewers can read outcomes without taking privileged actions.

Existing work covers team roles and review actions. This change focuses on interaction clarity, not a new permission engine.

## Goals / Non-Goals

**Goals:**

- Make current role and available actions visible in the review/audit surface.
- Show recent audit/review activity near the decision list or review flow.
- Make viewer read-only state explicit instead of merely hiding buttons.
- Provide a clearer next-action panel for pending review, accepted/rejected decisions, and missing candidates.
- Cover the behavior with component and browser-level tests.

**Non-Goals:**

- Do not add billing, marketplace, OAuth, or SaaS multi-tenancy.
- Do not redesign the full visual system.
- Do not change backend authorization semantics unless tests reveal a bug.
- Do not add complex notification workflows.

## Decisions

1. Improve existing surfaces rather than adding a separate admin console.
   - Rationale: small-team users need fewer page jumps.

2. Prefer explicit read-only guidance over silent absence of controls.
   - Rationale: viewers should understand why they cannot review.

3. Keep audit trail compact.
   - Rationale: the next release needs operational clarity, not a full compliance product.

## UX Shape

```text
Workspace / Review Page
  ├─ Role + permission banner
  ├─ Review queue / decision candidates
  ├─ Action panel
  │   ├─ reviewer/admin: accept / reject / needs evidence
  │   └─ viewer: read-only explanation + request reviewer action
  └─ Recent audit trail
      ├─ who
      ├─ action
      ├─ decision
      └─ time / source
```

## Risks / Trade-offs

- Tests may be coupled to existing fixtures. Mitigation: add small stable labels/test ids.
- Some audit data may be missing in demo fixtures. Mitigation: render empty state with next action.
- Role state may currently be client-side fixture driven. Mitigation: keep this change presentation-only unless a real auth bug is found.
