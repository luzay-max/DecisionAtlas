## 1. Data Model And Extraction

- [x] 1.1 Add governance document and governance rule draft database models plus migration.
- [x] 1.2 Add repositories/services to import Markdown governance documents and extract deterministic rule drafts.
- [x] 1.3 Add tests for document metadata validation, deterministic draft extraction, and empty-document behavior.

## 2. Engine API

- [x] 2.1 Add engine API routes to create/list governance documents, list rule drafts, and accept/reject drafts.
- [x] 2.2 Enforce current owner-scope and role boundaries for governance ingest and review actions.
- [x] 2.3 Add API tests for import, list, accept, reject, and accepted-rule source traceability.

## 3. API Proxy And Web Product Surface

- [x] 3.1 Add API proxy routes and web client helpers for governance endpoints.
- [x] 3.2 Add a minimal `/governance` page for Markdown import, document listing, draft listing, and review actions.
- [x] 3.3 Add English and Chinese copy that explains accepted rules are not yet automatic CI blockers.
- [x] 3.4 Add web/API route tests for governance ingest and review flows.

## 4. Documentation And Validation

- [x] 4.1 Update project documentation and the master plan to record Stage 4 MVP boundaries.
- [x] 4.2 Run targeted engine/API/web tests for governance ingest.
- [x] 4.3 Run OpenSpec validation for the change and all specs.
- [x] 4.4 Run the practical project validation gate or document any environment-limited skip.
