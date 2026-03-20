## 1. Remote document ingest foundation

- [x] 1.1 Extend the GitHub client with repository file discovery and markdown content fetch helpers for high-signal paths.
- [x] 1.2 Add a repository document selection layer that includes the approved high-signal markdown files and records skip categories for excluded files.
- [x] 1.3 Reuse the existing `doc` artifact model to upsert remote repository documents with stable repo-relative `source_id` values and GitHub blob URLs.

## 2. Import transparency and real-workspace feedback

- [x] 2.1 Extend import job summaries and related APIs to report repository document counts and skip-reason totals alongside existing issue/PR/commit counts.
- [x] 2.2 Update real-workspace dashboard and related empty states so sparse decision output is explained as limited evidence rather than import failure.
- [x] 2.3 Keep reruns idempotent and ensure mixed imports of classic GitHub artifacts plus repository docs do not duplicate stored artifacts.

## 3. Validation

- [x] 3.1 Add engine ingest tests for remote document selection, document import persistence, and import summary skip reasons.
- [x] 3.2 Add or update API and web tests for import summaries and real-workspace low-signal messaging.
- [x] 3.3 Run affected engine, API, and web validation and update progress tracking once the change is implemented.
