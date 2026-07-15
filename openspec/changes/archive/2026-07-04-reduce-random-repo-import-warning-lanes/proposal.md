## Why

Random real repository rehearsals now run end-to-end, but their warning lanes mix product issues, operator-guided proof gaps, external dependency limits, and missing optional inputs. Release decisions need a smaller, actionable diagnosis layer that explains which warning lanes can be reduced by product work versus which must be disclosed or rerun.

## What Changes

- Add a warning-lane reduction evidence collector for random repository release rehearsals.
- Classify non-clean lanes from full-chain random repo, multi-repo diagnosis, release rehearsal, and external-host trial evidence into product-controlled, external dependency, operator-guided, not-provided, and blocking categories.
- Generate JSON and Markdown evidence with prioritized follow-up actions without hiding or downgrading source warning statuses.
- Add tests and documentation so the collector can become part of release rehearsal evidence.

## Capabilities

### New Capabilities
- `random-repo-warning-lane-reduction`: Explains and prioritizes warning lanes from random real repository release evidence.

### Modified Capabilities
- `full-chain-random-repo-release-rehearsal`: Full-chain random repository release evidence can be consumed as a source for warning-lane reduction.
- `release-rehearsal-one-command-evidence`: Release rehearsal evidence can be consumed as a source for warning-lane reduction.

## Impact

- New CI evidence script under `scripts/ci/`.
- New targeted tests under `services/engine/tests/ci/`.
- New generated smoke outputs under `.tmp/`.
- Documentation and OpenSpec specs updated to describe how to interpret warning-lane reduction output.
