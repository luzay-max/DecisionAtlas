# DecisionAtlas · Evidence verification implementation sequence (2026-10-24)

**Baseline:** `main@e6a123e0` after merged PR #20 (CI #232 passed). **Status:** Phase A in review; phases B–D not started. This is a new implementation sequence, not a declaration of production readiness.

## Goal and constraints

Make each candidate decision inspectable against its original stored SourceRef and Artifact, then verify public upstream snapshots and distinguish adoption from mere proposal. Never silently convert evidence checks into an `accepted` review state. Keep all public CI evaluation offline, repeatable, and without private repository content, model API calls, tokens, or new database migrations.

| Phase | Scope | Exit evidence | Status |
| --- | --- | --- | --- |
| **A. Operator-approved snapshot export** | Export one public local SQLite workspace: Decision + SourceRef + Artifact body/quote/span/hash, report states and attribution | Synthetic scoped SQLite tests, deterministic JSON, CLI fail-closed behavior, CI green | **This Draft PR** |
| B. Immutable GitHub source check | Independently capture public GitHub blob/PR responses at fixed SHA, compare quotes and PR merged status, fail closed on missing snapshots | #2559 unmerged vs #2562 merged verified from recorded public API evidence, no live requests in CI | Not started |
| C. Independent human review | Reviewer template, explicit reviewer attribution/time and dispute resolution, preserve unknown values | Signed non-author ratings and raw links; unreviewed remains `not_run` | Not started |
| D. Optional review UI integration | Evidence status and source details in review/search, without auto-accept and without cross-workspace leaks | API authorization tests, browser tests, human usability check | Not started |

## Phase-A design and acceptance

1. Reuse the existing SQLAlchemy `Workspace`, `Decision`, `SourceRef`, `Artifact` and offline `evaluate_evidence`; **no schema changes**.
2. Local operator must explicitly select an **existing SQLite file**, a single public workspace slug and a destination *outside* the Git checkout, then acknowledge data is suitable for export. Open DB read-only; do not commit records or overwrite output.
3. Only canonical `https://github.com/{owner}/{repo}` workspace links and matching citation links without queries/credentials are in scope. Reject cross-workspace or dangling SourceRefs, private/GitHub App/token-backed access types. This is a **defense-in-depth guard**, not proof that a URL's repository is truly public; operator approval is still mandatory.
4. Include original text/quote/span and UTF-8 SHA-256 of the **stored** Artifact content. A SHA embedded in a blob URL is only syntax: upstream provenance remains `remote_not_verified`. PR merge state and model provider are **unknown** unless an operator explicitly declares a FakeProvider provenance; never infer live model quality.
5. Preserve existing `review_state` as metadata but report `human_review=not_run` for the new independent audit. Every diagnostic has `automatic_acceptance=false` and `review_required=true`.
6. CI may exercise only synthetic local SQLite fixtures. **Never upload an actual export as a public CI artifact.** Exported source text can contain personal data or proprietary content even if the workspace's access type was marked `public`.

## PR-A → PR-B gate

- [ ] Source/quote/span/hash agree with the stored database bytes.
- [ ] Explicit consent, public scope, cross-workspace refusal and outside-checkout output enforced by tests.
- [ ] Deterministic single-workspace JSON and no DB mutation.
- [ ] Full GitHub Actions tests pass at the final commit SHA.
- [ ] Independent upstream API snapshot validation, real human sign-off and live-model evaluation remain **not_evaluated / not_run**.

Reference: [PR #11 T0–T4](https://github.com/luzay-max/DecisionAtlas/pull/11); [PR #20 offline diagnostics](https://github.com/luzay-max/DecisionAtlas/pull/20).
