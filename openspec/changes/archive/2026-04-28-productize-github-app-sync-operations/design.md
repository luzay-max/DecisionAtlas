## Context

DecisionAtlas already has the lower-level GitHub App pieces: installation-backed access sources, webhook ingestion, incremental sync enqueueing, `sync_origin` metadata, and some dashboard/readiness rendering. The remaining gap is product coherence: users and operators need a reliable way to understand whether a workspace is GitHub App-backed, what triggered the latest or active sync, and how to validate or troubleshoot webhook delivery.

This change should productize the operational surface without turning it into a full GitHub Marketplace/OAuth installation project.

## Goals / Non-Goals

**Goals:**

- Make GitHub App-backed workspace state and sync provenance visible on the main workspace/import surfaces.
- Present sync origin with user-readable labels for manual full import, manual incremental sync, webhook-triggered sync, and installation-backed sync variants.
- Surface enough recent/latest sync metadata to explain current freshness without building a full job console.
- Document webhook setup, validation, and troubleshooting for operators.
- Add focused tests for lookup, dashboard/readiness rendering, webhook origin labels, and API/engine provenance behavior.

**Non-Goals:**

- Do not implement full GitHub OAuth or Marketplace self-service installation.
- Do not introduce a complex sync job management console.
- Do not require live GitHub App credentials in default CI.
- Do not redesign the import pipeline or webhook queueing model.
- Do not expand private repository access hardening in this change.

## Decisions

1. Use existing import/job metadata as the product contract.

   The current model already carries `access_source_type`, `access_source_label`, `latest_import`, `sync_origin`, `trigger_event`, `latest_sync_origin`, and `active_sync_origin`. This change should first make those fields consistently visible and tested before adding new storage.

2. Prefer a compact latest/recent sync summary over a full operations console.

   Users need to answer whether the workspace is App-backed and what triggered the latest sync. A full job history UI would add scope and maintenance cost; a bounded latest/recent summary is enough for stage 3.

3. Keep webhook validation operator-guided.

   CI can validate webhook API behavior through tests and fixtures. Real webhook delivery depends on external GitHub App configuration and should remain an operator checklist until hosted preview has stable credentials.

4. Preserve release-gate determinism.

   New tests should cover rendering and API contracts with fixtures. Live webhook delivery should not be added to `pre-release.ps1`.

## Risks / Trade-offs

- Existing fields may be inconsistently populated across surfaces -> normalize display helpers and add regression tests.
- Sync labels can become confusing across public, installation-backed, and private sources -> keep one label map and use it in dashboard/imported readiness surfaces.
- Webhook documentation can overpromise live automation -> explicitly mark production GitHub App setup as operator-managed and not Marketplace/OAuth self-service.
- Recent sync history may require more data than currently exposed -> fall back to latest/active sync summary if a true history endpoint would expand scope.
