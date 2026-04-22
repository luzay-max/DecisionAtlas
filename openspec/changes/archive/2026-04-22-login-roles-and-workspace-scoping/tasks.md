## 1. Identity and Membership Foundations

- [x] 1.1 Choose and implement the first-release auth shape: local application accounts plus server-side session cookie.
- [x] 1.2 Add owner-scope membership and role persistence for `viewer`, `reviewer`, and `admin`.
- [x] 1.3 Add request-context resolution for authenticated actor plus session-carried current owner scope.

## 2. Authorization and Product Flows

- [x] 2.1 Enforce role checks on imported-workspace actions: import, rerun, incremental sync, review, accept/reject, and drift evaluation.
- [x] 2.2 Scope dashboard, search, live-analysis lookup, and workspace reads to the authenticated actor's current owner scope resolved from session state.
- [x] 2.3 Preserve webhook/background execution as trusted system-action paths while adding honest unauthorized/forbidden product outcomes without leaking cross-scope workspace existence.

## 3. Validation and Migration

- [x] 3.1 Backfill a bootstrap local actor, owner scope, and admin membership for current single-user data.
- [x] 3.2 Add regression coverage for session resolution, scope membership, role enforcement, and trusted system-action execution.
- [x] 3.3 Validate that the bootstrap local flow plus current GitHub App and private-repo owner-scoped flows remain correct under authenticated scope resolution.
