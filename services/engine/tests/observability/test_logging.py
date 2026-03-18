from __future__ import annotations

import io
import json
import logging

from app.observability.logging import JsonFormatter, build_log_context


def test_json_formatter_includes_workspace_job_and_artifact_ids() -> None:
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JsonFormatter())
    logger = logging.getLogger("decisionatlas.test")
    logger.handlers = [handler]
    logger.setLevel(logging.INFO)
    logger.propagate = False

    logger.info("import completed", extra=build_log_context(workspace_id=7, job_id="job-123", artifact_id=42))

    payload = json.loads(stream.getvalue().strip())
    assert payload["message"] == "import completed"
    assert payload["workspace_id"] == 7
    assert payload["job_id"] == "job-123"
    assert payload["artifact_id"] == 42
