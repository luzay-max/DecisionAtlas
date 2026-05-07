from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.db.models import GovernanceDocument, GovernanceRuleDraft
from app.repositories.governance import GovernanceRepository

DOCUMENT_TYPES = {
    "standard",
    "coding_guideline",
    "architecture_policy",
    "roadmap",
    "postmortem",
    "checklist",
    "decision_record",
    "anti_pattern",
    "release_policy",
    "security_policy",
}
DOCUMENT_STATUSES = {"active", "deprecated", "superseded", "experimental"}
RULE_SEVERITIES = {"blocker", "warning", "note"}
RULE_SCOPES = {"frontend", "api", "engine", "docs", "release", "security", "roadmap", "all"}
RULE_TYPES = {"standard", "postmortem_lesson", "decision_rule", "anti_pattern"}
LIFECYCLE_STATUSES = {"current", "stale", "superseded"}
REVIEW_RATIONALE_LIMIT = 1000


@dataclass(frozen=True)
class ExtractedRuleDraft:
    title: str
    description: str
    severity: str
    scope: str
    rationale: str | None
    source_excerpt: str
    rule_type: str
    extraction_reason: str


def import_governance_markdown(
    *,
    session: Session,
    owner_scope: str,
    title: str,
    document_type: str,
    content: str,
    scope: str = "all",
    status: str = "active",
    source_path: str | None = None,
) -> tuple[GovernanceDocument, list[GovernanceRuleDraft]]:
    normalized_type = _require_allowed(document_type, DOCUMENT_TYPES, "document_type")
    normalized_scope = _normalize_allowed(scope, RULE_SCOPES, default="all")
    normalized_status = _require_allowed(status, DOCUMENT_STATUSES, "status")
    normalized_title = title.strip()
    if not normalized_title:
        raise ValueError("Governance document title is required")
    if not content.strip():
        raise ValueError("Governance document content is required")

    repository = GovernanceRepository(session)
    document = repository.create_document(
        owner_scope=owner_scope,
        title=normalized_title,
        document_type=normalized_type,
        scope=normalized_scope,
        status=normalized_status,
        source_path=source_path.strip() if source_path else None,
        content_hash=hashlib.sha256(content.encode("utf-8")).hexdigest(),
        content=content,
        metadata_json={"extractor": "deterministic_markdown_v1"},
    )
    drafts = [
        repository.create_rule_draft(
            owner_scope=owner_scope,
            document_id=document.id,
            title=draft.title,
            description=draft.description,
            severity=draft.severity,
            scope=draft.scope,
            rationale=draft.rationale,
            source_excerpt=draft.source_excerpt,
            rule_type=draft.rule_type,
            extraction_reason=draft.extraction_reason,
        )
        for draft in extract_rule_drafts(content, default_scope=normalized_scope, document_type=normalized_type)
    ]
    return document, drafts


def extract_rule_drafts(content: str, *, default_scope: str = "all", document_type: str = "standard") -> list[ExtractedRuleDraft]:
    sections = _markdown_sections(content)
    drafts: list[ExtractedRuleDraft] = []
    normalized_document_type = _normalize_document_type(document_type)
    for title, body in sections:
        signal = _rule_signal(title, body, document_type=normalized_document_type)
        if signal is None:
            continue
        severity = _extract_marker(body, "severity")
        scope = _extract_marker(body, "scope")
        rationale = _extract_marker(body, "rationale")
        description = _description_from_body(body)
        if not description:
            continue
        drafts.append(
            ExtractedRuleDraft(
                title=title[:255],
                description=description,
                severity=_normalize_allowed(severity, RULE_SEVERITIES, default="warning"),
                scope=_normalize_allowed(scope or default_scope, RULE_SCOPES, default="all"),
                rationale=rationale,
                source_excerpt=_source_excerpt(title, body),
                rule_type=_rule_type_for_signal(normalized_document_type, title, body),
                extraction_reason=signal,
            )
        )
    return drafts


def review_rule_draft(
    *,
    session: Session,
    owner_scope: str,
    draft_id: int,
    review_state: str,
    reviewer: str,
    review_rationale: str | None = None,
) -> GovernanceRuleDraft:
    if review_state not in {"accepted", "rejected"}:
        raise ValueError("review_state must be accepted or rejected")
    repository = GovernanceRepository(session)
    draft = repository.get_rule_draft(owner_scope=owner_scope, draft_id=draft_id)
    if draft is None:
        raise ValueError(f"Governance rule draft not found: {draft_id}")
    status = "active" if review_state == "accepted" else "rejected"
    return repository.review_rule_draft(
        draft,
        review_state=review_state,
        status=status,
        reviewed_by=reviewer,
        reviewed_at=datetime.now(UTC),
        review_rationale=_bounded_optional_text(review_rationale, REVIEW_RATIONALE_LIMIT),
    )


