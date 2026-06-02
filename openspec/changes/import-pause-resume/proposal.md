## Why

Importing large repositories takes a long time, often spanning several minutes or more. Users need the ability to pause the import process midway and resume it later, avoiding total progress loss or server overload when they wish to halt extraction temporarily.

## What Changes

- Added `POST /imports/{job_id}/pause` and `POST /imports/{job_id}/resume` endpoints.
- Modified the import extraction loop in `import_jobs.py` to check for `paused` status and hang in a sleep loop.
- Added 'Pause' and 'Resume' buttons to the `demo-import-button.tsx` in the frontend dashboard.
- Display `Failure Category` detailed messages in the frontend to make error tracking easier.

## Capabilities

### New Capabilities
- `import-pause-resume`: Pause and resume long-running import jobs.

### Modified Capabilities

## Impact

Affects the `import_jobs.py` core extraction loop, `imports.py` router, and `demo-import-button.tsx` frontend component. Does not change existing decision extraction models.
