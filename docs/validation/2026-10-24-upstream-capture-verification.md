# Phase B: recorded public GitHub source verification (offline)

**Scope:** new Draft PR stacked on Phase A (PR #21). No production API change, paid model, network request inside verifier, human acceptance, or private data exports.

## Inputs

- A Phase-A operator-approved local public SQLite export JSON (one workspace, see [Phase-A instructions](2026-10-24-operator-public-snapshot-export.md)).
- An operator-reviewed public capture manifest with fixed source URLs, source content or PR metadata and capture date. The committed [example manifest](../../services/engine/tests/fixtures/upstream_evidence/pallets-click-public-captures.json) contains:
  - `pallets/click@2247b35ea1c47c727d7a06e51fa280e12a863ff6` `docs/contributing.md`, original complete public Markdown text and Git blob object SHA-1 `25a2426928a85fe087d49048350a7118b84d70dc`. Source: `raw.githubusercontent.com` pinned commit and GitHub commit tree.
  - [pallets/click#2559](https://github.com/pallets/click/pull/2559): `state=closed`, `merged=false`. Its API `merge_commit_sha` being present **must not** be mistaken for adoption.
  - [pallets/click#2562](https://github.com/pallets/click/pull/2562): `state=closed`, `merged=true`, `merged_at=2023-07-13T14:56:13Z`. Merging a PR is not proof that any candidate summary or selected option has been independently reviewed.
- The capture records were retrieved from the public GitHub endpoints on **2026-10-24**. PR state is mutable; a checked-in JSON fixture is only evidence of a **recorded capture** at the stated time, not a GitHub-signed origin certificate or continuous live status.

## Example (operator-approved local data only)

```sh
uv run --project services/engine python scripts/eval/verify_public_evidence.py \
  --snapshot /absolute/path/outside/repo/public-evidence.json \
  --manifest services/engine/tests/fixtures/upstream_evidence/pallets-click-public-captures.json \
  --output /absolute/path/outside/repo/capture-comparison.json \
  --approve-public-data
```

The CLI operates solely on disk. It requires explicit approval, an output file **outside Git checkout**, and exclusive creation (no overwrite). Exit code `0` means no source comparison failures; `1` means one or more captured-source discrepancies or known unmerged-PR negatives; `2` is invalid input/capture. Neither `0` nor a `pass`ed quote allows human acceptance. Do **not** copy real Phase-A exported artifacts to the public repository or upload to CI.

## What is actually checked

- A recorded Git blob capture must use a fixed 40-character commit SHA URL, a path consistent with the URL, and a content body matching the recorded **Git blob SHA-1 object ID**. SourceRef text/span is compared byte-for-byte (as Unicode text positions) with the recorded body, and stored Artifact content must match the capture. An invalid/missing capture fails or remains `not_evaluated`; there is no silent remote fetch or fabricated quote.
- Recorded PR metadata must match its numeric GitHub PR URL and repository. `merged=false` is **not adopted**; `merged=true` remains `review_required`. A missing captured source stays `not_evaluated`.
- Every result retains `automatic_acceptance=false`, `review_required=true`, `human_review=not_run` and `model_accuracy=not_evaluated`.

**Limitations:** Current capture records do not independently authenticate GitHub via a remote signature, do not prove semantic support, and do not perform human review; capturing different upstream content or refreshing mutable PR status requires a separately reviewed capture update. Real Phase-A candidate/reference exports from the original 8-candidate pilot are still not available. The paired #2559/#2562 fixtures are public-source observations and negative/contrast acceptance, **not** a real live-model accuracy baseline.
