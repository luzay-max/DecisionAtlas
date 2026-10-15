# Review Candidates Into Accepted Baseline

## Outcome

The real imported `Textualize/rich` workspace now has a bounded accepted-decision baseline produced through the existing review API and verified through the product UI.

- Workspace: `github-textualize-rich`
- Repository: `Textualize/rich`
- Import mode: real GitHub imported workspace, reused from an earlier successful import
- Before: 35 candidates, 0 accepted decisions
- After: 34 candidates, 1 accepted decision
- Accepted decision: `#241 Don't use windows legacy terminal support when ctypes is not available`
- Review actor: `local-admin` (`admin`)
- Review rationale: `Accepted as a source-backed baseline seed for rich why/drift validation.`

## Implementation

Added `scripts/ci/review_candidates_into_accepted_baseline.py` with two explicit modes:

- Dry-run inspects a bounded candidate prefix without changing review state.
- Confirmed mode requires an explicit confirmation flag, a non-empty rationale, and a bounded `--max-accept` value.
- JSON and Markdown output preserve before/after counts, selected candidate quality, accepted IDs, and limitations without storing credentials or raw private source.

## Real Browser Rehearsal

Chrome was used for human-like interaction against the running local stack:

1. Opened the real imported `github-textualize-rich` review queue and confirmed 34 remaining candidates.
2. Opened accepted decision `#241` and verified status, review actor, rationale, timestamp, and three GitHub source references.
3. Submitted `Why skip Windows legacy terminal support when ctypes is unavailable?` through Why Search.
4. Verified the AI/retrieval answer used the accepted decision and displayed GitHub citations.
5. Opened Drift, clicked `现在评估漂移`, waited for completion, and verified a clean result with evaluation time `2026-07-10T01:51:23.734929+00:00`.
6. Verified the Chrome console had no application errors.

Browser evidence is archived under `docs/evidence/readiness/2026-07-10-review-candidates-accepted-baseline-smoke/`.

## Validation

- Targeted pytest: 23 passed.
- OpenSpec strict validation: 84 passed, 0 failed.
- Full-chain rehearsal: warning, 0 blocking lanes.
- Warning-lane reduction: 11 operator-guided and 3 product-controlled classified lanes, 0 blocking.
- Governance guardrail: caution because historical drift/advisory findings remain; diff check passed.

## Honest Boundary

This rehearsal used real GitHub-derived `Textualize/rich` data, not fixtures or a seeded demo. It reused an existing imported workspace, so it is not evidence of a fresh clone/import on this date. One accepted decision is a thin baseline, not proof that the repository has broad accepted-decision coverage. The next real-repository gate should use a newly selected public repository and perform a clean import before browser review.
