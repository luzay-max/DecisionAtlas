## Context

The team self-hosted plan prioritizes manual admin accounts, workspace permissions, token-paste repository access, and read/review/admin separation before SaaS features. The codebase already contains local auth, team account APIs, workspace membership APIs, frontend team management, and Playwright smoke infrastructure, but there is no single browser rehearsal that proves the team product loop end to end.

## Goals / Non-Goals

**Goals:**
- Add a repeatable browser rehearsal for the small-team self-hosted workflow.
- Verify admin account management is visible and usable, while reviewer/viewer roles remain bounded.
- Document how operators collect this evidence during self-hosted delivery.
- Keep rehearsal deterministic for CI while allowing an optional live public GitHub repository validation step.

**Non-Goals:**
- Do not add SaaS billing, marketplace OAuth, Git hosting, SSO, or enterprise license enforcement.
- Do not require private repository credentials for CI.
- Do not replace existing API unit tests; add browser/operator evidence on top.

## Decisions

- Use Playwright for the canonical browser rehearsal.
  - Rationale: the project already uses Playwright smoke infrastructure and CI installs browsers.
  - Alternative considered: only React unit tests; rejected because they do not prove navigation, session, and human-like flow.
- Keep live GitHub repository validation optional and evidence-based.
  - Rationale: public GitHub availability and rate limits are external dependencies, so deterministic CI should not depend on them.
  - Alternative considered: mandatory random live repo import in CI; rejected because it would make validation flaky and network-dependent.
- Record rehearsal guidance in self-hosted docs and update logs.
  - Rationale: the commercial self-hosted path needs operator-readable proof, not just test names.

## Risks / Trade-offs

- Browser rehearsal may duplicate some unit/API coverage -> Keep it focused on product journey proof, not every edge case.
- Live repository checks can fail due to external network/rate limits -> Make them explicit optional evidence with status disclosure.
- Role boundary UI may hide controls while backend also enforces permissions -> Keep backend API tests as the source of enforcement proof and browser tests as usability proof.
