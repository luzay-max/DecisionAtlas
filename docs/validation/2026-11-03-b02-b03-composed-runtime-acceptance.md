# B02 + B03 combined behavior acceptance — integration-only Draft (2026-11-03)

**Not a feature PR; do not merge this branch.** This branch uses the already verified main after authorized B01 #43 merge (`f2fae3949c2da9b1401ab14c1e0ff00c48592290`; main push CI #41594072583 SUCCESS), then assembles the exact independent draft implementations of B02 [#44](https://github.com/luzay-max/DecisionAtlas/pull/44) and B03 [#45](https://github.com/luzay-max/DecisionAtlas/pull/45), with an explicit content merge for their shared `apps/web/lib/api.ts`. It never changes main or grants authorization to merge B02/B03.

## Behavioral acceptance: not just Git merging

1. **Real Web → Next.js rewrite → Fastify BFF → FastAPI Engine, all running in Windows Playwright smoke**: use a browser with a same-origin HttpOnly `decisionatlas_session` cookie to request `/backend/query/why` for the synthetic Chinese/English question “为什么使用 PostgreSQL 主库保证一致性？”. The engine uses FakeEmbedder **lexical-only** mode; assert real response `retrieval_mode` at root and `answer_context`, expected accepted Chinese PostgreSQL primary, no direct browser request to port 3001 and no JS-readable session token.
2. **Negative evidence**: another Chinese candidate-only question “火星电梯未审核” must not produce a primary/citation. The test source is explicitly generated synthetic text, not real repository evidence.
3. **Request Origin trust**: a hostile Origin POST is blocked. Valid browser same-origin Cookie stays HttpOnly/SameSite=Lax.
4. **BFF behavioral contract, with mocked upstream**: Chinese Why payload and explicit `lexical_fallback` pass through unchanged; only validated cookie session token reaches Engine, an injected raw session header is ignored, duplicate cookie does not authenticate, hostile Origin is rejected.
5. **Typed Web client, with mocked BFF**: `WhyAnswerResponse.retrieval_mode` and `answer_context.retrieval_mode` typecheck and survive all `lexical_only`, `lexical_fallback` and `hybrid` variants, while requests remain `/backend/query/why` and old `localStorage` tokens are never forwarded.
6. The full B02 Chinese/mixed lexical Engine tests, B03 Cookie auth tests, B01 cache regressions and pre-existing Windows/Playwright suites must all run **on the single assembled candidate commit**. No claim that separately green PRs prove composition.

## Gate semantics

If this composite CI fails, fix the underlying B02 or B03 code on the corresponding independent Draft, *not* by silently merging the composite branch; regenerate/retest the candidate before seeking merge approval. If composite succeeds, post a review record to #37/#44/#45, but **do not merge this integration-only PR**. Each actual #44/#45 merge still needs explicit maintainer authorization and new-main exact-head CI. A production HTTPS/Origin and private-data P test is still separate; this CI uses only local disposable synthetic data and FakeEmbedder, with no paid providers.

**Current status:** CI pending on exact composite Head; no human merge approval for #44/#45 or this test-only Draft.
