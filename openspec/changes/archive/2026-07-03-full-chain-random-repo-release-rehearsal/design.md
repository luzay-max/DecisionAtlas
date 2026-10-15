## Context

DecisionAtlas has accumulated several evidence collectors:

- multi-repo live diagnosis for random real public GitHub repositories
- one-command release rehearsal
- external customer-host rehearsal v2
- browser-level self-hosted team rehearsal
- readiness evidence history

These are useful individually, but a release or customer handoff still needs a single top-level artifact that says which pieces were run together, which random repositories were selected, and which lanes are still non-clean.

## Goals / Non-Goals

**Goals:**

- Generate a full-chain JSON/Markdown bundle from explicit source artifacts.
- Support optional execution of random real repository diagnosis through the existing release rehearsal path.
- Preserve all non-pass states.
- Record browser rehearsal as a first-class lane.
- Archive full-chain output into readiness history when requested.

**Non-Goals:**

- Do not mutate customer infrastructure.
- Do not replace release rehearsal, customer-host v2, or multi-repo collectors.
- Do not claim real customer-host proof when only a template or local evidence was used.
- Do not add SaaS, billing, marketplace, or hosted multi-tenant functionality.

## Decisions

### Decision: Compose evidence instead of rerunning every lane internally

The full-chain collector reads explicit evidence files and can call the existing release rehearsal collector when requested. This avoids duplicating lane-specific logic.

### Decision: Browser evidence is a bounded lane

The collector records browser rehearsal command, status, and summary. It does not store traces or screenshots by default because those can contain local or customer-specific material.

### Decision: Archive as its own readiness-history entry

The full-chain bundle is archived separately from lower-level release/customer-host bundles, so operators can compare top-level release readiness over time.

## Risks / Trade-offs

- Running random live repo diagnosis depends on local stack and GitHub/network availability -> preserve provider/local-stack failure rather than fail silently.
- A full-chain bundle can become warning-heavy -> keep lane summaries compact and actionable.
- Browser evidence may be manually supplied -> mark it operator-guided unless an explicit passed status is provided.
