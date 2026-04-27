## 1. Installation Binding Client

- [x] 1.1 Add a web API client function and types for `/imports/github/installations/bind`.
- [x] 1.2 Preserve existing API proxy auth/session behavior for installation binding and add coverage if needed.

## 2. Product UI

- [x] 2.1 Add an admin-only GitHub App installation binding panel that shows current owner scope and accepts repo, installation id, and optional account metadata.
- [x] 2.2 Integrate the panel into the live analysis/admin controls flow without exposing owner-scope override fields.
- [x] 2.3 Show successful binding result with workspace slug, access-source label, and next actions.
- [x] 2.4 Keep reviewer/viewer users from mutating installation binding while allowing them to see existing workspace access-source state.

## 3. Installation-Backed State

- [x] 3.1 Ensure live analysis lookup and existing workspace controls clearly label GitHub App installation-backed reuse.
- [x] 3.2 Ensure workspace dashboard/readiness surfaces continue to show installation-backed source and webhook/manual sync provenance.
- [x] 3.3 Preserve public import, local bootstrap, and hosted demo smoke behavior.

## 4. Tests And Validation

- [x] 4.1 Add web tests for installation binding success, validation failure, admin-only controls, and installation-backed reuse labels.
- [x] 4.2 Run targeted API/web tests for GitHub App binding and live analysis flows.
- [x] 4.3 Run the canonical pre-release validation.
