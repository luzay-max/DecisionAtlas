## 1. Repository Lookup

- [x] 1.1 Add an engine lookup path that resolves a repository into existing imported workspace state and latest import metadata.
- [x] 1.2 Proxy the lookup path through the API service so the web app can query it directly.

## 2. Reuse Controls

- [x] 2.1 Update the live analysis form to debounce repository lookup and surface existing-workspace actions.
- [x] 2.2 Add explicit actions for opening the existing workspace, syncing since the last successful import, and rerunning a full analysis.
- [x] 2.3 Disable duplicate rerun paths when the latest import is already queued or running.

## 3. Incremental Sync Safety

- [x] 3.1 Normalize `since_last_sync` timestamps before comparing them against GitHub timestamps.
- [x] 3.2 Add regression coverage for naive `since` datetimes so incremental sync no longer fails on timezone mismatches.

## 4. Validation

- [x] 4.1 Add engine/API tests for repository lookup responses.
- [x] 4.2 Add web tests for the existing-workspace and incremental-sync flow.
- [x] 4.3 Re-run the affected engine, API, and web test suites after the lookup and datetime fixes land.
