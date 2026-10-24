# DecisionAtlas evidence-first roadmap — status update 2026-10-24

## Baseline and scope

Phase A [PR #21](https://github.com/luzay-max/DecisionAtlas/pull/21) and Phase B [PR #22](https://github.com/luzay-max/DecisionAtlas/pull/22) were merged in order. `main@a12cf326` passed [CI #240](https://github.com/luzay-max/DecisionAtlas/actions/runs/40077156396). PR #20 had delivered the earlier 13 synthetic offline evidence regression samples.

The next slice is **Phase C: human evidence-review packet and self-attested annotations**. This stage does not authenticate reviewers or produce human validation metrics from the historic 8 FakeProvider AI-assisted cases. No private-source exports, paid model calls, migration, production API or review-state changes.

| Phase | Deliverable | State | Explicit remaining gate |
| --- | --- | --- | --- |
| A: offline public snapshot export | Decision / SourceRef / Artifact values, read-only operator CLI, scope protections | Merged (#21) | Operator still must verify actual data is public before exporting |
| B: recorded source comparison | Fixed Git blob captures, PR #2559 unmerged vs #2562 merged, no automatic adoption | Merged (#22) | Source fixtures are recorded snapshots, not signed authenticity |
| **C: independent reviewer workflow** | Reduced packet, blank template, self-attested submissions, disagreement report, offline tests | **This Draft PR** | Real reviewers, identity authentication and independent human sign-off remain `not_run` / `not_verified` |
| D: optional review UI | Read-only evidence display with API access control and explicit review action gates | Not started | Must not ingest self-attested summaries as accepted decisions |

## Phase-C acceptance criteria

- [ ] Match Phase-A candidate IDs/source URLs against Phase-B citation checks (same order, exact source identity), reject mismatches and implicit auto acceptance.
- [ ] Generate deterministic packet SHA-256, preserve Phase-A/B digests, show quote/status but avoid full Artifact text in the review packet.
- [ ] Output blank reviewer templates: no fake reviewer, timestamp or decision. Blank submissions are not counted.
- [ ] Reject forged packet mismatches, duplicate reviewer IDs, wrong candidate IDs, missing source/rationale, impossible accepted claims and source checks marked `fail`.
- [ ] Disagreements and missing reviews reported separately; agreement denominator counts only candidates with at least two independent self-attestations, zero denominator returns `null`.
- [ ] Report identity/authentication limits transparently; `automatic_acceptance=false` and database review state unmodified.
- [ ] Windows GitHub Actions CI passes latest PR head (synthetic test data only), with no private data artifacts or model calls.

## Next human gate

Recruit **two real independent reviewers** of an authorized public sample. Each must read the original cited sources, report question/option/tradeoff adequacy, quote support, adopted state, and justification; preserve disagreements as uncertain until separately adjudicated. Without verified identities and actual independent review records, do **not** claim completion of human acceptance or publish a real-model accuracy estimate. The tooling alone is not that gate.

For production reviewer identity/session integration, design explicit authorization and audit first; this PR deliberately avoids modifying existing review APIs and state transitions.
