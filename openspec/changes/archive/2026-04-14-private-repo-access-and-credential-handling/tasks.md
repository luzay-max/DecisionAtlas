## 1. Access-Source and Credential Foundations

- [x] 1.1 Add owner-scoped credential-bearing access-source persistence for private repositories without storing raw credential material on workspaces.
- [x] 1.2 Define access-source status and repository authorization checks so private imports can distinguish authorized, missing, and invalid source states.
- [x] 1.3 Preserve the public-repository baseline so public/manual and installation-backed flows continue to work when no private source is required.

## 2. Private Import and Reuse Flows

- [x] 2.1 Update live-analysis and import entry points to resolve private repositories through an authorized owner-scoped access source before job creation.
- [x] 2.2 Update repository lookup, workspace reuse, and incremental sync to keep private workspaces bound to their original authorized source unless explicitly re-bound.
- [x] 2.3 Add honest product-facing outcome states for credential-required and authorization-failed private repository requests.

## 3. Validation and Product Surfaces

- [x] 3.1 Add regression coverage for private access-source resolution, private workspace reuse, and authorization-specific failure classes.
- [x] 3.2 Update dashboard/search or other imported-workspace surfaces to describe private-access setup and bound-source state clearly without exposing secret material.
- [x] 3.3 Validate that public-repo baselines, lightweight benchmarks, and current GitHub App incremental sync behavior still hold after private-access support lands.
