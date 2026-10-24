# Phase C — independent human evidence review (offline, self-attested)

**Status:** Draft implementation. This is an *operator-only offline process* for collecting human annotations after Phase A (public SQLite snapshot) and Phase B (recorded GitHub source comparison). It does **not** perform authenticated human identity verification, produce cryptographic signatures, or update any production Decision review state.

## Workflow

All paths below must point to **approved, local, public-only content**. Do not commit or upload real review packets/assessments or candidate source excerpts to public GitHub Actions. All output paths must be new files **outside** the Git checkout.

1. Prepare the review packet by joining the Phase-A export and Phase-B report **in their original order**. A candidate's ID, citation index, URL and prior offline check are verified against one another; mismatches are rejected. Full Artifact snapshot bodies are deliberately **not** copied into this reduced packet, but candidate fields and quotations can still contain sensitive text.

   ```sh
   uv run --project services/engine python scripts/eval/human_evidence_review.py prepare \
     --snapshot /local/public-phase-a.json \
     --verification /local/public-phase-b.json \
     --output /local/review-packet.json \
     --approve-public-data
   ```

2. Generate **separate blank submission templates** for each reviewer using the same packet. They must not collaborate before initially recording independent assessments. The command never invents reviewer identity, time, conclusion or sign-off.

   ```sh
   uv run --project services/engine python scripts/eval/human_evidence_review.py template \
     --packet /local/review-packet.json \
     --output /local/reviewer-a-blank.json \
     --approve-public-data
   ```

3. Each reviewer independently inspects **the actual linked source** and fills their own JSON with:
   - `reviewer_id`: a unique, nonempty pseudonymous identifier (not a verified login).
   - `reviewed_at`: explicit timezone-aware ISO-8601 timestamp supplied by the reviewer.
   - `independent_of_candidate_author_attested=true` and `original_sources_checked_attested=true`, but **only if those statements are true**. An assertion alone does not authenticate them.
   - For each reviewed candidate: `decision_quality` = `real_decision` / `not_a_decision` / `uncertain`; `quote_validity` = `supported` / `unsupported` / `not_evaluated`; `adoption_evidence` = `adopted` / `not_adopted` / `unknown`; `verdict` = `accept` / `reject` / `uncertain`; plus an explicit rationale and `source_urls` taken from that candidate's actual packet links.
   - Reviewers may submit only a **subset of candidates**; unsupplied items remain `not_run`. A claimed `accept` requires positive judgments, cited packet sources and no `fail` finding for cited sources. Even then it stays **a reviewer assertion**, not a production-approved Decision.

4. After human reviewers have independently supplied their actual records, summarize them:

   ```sh
   uv run --project services/engine python scripts/eval/human_evidence_review.py summarize \
     --packet /local/review-packet.json \
     --submission /local/reviewer-a-filled.json \
     --submission /local/reviewer-b-filled.json \
     --output /local/reviewer-agreement.json \
     --approve-public-data
   ```

   Without `--submission` files the resulting `human_review` is `not_run`; blank templates are rejected as completed submissions.

## Results and limits

- Review packet has `packet_sha256`, an **unsigned deterministic SHA-256 fingerprint** over its data, and fingerprints of the Phase-A/B inputs. Every submission must reference the same packet hash; changed or mixed records fail closed. **A hash alone does not authenticate a person or GitHub's real origin.**
- Duplicate reviewer identifiers (case-insensitive), invalid timestamps, duplicate/unknown candidates and off-packet source URLs fail validation. A single review is `single_review`; matching opinions from two or more self-attested reviewers are `agreed`; divergent verdicts are `disputed`. A candidate without reviews stays `not_run`.
- The report's verdict agreement **numerator/denominator** includes only candidates with 2+ reviewers; with zero such candidates the rate is `null`, not 0% or 100%. No real model accuracy or human-authenticated signatures are inferred.
- `identity_verified=false`, `independent_human_signoff=not_verified`, `automatic_acceptance=false`, `database_review_state_modified=false`. Never feed `self_attested_consensus_verdict` into production review states without a separate authenticated reviewer and explicit authorization workflow.

The historical eight `pallets/click` FakeProvider candidate audit is **not independent non-author human annotation**. Existing AI-assistant 7 reject / 1 uncertain observations are not imported as signatures. Real independent reviewer participation remains **not_run** until an actual person supplies and authenticates records through an appropriately controlled procedure. Signed enterprise verification and reviewer access control are future work.

Reference: [Phase A](2026-10-24-operator-public-snapshot-export.md), [Phase B](2026-10-24-upstream-capture-verification.md), and [implementation sequence](../plans/2026-10-24-evidence-verification-implementation-plan.md).
