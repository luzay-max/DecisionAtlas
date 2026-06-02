## 1. Backend Implementation

- [x] 1.1 Add mark_paused and mark_resumed methods to `ImportJobRepository`
- [x] 1.2 Add `/imports/{job_id}/pause` and `resume` API endpoints in `imports.py`
- [x] 1.3 Add sleep loop inside `on_progress` to respect paused status
- [x] 1.4 Add sleep loop inside `_build_extraction_progress_reporter` to pause LLM extraction

## 2. Frontend Implementation

- [x] 2.1 Expose `pauseGithubImport` and `resumeGithubImport` in `api.ts`
- [x] 2.2 Update `demo-import-button.tsx` polling logic `waitForJob` to handle paused state indefinitely
- [x] 2.3 Add "Pause" and "Resume" buttons to the UI
- [x] 2.4 Show failure category details directly in UI components
