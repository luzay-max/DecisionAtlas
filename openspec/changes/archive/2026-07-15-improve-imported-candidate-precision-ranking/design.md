## Context

Candidate rows currently retain decision fields and confidence, while parser salvage, extraction family, and recovery path exist only as aggregate import counters. The review API calculates evidence quality one row at a time and the repository orders candidates by confidence, so it cannot explain extraction origin, detect semantic repetition, or place the strongest grounded representative first. The pip-tools baseline makes the cost visible: 28 review items were parser-salvaged and confidence-first ordering does not give a reviewer a reliable first screen.

The change spans extraction persistence, a backward-compatible migration, deterministic engine profiling, API serialization, and the imported review UI. Existing decisions, audit records, and accept/reject/supersede semantics must remain intact.

## Goals / Non-Goals

**Goals:**

- Preserve bounded extraction provenance for every newly created candidate.
- Produce a deterministic precision score, tier, explanations, and near-duplicate cluster for a workspace queue.
- Rank imported candidates evidence-first with stable results across repeated requests.
- Show reviewers why a candidate is strong, partial, weak, or a secondary cluster member.
- Keep legacy candidates usable when per-candidate extraction metadata is absent.

**Non-Goals:**

- Automatically accepting, rejecting, merging, or deleting candidates.
- Bulk review actions or precision-history reporting; those are separate follow-up changes.
- Embedding-based clustering, another model call, or raw provider-output storage.
- Rewriting historical aggregate import summaries to invent per-candidate provenance.

## Decisions

### Persist bounded candidate metadata in one nullable JSON column

Add `candidate_metadata_json` to `decisions`. New extraction writes `artifact_family`, `parser_salvaged`, `recovery`, and `sparse_recovery`. Existing rows remain `null` and are reported as `unknown` rather than being penalized as salvaged.

This is preferred over four nullable columns because the metadata is diagnostic, bounded, and likely to gain another extraction-path flag. It is preferred over reading the latest import summary because aggregate counters cannot be attributed safely to individual candidates.

### Build profiles in a dedicated candidate precision module

The engine will create an in-memory profile for each candidate from decision fields, source refs, primary artifact, and bounded metadata. A raw score combines source grounding, previewable evidence, provenance and URL availability, confidence, decision specificity, and artifact-family signal. Parser salvage and recovery are visible bounded penalties, not automatic rejection.

Tier boundaries are deterministic: `strong`, `partial`, and `weak`. Strong still requires grounded evidence and provenance; confidence alone cannot create a strong tier. Reasons are stable machine-readable codes.

This keeps ranking logic reusable by the later precision benchmark rather than burying it in API formatting or frontend sorting.

### Use deterministic lexical clustering before ranking

Near duplicates are clustered within one workspace using normalized tokens from title, problem, chosen option, and tradeoffs. Candidates join a cluster only when weighted token overlap passes a fixed threshold and decision-bearing title or chosen-option overlap is present. Generic stop words and very short tokens are excluded.

Each connected cluster receives a stable ID derived from its smallest decision ID. The highest raw-score member is the representative; stable ID breaks ties. Other members expose `duplicate_of`, remain in the response, and are ranked immediately after or below the representative according to tier. This preserves auditability and avoids model cost or non-repeatable embedding drift.

### Rank at the engine API boundary

For candidate queues, `GET /decisions` will load the evidence needed for the whole set, compute profiles and clusters, then order by tier, representative status, score, creation time, and ID. Non-candidate decision listings preserve their existing ordering. The response adds an optional `candidate_ranking` object and does not remove current `candidate_quality` or `review_evidence` fields.

Server-side ordering is preferred because API, UI, browser tests, and future evidence collectors must share one canonical result.

### Present tiers without hiding candidates

The review page will show a compact queue summary and tier/cluster badges on each imported card. Weak and secondary duplicate candidates remain visible and individually reviewable. The UI does not add a bulk-accept control or imply that a score is an approval decision.

## Risks / Trade-offs

- [Lexical similarity can miss paraphrases] -> Keep the threshold conservative, expose cluster reasons, and leave every item reviewable; later evidence can justify embeddings.
- [Lexical similarity can merge generic candidates] -> Require decision-bearing title or chosen-option overlap and test unrelated same-family candidates.
- [Legacy rows lack extraction metadata] -> Report `unknown` neutrally and never infer salvage from aggregate counters.
- [Pairwise clustering is quadratic] -> Normalize once, short-circuit by token overlap, and benchmark the expected queue size; add an indexed approach only if measured queues demand it.
- [Ranking changes reviewer-visible order] -> Stable tie-breakers and regression fixtures make the change explainable and repeatable.
- [JSON metadata can become unbounded] -> Write only an allowlisted schema and never provider prose or repository content.

## Migration Plan

1. Add nullable `candidate_metadata_json` through Alembic with no destructive backfill.
2. Deploy model and repository support while treating missing metadata as legacy/unknown.
3. Start writing metadata for newly extracted candidates.
4. Enable canonical profile calculation and API ordering.
5. Enable review UI explanations and validate against existing and newly imported workspaces.

Rollback can stop reading and writing the optional field while retaining it. A database downgrade removes only the new nullable diagnostic column; existing decision and source-ref data are unchanged.

## Open Questions

- The first real-repository comparison will determine whether the conservative lexical threshold should be adjusted in a later change.
- Batch rejection and candidate precision trend evidence remain explicitly deferred to the next two OpenSpec changes.
