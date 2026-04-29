from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import GovernanceDocument, GovernanceRuleDraft


class GovernanceRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_document(
        self,
        *,
        owner_scope: str,
        title: str,
        document_type: str,
        scope: str,
        status: str,
        source_path: str | None,
        content_hash: str,
        content: str,
        metadata_json: dict | None,
    ) -> GovernanceDocument:
        document = GovernanceDocument(
            owner_scope=owner_scope,
            title=title,
            document_type=document_type,
            scope=scope,
            status=status,
            source_path=source_path,
            content_hash=content_hash,
            content=content,
            metadata_json=metadata_json,
        )
        self.session.add(document)
        self.session.flush()
        return document

    def list_documents(self, *, owner_scope: str) -> list[GovernanceDocument]:
        stmt = (
            select(GovernanceDocument)
            .where(GovernanceDocument.owner_scope == owner_scope)
            .order_by(GovernanceDocument.created_at.desc(), GovernanceDocument.id.desc())
        )
        return list(self.session.scalars(stmt))

    def get_document(self, *, owner_scope: str, document_id: int) -> GovernanceDocument | None:
        stmt = select(GovernanceDocument).where(
            GovernanceDocument.owner_scope == owner_scope,
            GovernanceDocument.id == document_id,
        )
        return self.session.scalar(stmt)

    def create_rule_draft(
        self,
        *,
        owner_scope: str,
        document_id: int,
        title: str,
        description: str,
        severity: str,
        scope: str,
        rationale: str | None,
        source_excerpt: str,
    ) -> GovernanceRuleDraft:
        draft = GovernanceRuleDraft(
            owner_scope=owner_scope,
            document_id=document_id,
            title=title,
            description=description,
            severity=severity,
            scope=scope,
            rationale=rationale,
            source_excerpt=source_excerpt,
            review_state="pending",
            status="draft",
        )
        self.session.add(draft)
        self.session.flush()
        return draft

    def list_rule_drafts(self, *, owner_scope: str, review_state: str | None = None) -> list[GovernanceRuleDraft]:
        stmt = select(GovernanceRuleDraft).where(GovernanceRuleDraft.owner_scope == owner_scope)
        if review_state:
            stmt = stmt.where(GovernanceRuleDraft.review_state == review_state)
        stmt = stmt.order_by(GovernanceRuleDraft.created_at.desc(), GovernanceRuleDraft.id.desc())
        return list(self.session.scalars(stmt))

    def get_rule_draft(self, *, owner_scope: str, draft_id: int) -> GovernanceRuleDraft | None:
        stmt = select(GovernanceRuleDraft).where(
            GovernanceRuleDraft.owner_scope == owner_scope,
            GovernanceRuleDraft.id == draft_id,
        )
        return self.session.scalar(stmt)

    def review_rule_draft(
        self,
        draft: GovernanceRuleDraft,
        *,
        review_state: str,
        status: str,
        reviewed_by: str,
        reviewed_at: datetime,
    ) -> GovernanceRuleDraft:
        draft.review_state = review_state
        draft.status = status
        draft.reviewed_by = reviewed_by
        draft.reviewed_at = reviewed_at
        self.session.flush()
        return draft
