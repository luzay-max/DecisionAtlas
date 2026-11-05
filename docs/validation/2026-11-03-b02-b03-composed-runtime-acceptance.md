# B02 + B03 composed behavior acceptance — regression tests integrated into B03 #45

**2026-11-05 · Candidate validation record.** These tests originated in integration-only [PR #47](https://github.com/luzay-max/DecisionAtlas/pull/47), which assembled the B02 lexical retrieval implementation and B03 same-origin cookie implementation with an explicit merge of their shared `apps/web/lib/api.ts`. B02 [#44](https://github.com/luzay-max/DecisionAtlas/pull/44) has since been independently merged at `0df1b2be3b5fb3dbf7a09c558f18f7ab666191f7`; post-merge main CI [#41960827789](https://github.com/luzay-max/DecisionAtlas/actions/runs/41960827789) is SUCCESS.

The composed regression tests and synthetic fixture workflow are now **copied into B03 #45** so the actual B03 candidate, not a separate integration branch, carries cross-feature regression coverage. The shared Web API file retains B02 retrieval-mode types and B03 cookie-only same-origin behavior. **#47 remains integration-only, Draft, and must never be merged.**

## Behavioral acceptance

1. **BFF composition contract:** a Chinese/mixed-language Why request and `lexical_fallback` response survive unchanged; only a validated session cookie is forwarded to Engine; an injected browser session header is ignored; hostile Origin is rejected; duplicate cookie names do not authenticate.
2. **Typed Web transport:** `WhyAnswerResponse.retrieval_mode` and `answer_context.retrieval_mode` survive `lexical_only`, `lexical_fallback`, and `hybrid` variants while the browser calls same-origin `/backend/query/why`, uses `credentials: same-origin`, and never forwards old localStorage tokens or raw session headers.
3. **Real browser composition:** Playwright runs Web → Next.js rewrite → Fastify BFF → FastAPI Engine using only a disposable synthetic fixture. It checks a Chinese PostgreSQL accepted decision, a candidate-only negative question with no primary/citations, HttpOnly/SameSite=Lax cookie attributes, hostile Origin 403, no browser request to port 3001 and no JavaScript-readable localStorage token.
4. **Fixture isolation:** `scripts/ci/seed_b02_b03_composition.py` creates a clearly synthetic workspace/decision/source reference in the CI database. It does not capture real repositories, private data or call paid embedding providers.
5. The full B02 lexical Engine tests, B03 cookie tests, B01 cache regressions and existing Windows/Playwright suites must all pass on the **same updated #45 candidate head**. Separately green feature PRs or the prior #47 CI do not replace this exact-head run.

## Previous evidence vs current gate

The original integration-only #47 head `e6092c8e86e72f613b98dba84aad3a3860485397` passed [CI #41595983746](https://github.com/luzay-max/DecisionAtlas/actions/runs/41595983746). That result validates the prior composite candidate only. Because B02 is now in main and the tests are being transferred to B03, rerun the complete CI on the updated #45 head and inspect browser/Engine logs.

A production HTTPS/reverse-proxy/Origin deployment rehearsal remains separate. No claim of live production validation, real retrieval precision or private-source safety is made here.

**Gate:** #45 remains Draft/unmerged until its exact updated head CI passes and B03 receives independent maintainer approval. #44 approval does not authorize #45. #47 stays a non-mergeable integration record.
