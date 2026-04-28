## Why

Private repository token binding is already productized, but its operational edge cases are still too thin for a credible hosted preview. Users and operators need clearer failure categories, consistent access-source state, and stronger credential-safety guarantees before private-repo access can be treated as a stable v0.3 lane.

## What Changes

- Classify private repository access failures into actionable outcomes such as missing source, unauthorized or revoked source, repository not found, and provider/network failure.
- Make token-backed access-source label, authorization status, and authorization detail consistent across lookup, live analysis, workspace dashboard, readiness, and review-adjacent surfaces.
- Preserve the current security boundary: raw tokens are accepted only during admin setup and are never echoed in product results, logs, or reusable workspace summaries.
- Strengthen role and scope enforcement around private access setup so owner scope remains session-derived and non-admin users cannot submit credentials.
- Add operator documentation for recommended token permissions, rotation expectations, troubleshooting, and explicit non-goals.
- Add tests covering failure classification, no-token echo behavior, role gates, scope authority, and product rendering consistency.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `private-repo-access-and-credential-handling`: Clarify hardened authorization-state semantics and credential safety requirements.
- `private-repo-access-product-flow`: Require consistent product display, troubleshooting guidance, and no-token echo behavior across private access surfaces.
- `live-repository-analysis`: Require private-repository lookup/import failures to surface actionable access outcomes instead of generic errors.
- `imported-workspace-readiness-surface`: Require readiness summaries to preserve token-backed access-source status and detail without exposing credential material.
- `login-roles-and-workspace-scoping`: Reinforce private access setup as an admin-only, session-scoped action.
- `hosted-demo-operator-flow`: Document private access operational guidance and non-goals for hosted preview.

## Impact

- Engine import and lookup failure classification around GitHub token access sources.
- API proxy schemas and tests for private-access binding and live-analysis outcomes.
- Web live-analysis, workspace dashboard, imported readiness, and private access setup UI copy/tests.
- Operator documentation under `docs/project`.
- OpenSpec specs for private repository access, product flow, readiness, live analysis, role gates, and hosted operator guidance.