def serialize_document(document: GovernanceDocument) -> dict:
    return {
        "id": document.id,
        "owner_scope": document.owner_scope,
        "title": document.title,
        "document_type": document.document_type,
        "scope": document.scope,
        "status": document.status,
        "source_path": document.source_path,
        "content_hash": document.content_hash,
        "created_at": document.created_at.isoformat() if document.created_at else None,
    }


def serialize_rule_draft(draft: GovernanceRuleDraft, *, source_title: str | None = None) -> dict:
    return {
        "id": draft.id,
        "owner_scope": draft.owner_scope,
        "document_id": draft.document_id,
        "source_title": source_title,
        "title": draft.title,
        "description": draft.description,
        "severity": draft.severity,
        "scope": draft.scope,
        "rationale": draft.rationale,
        "source_excerpt": draft.source_excerpt,
        "rule_type": draft.rule_type,
        "extraction_reason": draft.extraction_reason,
        "review_state": draft.review_state,
        "status": draft.status,
        "review_rationale": draft.review_rationale,
        "lifecycle_status": draft.lifecycle_status,
        "superseded_by_rule_id": draft.superseded_by_rule_id,
        "reviewed_by": draft.reviewed_by,
        "reviewed_at": draft.reviewed_at.isoformat() if draft.reviewed_at else None,
    }


def _markdown_sections(content: str) -> list[tuple[str, str]]:
    sections: list[tuple[str, list[str]]] = []
    current_title: str | None = None
    current_body: list[str] = []
    for raw_line in content.splitlines():
        heading = re.match(r"^\s{0,3}#{1,4}\s+(.+?)\s*$", raw_line)
        if heading:
            if current_title is not None:
                sections.append((current_title, current_body))
            current_title = heading.group(1).strip()
            current_body = []
        elif current_title is not None:
            current_body.append(raw_line.rstrip())
    if current_title is not None:
        sections.append((current_title, current_body))
    return [(title, "\n".join(body).strip()) for title, body in sections]


def _looks_like_rule(title: str, body: str) -> bool:
    return _rule_signal(title, body, document_type="standard") is not None


def _rule_signal(title: str, body: str, *, document_type: str) -> str | None:
    value = f"{title}\n{body}".lower()
    title_value = title.strip().lower()
    if title_value.startswith("rule:") or "rule:" in value:
        return "rule heading marker"
    if _extract_marker(body, "severity") or _extract_marker(body, "scope"):
        return "bounded severity or scope marker"
    if document_type == "postmortem" and any(marker in value for marker in ("lesson", "follow-up", "action item", "复盘", "教训")):
        return "postmortem lesson marker"
    if document_type == "decision_record" and any(marker in value for marker in ("decision", "decided", "chosen", "must", "shall", "决策", "决定")):
        return "decision outcome marker"
    if document_type == "anti_pattern" and any(marker in value for marker in ("anti-pattern", "do not", "never", "禁止", "不得")):
        return "anti-pattern prohibition marker"
    if document_type == "checklist" and re.search(r"(?m)^\s*[-*]\s+\S", body) and _contains_normative_language(value):
        return "checklist command marker"
    return None


def _rule_type_for_signal(document_type: str, title: str, body: str) -> str:
    value = f"{title}\n{body}".lower()
    if document_type == "postmortem":
        return "postmortem_lesson"
    if document_type == "decision_record":
        return "decision_rule"
    if document_type == "anti_pattern" or any(marker in value for marker in ("anti-pattern", "do not", "never", "禁止", "不得")):
        return "anti_pattern"
    return "standard"


def _extract_marker(body: str, name: str) -> str | None:
    match = re.search(rf"(?im)^\s*[-*]?\s*{re.escape(name)}\s*:\s*(.+?)\s*$", body)
    return match.group(1).strip() if match else None


def _description_from_body(body: str) -> str:
    lines: list[str] = []
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if re.match(r"(?i)^[-*]?\s*(severity|scope|rationale)\s*:", stripped):
            continue
        lines.append(stripped.lstrip("-* ").strip())
    return " ".join(lines)[:1200]


def _source_excerpt(title: str, body: str) -> str:
    excerpt = f"## {title}\n{body}".strip()
    return excerpt[:2000]


def _require_allowed(value: str, allowed: set[str], field: str) -> str:
    normalized = value.strip().lower()
    if normalized not in allowed:
        raise ValueError(f"Unsupported {field}: {value}")
    return normalized


def _normalize_allowed(value: str | None, allowed: set[str], *, default: str) -> str:
    if not value:
        return default
    normalized = value.strip().lower()
    return normalized if normalized in allowed else default


def _normalize_document_type(value: str) -> str:
    normalized = value.strip().lower()
    return normalized if normalized in DOCUMENT_TYPES else "standard"


def _contains_normative_language(value: str) -> bool:
    return any(marker in value for marker in ("must", "shall", "required", "禁止", "必须", "不得"))


def _bounded_optional_text(value: str | None, limit: int) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped[:limit] if stripped else None
