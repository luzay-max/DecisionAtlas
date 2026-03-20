## Why

DecisionAtlas can already import and analyze a curated public repository, but the current product still behaves more like a guided demo than a trustworthy live-analysis tool. To prove real capability, the product needs a user-driven path for analyzing arbitrary public GitHub repositories, plus clearer stage visibility and honest failure reporting when providers fail or repository evidence is thin.

## What Changes

- Add a live-analysis flow where a user can submit a public GitHub repository reference and trigger a real analysis run against that repository.
- Create or reuse imported workspaces per analyzed repository so live runs do not mix with the guided demo workspace.
- Extend import job visibility beyond a single `running` state to show analysis stages such as import, indexing, extraction, completion, and failure.
- Surface explicit live-analysis failure reasons and insufficient-evidence messaging so real runs fail transparently instead of looking broken.
- Add a small benchmark set of public repositories and validation expectations to prove the live-analysis path works outside the fixed demo repository.

## Capabilities

### New Capabilities
- `live-repository-analysis`: Allow users to submit a public GitHub repository for one-off live analysis with workspace creation, staged progress, and transparent outcomes.

### Modified Capabilities
- `repository-document-ingest`: Extend real-repository import reporting to include staged progress and clearer failure versus thin-evidence outcomes.

## Impact

- Affected engine import job execution, workspace creation, and job status APIs in `services/engine`
- Affected API proxy routes and web UX for starting live analysis and displaying staged progress
- Affected benchmark fixtures, smoke validation, and public demo documentation
