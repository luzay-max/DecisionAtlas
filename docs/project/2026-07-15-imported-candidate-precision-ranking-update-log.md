# 2026-07-15 Imported Candidate Precision Ranking Update Log

## Why This Change

Real imported repositories can create a long candidate queue where confidence-only ordering places thin, salvaged, or semantically repeated decisions ahead of better-grounded evidence. This change makes the queue evidence-first and explains why each candidate appears where it does.

## Implementation

- Added nullable bounded candidate extraction metadata for artifact family, parser salvage, recovery, and sparse recovery.
- Added deterministic precision scores, strong/partial/weak tiers, machine-readable reasons, and conservative lexical near-duplicate clustering.
- Made candidate API ordering canonical and evidence-first while preserving non-candidate ordering and all existing review actions.
- Added imported review queue summaries and card-level precision, extraction-origin, and duplicate context.
- Added a live evidence collector at scripts/ci/collect_candidate_precision_evidence.py.

## Real Verification

- Live provider mode: openai_compatible; embedding mode: fake; no credentials were recorded.
- Real jazzband/pip-tools: 27 candidates, 21 strong, 6 partial; legacy top candidate ID 416, precision-ranked top candidate ID 442.
- Fresh real pallets/markupsafe: 5 candidates, 4 strong, 1 partial; candidate ID 454 remained first in both legacy and precision ordering while lower positions changed.
- Real local stack browser rehearsal against pallets/markupsafe: 1 passed.
- Engine: 392 passed; web: 83 passed; API: 32 passed; typecheck and benchmark fixture passed.
- OpenSpec strict validation: 88 passed.
- Durable evidence: docs/evidence/readiness/2026-07-15-improve-imported-candidate-precision-ranking/.

## Boundary

- The before ordering is reconstructed from the same live payload, not presented as a historical snapshot.
- Ranking does not imply acceptance. Candidates remain individually reviewable and require explicit human action.
- GitHub Actions run 29384129719 for commit 2f57d70 passed: Node, typecheck, 392 engine tests, benchmark, and 12 browser smoke tests.

## CI Stabilization

- Run 29382972768 exposed one incorrect sparse-recovery family expectation; the implementation produced the bounded family recorded by the pipeline.
- Runs 29383266063 and 29383685702 exposed that the browser smoke tried to enter Review while a fresh import still held the workspace in a running state.
- The final rehearsal now accepts an existing active import as a valid workspace context, enters Review only when candidates are ready, and still verifies the bounded review link otherwise.

## Post-archive Navigation Race Fix

- Archive follow-up commit 22de990 made the imported smoke locator target the exact workspace-scoped Why Search href; the clean CI run still reproduced the failure while an import completed in the background.
- Root cause was `DemoImportButton` calling `router.refresh()` after its component had unmounted, which could interrupt an in-flight dashboard navigation and return the browser to the workspace dashboard.
- Commit f0b2836 guards the refresh with the mounted state. Local imported browser rehearsal passed 1/1, and GitHub Actions run 29385331090 passed Node, typecheck, 392 engine tests, benchmark, and browser smoke 12/12.

## Next Step

With the change archived and the follow-up CI green, the next priority is sparse-conversion trend evidence across a fixed pool of fresh repositories. Batch rejection, automatic duplicate handling, billing, multi-tenancy, Marketplace, and self-service OAuth remain out of scope.
