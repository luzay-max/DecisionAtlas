# Real Repository Decision Quality Report

Date: 2026-04-29
Scope: v0.3 phase six, `improve-real-repo-decision-signal-quality`

## Purpose

This report records how real-repository validation should judge imported candidate value, not only import readiness. The current implementation keeps quality assessment bounded to existing observable data: source-reference count, previewable quotes, artifact provenance, source URL availability, and confidence bucket.

## Candidate Quality Model

- Strong candidate: multiple source refs, at least one previewable quote, artifact provenance, source URL availability, and non-low confidence.
- Partial candidate: at least one source ref plus previewable evidence, artifact provenance, or source URL support, but missing enough support to treat as a strong first-baseline candidate.
- Thin candidate: missing source refs or only weak grounding/provenance. These stay visible in review as diagnostics and are not silently filtered.

Confidence remains context only. A high-confidence candidate with missing source refs, missing previewable quotes, missing provenance, or missing source URL support must not be promoted to `strong`.

The bounded reason vocabulary currently includes:

- source-ref support: `multiple_source_refs`, `single_source_ref`, `missing_source_refs`.
- quote support: `previewable_quote`, `missing_previewable_quote`.
- provenance support: `artifact_provenance`, `missing_artifact_provenance`.
- source URL support: `source_url_available`, `missing_source_url`.
- confidence context: `high_confidence`, `medium_confidence`, `low_confidence`.

## Curated Repository Expectations

The offline fixture set now carries `candidate_quality` expectations for each curated real repository:

- `minimum_strong_candidates`: protects that high-signal repositories should produce at least some strong review candidates.
- `maximum_thin_candidate_ratio`: records acceptable thin-candidate pressure without depending on exact generated prose.
- `require_provenance`: distinguishes repos where source artifact provenance is expected from stress cases where evidence may remain sparse.

## Live Report Shape

When `python scripts/ci/run_benchmark.py --live-real-repos` is run against an existing stack, each repository row includes `candidate_quality` with:

- candidate counts by quality label.
- strong and thin candidate counts.
- thin-candidate ratio.
- total source refs and previewable source refs.
- provenance gap count.
- source URL gap count.
- confidence bucket distribution.
- bounded reason counts.
- pass/fail checks against fixture expectations.

Live quality observation remains outside default CI because it depends on existing imported workspaces, repository availability, and provider output. Default CI still validates the deterministic fixture shape.

## Current Follow-Up Risks

- The quality label is intentionally heuristic. It should be recalibrated after several real imports are reviewed by a human.
- Thin candidates are labeled rather than removed. If reviewers repeatedly reject the same thin patterns, the extraction prompt and conversion filters should be tightened in a later change.
- Confidence is only contextual. It must not override weak source refs, missing provenance, or missing source URL support.
- Why/drift guidance should remain bounded to accepted decisions with matching grounded evidence, especially when the first accepted baseline was only partial or thin.
