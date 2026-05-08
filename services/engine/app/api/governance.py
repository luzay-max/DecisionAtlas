from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.auth import AuthContext, require_actor, require_scope_role
from app.db.session import get_db_session
from app.governance.markdown_ingest import (
    import_governance_markdown,
    review_rule_draft,
    serialize_document,
    serialize_rule_draft,
    update_rule_lifecycle,
)
from app.repositories.governance import GovernanceRepository

router = APIRouter(prefix="/governance", tags=["governance"])


class GovernanceDocumentImportRequest(BaseModel):
    title: str
    document_type: str
    content: str
    scope: str = "all"
    status: str = "active"
    source_path: str | None = None


class GovernanceRuleReviewRequest(BaseModel):
    review_state: str
    review_rationale: str | None = None


class GovernanceRuleLifecycleRequest(BaseModel):
    lifecycle_status: str
    lifecycle_rationale: str | None = None
    superseded_by_rule_id: int | None = None


@router.post("/documents")
def create_governance_document(
    request: GovernanceDocumentImportRequest,
    auth: AuthContext = Depends(require_actor),
) -> dict:
    require_scope_role(auth, owner_scope=auth.owner_scope, required_role="admin")
    session = get_db_session()
    try:
        document, drafts = import_governance_markdown(
            session=session,
            owner_scope=auth.owner_scope,
            title=request.title,
            document_type=request.document_type,
            content=request.content,
            scope=request.scope,
            status=request.status,
            source_path=request.source_path,
        )
        session.commit()
        return {
            "document": serialize_document(document),
            "drafts": [serialize_rule_draft(draft, source_title=document.title) for draft in drafts],
        }
    except ValueError as exc:
        session.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        session.close()


@router.get("/documents")
def list_governance_documents(auth: AuthContext = Depends(require_actor)) -> dict:
    require_scope_role(auth, owner_scope=auth.owner_scope, required_role="viewer")
    session = get_db_session()
    try:
        documents = GovernanceRepository(session).list_documents(owner_scope=auth.owner_scope)
        return {"documents": [serialize_document(document) for document in documents]}
    finally:
        session.close()


@router.get("/rules")
def list_governance_rules(
    review_state: str | None = Query(default=None),
    auth: AuthContext = Depends(require_actor),
) -> dict:
    require_scope_role(auth, owner_scope=auth.owner_scope, required_role="viewer")
    session = get_db_session()
    try:
        repository = GovernanceRepository(session)
        drafts = repository.list_rule_drafts(owner_scope=auth.owner_scope, review_state=review_state)
        documents = {
            document.id: document
            for document in repository.list_documents(owner_scope=auth.owner_scope)
        }
        return {
            "rules": [
                serialize_rule_draft(
                    draft,
                    source_title=documents.get(draft.document_id).title if documents.get(draft.document_id) else None,
                )
                for draft in drafts
            ]
        }
    finally:
        session.close()


@router.post("/rules/{draft_id}/review")
def review_governance_rule(
    draft_id: int,
    request: GovernanceRuleReviewRequest,
    auth: AuthContext = Depends(require_actor),
) -> dict:
    require_scope_role(auth, owner_scope=auth.owner_scope, required_role="reviewer")
    session = get_db_session()
    try:
        draft = review_rule_draft(
            session=session,
            owner_scope=auth.owner_scope,
            draft_id=draft_id,
            review_state=request.review_state,
            reviewer=auth.username,
            review_rationale=request.review_rationale,
        )
        document = GovernanceRepository(session).get_document(owner_scope=auth.owner_scope, document_id=draft.document_id)
        session.commit()
        return {"rule": serialize_rule_draft(draft, source_title=document.title if document else None)}
    except ValueError as exc:
        session.rollback()
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise HTTPException(status_code=status_code, detail=message) from exc
    finally:
        session.close()


@router.post("/rules/{draft_id}/lifecycle")
def update_governance_rule_lifecycle(
    draft_id: int,
    request: GovernanceRuleLifecycleRequest,
    auth: AuthContext = Depends(require_actor),
) -> dict:
    require_scope_role(auth, owner_scope=auth.owner_scope, required_role="reviewer")
    session = get_db_session()
    try:
        draft = update_rule_lifecycle(
            session=session,
            owner_scope=auth.owner_scope,
            draft_id=draft_id,
            lifecycle_status=request.lifecycle_status,
            lifecycle_rationale=request.lifecycle_rationale,
            superseded_by_rule_id=request.superseded_by_rule_id,
        )
        document = GovernanceRepository(session).get_document(owner_scope=auth.owner_scope, document_id=draft.document_id)
        session.commit()
        return {"rule": serialize_rule_draft(draft, source_title=document.title if document else None)}
    except ValueError as exc:
        session.rollback()
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise HTTPException(status_code=status_code, detail=message) from exc
    finally:
        session.close()
