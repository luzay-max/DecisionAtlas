## 1. Current Surface Audit

- [x] 1.1 Audit current engine/API payloads for `access_source_type`, `access_source_label`, `latest_import`, `sync_origin`, `trigger_event`, `latest_sync_origin`, and `active_sync_origin`.
- [x] 1.2 Audit current web rendering in live analysis, workspace dashboard, imported readiness, and GitHub App installation panel for sync provenance gaps.
- [x] 1.3 Identify whether existing data supports a compact recent/latest sync summary without adding a new job-history data model.

## 2. Product UI and API Contract

- [x] 2.1 Normalize product-facing sync origin labels for manual full, manual incremental, installation-backed full, installation-backed incremental, private-source sync, and webhook-triggered sync.
- [x] 2.2 Ensure installation-backed lookup and import surfaces show the GitHub App access-source label before open, rerun, or incremental sync actions.
- [x] 2.3 Ensure workspace dashboard shows access-source label plus latest or active sync provenance clearly enough to distinguish webhook from manual sync.
- [x] 2.4 Add a bounded latest/recent sync summary where current API data supports it, without introducing a broad operations console.
- [x] 2.5 Keep the successful installation binding result connected to the workspace identity and explain where post-binding sync state is visible.

## 3. Webhook Operator Documentation

- [x] 3.1 Add or update GitHub App webhook operator documentation with endpoint, expected events, secret/signature boundary, and validation steps.
- [x] 3.2 Document troubleshooting cases for unresolved repository, missing installation binding, invalid webhook headers/signature, duplicate active sync, and provider/network failure.
- [x] 3.3 Update release-facing or hosted operator docs only where needed to distinguish operator-guided webhook validation from default release validation.

## 4. Tests

- [x] 4.1 Add or update engine/API tests for installation-backed lookup, webhook-triggered sync provenance, and duplicate active sync behavior.
- [x] 4.2 Add or update web tests for dashboard sync provenance rendering, webhook origin labels, and installation-backed lookup controls.
- [x] 4.3 Add or update GitHub App installation panel tests so binding results point users toward workspace sync state without exposing unsupported OAuth/Marketplace behavior.
- [x] 4.4 Run targeted API, engine, and web tests covering GitHub App sync operations.

## 5. Final Validation

- [x] 5.1 Run the relevant typechecks for changed packages.
- [x] 5.2 Run OpenSpec validation for this change.
- [x] 5.3 Record any deferred work for private repo hardening, full OAuth/Marketplace setup, or hosted live webhook verification without implementing it in this change.
