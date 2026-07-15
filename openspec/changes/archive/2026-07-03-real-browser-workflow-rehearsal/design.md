## Context

DecisionAtlas already has unit tests, page-level browser smoke, team self-hosted rehearsal, real repo benchmark evidence, and readiness evidence history. The remaining gap is a repeatable browser-level proof that a human operator can move through the main product workflow and that real GitHub repository context remains visible in the UI evidence.

Current Playwright coverage is useful but fragmented: one smoke file checks homepage/settings/evidence/demo workspace, one checks team account roles, and real repository validation is mostly script/evidence driven. This change connects those pieces into a single rehearsal lane.

## Goals / Non-Goals

**Goals:**

- Add a browser-driven rehearsal that follows the main user journey from onboarding to workspace, review, why-search, drift, evidence, and team permissions.
- Require a real public GitHub repository reference in the rehearsal so the evidence is not demo-only.
- Produce deterministic local test coverage that can run without mutating external GitHub state.
- Keep live-provider limitations explicit as `operator_guided`, `not_provided`, or `warning` when credentials or services are unavailable.

**Non-Goals:**

- Do not add SaaS billing, Marketplace, self-service OAuth, or hosted multi-tenant behavior.
- Do not require a private token or scrape private repository content in the browser test.
- Do not make Playwright depend on a successful live import from GitHub on every CI run.
- Do not replace backend real-repo benchmark or release evidence scripts.

## Decisions

1. Add a dedicated Playwright rehearsal instead of expanding every existing smoke.
   - Rationale: one workflow file makes the human journey clear and keeps page smoke tests focused.
   - Alternative considered: only add component tests. Rejected because the gap is cross-page human behavior.

2. Use real public repository metadata with bounded mocked API responses when needed.
   - Rationale: the UI evidence must show a real GitHub repository reference, but CI/local runs must not be flaky because of GitHub network limits.
   - Alternative considered: force live GitHub import in Playwright. Rejected because provider availability should be separate from UI workflow proof.

3. Keep role and permission checks in the same rehearsal lane.
   - Rationale: the intended product route is self-hosted team usage, so admin/reviewer/viewer behavior must remain visible in the workflow proof.
   - Alternative considered: keep team tests separate only. Rejected because the product handoff depends on showing division of work.

4. Treat browser rehearsal evidence as product-flow proof, not benchmark proof.
   - Rationale: benchmark comparison and live repository analysis already have separate evidence paths. Browser rehearsal proves users can operate the product.

## Risks / Trade-offs

- Playwright selectors can become brittle if UI copy changes. Mitigation: prefer roles, headings, and stable visible workflow landmarks over low-level CSS selectors.
- Mocking API responses can overstate live import readiness. Mitigation: require the rehearsal to label mocked or seeded responses and preserve real live import proof in benchmark/readiness evidence.
- A single long browser test can be harder to debug. Mitigation: split into named phases inside the test and keep existing smaller smoke tests.
- Local proxy or running stack differences can affect browser runs. Mitigation: document and preserve the localhost proxy bypass assumptions already used by Mimo UI smoke.
