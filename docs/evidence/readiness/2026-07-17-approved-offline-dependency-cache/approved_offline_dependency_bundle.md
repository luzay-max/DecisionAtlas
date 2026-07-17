# Offline Self-Hosted Install Rehearsal

- Status: `pass`
- Package: `0.4.0-offline-dependencies`
- Commit: `fa420c5`
- Proof level: `process_enforced_offline_install`
- Customer controlled: `false`

## Stages

| Stage | Status |
| --- | --- |
| Copy package and offline bundle into isolated root | `pass` |
| Verify copied package and offline dependency bundle | `pass` |
| Load and inspect bundled container images without registry pulls | `pass` |
| Install Node dependencies from bundled pnpm store | `pass` |
| Install Python dependencies from bundled uv cache | `pass` |
| Start Engine/API/Web and run local-only browser shell | `pass` |
| Run separately labelled live-network public repository core loop | `pass` |

## Boundaries

- Windows process-level offline controls are not proof of a physical air gap.
- Maintainer or CI rehearsal is not customer-controlled-host proof.
