from __future__ import annotations

import json
import logging
from typing import Any


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for field in ("workspace_id", "job_id", "artifact_id"):
            value = getattr(record, field, None)
            if value is not None:
                payload[field] = value
        return json.dumps(payload, ensure_ascii=True)


def build_log_context(
    *,
    workspace_id: int | None = None,
    job_id: str | None = None,
    artifact_id: int | None = None,
) -> dict[str, int | str]:
    context: dict[str, int | str] = {}
    if workspace_id is not None:
        context["workspace_id"] = workspace_id
    if job_id is not None:
        context["job_id"] = job_id
    if artifact_id is not None:
        context["artifact_id"] = artifact_id
    return context


def get_logger(name: str = "decisionatlas.engine") -> logging.Logger:
    return logging.getLogger(name)
