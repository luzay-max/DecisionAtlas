## Why

The project now has separate evidence lanes for random real repositories, release rehearsal, customer-host v2, and browser self-hosted flow. The remaining gap is a single full-chain rehearsal evidence entry that proves those lanes were run together and preserves their mixed outcomes.

## What Changes

- Add a full-chain random repository release rehearsal collector.
- Include selected real GitHub repository IDs, release rehearsal evidence, customer-host v2 evidence, and browser rehearsal evidence in one JSON/Markdown bundle.
- Preserve warnings, operator-guided states, local-stack failures, and customer-host template limitations.
- Archive the full-chain bundle into readiness history when requested.
- Update taskbook and update log so this becomes the current handoff-level evidence checkpoint.

## Capabilities

### New Capabilities
- `full-chain-random-repo-release-rehearsal`: one-command full-chain evidence bundle across random real GitHub repos, release readiness, customer-host v2, and browser rehearsal.

### Modified Capabilities
- `release-rehearsal-one-command-evidence`: release rehearsal can be used as a source lane for full-chain evidence.
- `multi-repo-live-diagnosis-rotation`: random real repository diagnosis can feed full-chain rehearsal evidence.
- `external-customer-host-rehearsal-v2`: customer-host v2 evidence can feed full-chain rehearsal evidence.
- `project-completion-taskbook`: taskbook reflects full-chain random repo release rehearsal progress and remaining true external proof boundary.

## Impact

- Adds one CI/operator script under `scripts/ci/`.
- Adds targeted pytest coverage under `services/engine/tests/ci/`.
- Adds project documentation and durable readiness evidence.
- No database or runtime API changes.
