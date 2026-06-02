## Context

Import jobs for large repositories take minutes to process. Users currently have no way to pause these background extractions midway.

## Goals / Non-Goals

**Goals:**
- Implement state-aware logic in the import job processor to respect `paused` status in the DB.
- Provide simple `/imports/{id}/pause` and `resume` API endpoints.
- Provide frontend buttons.

**Non-Goals:**
- Do not persist pause state across server restarts for running HTTP connections (currently relying on simple `time.sleep` while in the generator).
- Do not provide a global task manager for all jobs.

## Decisions

- **Checking DB State Continuously**: The import job's extraction phase runs in a tight loop and issues API requests. By injecting a check `job.status == 'paused'` periodically during the GitHub and LLM extraction phases, we can stall execution via `time.sleep` until it changes back to `running`.
- **Frontend Long-Polling Support**: The frontend polling `waitForJob` was designed to assume standard running behavior. We inject a `paused` check to skip the timeout threshold, allowing indefinite waiting while the job is paused.

## Risks / Trade-offs

- **Risk**: Connection timeouts during a long pause.
  - **Mitigation**: The extraction loops are highly compartmentalized. The sleep does not hold open external network calls (they are yielded back).
- **Risk**: User closes browser during a pause.
  - **Mitigation**: The backend job thread sleeps in memory. The process will still exist and resume perfectly when the API is hit again.
