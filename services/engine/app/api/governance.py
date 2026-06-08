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
from app.repositories.review_audit import ReviewAuditRepository, serialize_review_audit_event

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


def _rule_state(draft) -> dict:
    return {
        "review_state": draft.review_state,
        "status": draft.status,
        "lifecycle_status": draft.lifecycle_status,
        "superseded_by_rule_id": draft.superseded_by_rule_id,
    }


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
                {
                    **serialize_rule_draft(
                        draft,
                        source_title=documents.get(draft.document_id).title if documents.get(draft.document_id) else None,
                    ),
                    "audit_history": [
                        serialize_review_audit_event(event)
                        for event in ReviewAuditRepository(session).list_for_target(
                            owner_scope=auth.owner_scope,
                            target_type="governance_rule",
                            target_id=draft.id,
                        )
                    ],
                }
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
        repository = GovernanceRepository(session)
        existing = repository.get_rule_draft(owner_scope=auth.owner_scope, draft_id=draft_id)
        if existing is None:
            raise ValueError(f"Governance rule draft not found: {draft_id}")
        previous_state = _rule_state(existing)
        draft = review_rule_draft(
            session=session,
            owner_scope=auth.owner_scope,
            draft_id=draft_id,
            review_state=request.review_state,
            reviewer=auth.username,
            review_rationale=request.review_rationale,
        )
        event = ReviewAuditRepository(session).create_event(
            owner_scope=auth.owner_scope,
            workspace_id=None,
            actor_id=auth.actor_id,
            actor_username=auth.username,
            actor_role=auth.role,
            target_type="governance_rule",
            target_id=draft.id,
            action=f"governance_rule_review_{request.review_state}",
            previous_state=previous_state,
            new_state=_rule_state(draft),
            rationale=request.review_rationale,
        )
        document = repository.get_document(owner_scope=auth.owner_scope, document_id=draft.document_id)
        session.commit()
        return {
            "rule": {
                **serialize_rule_draft(draft, source_title=document.title if document else None),
                "audit_history": [
                    serialize_review_audit_event(history_event)
                    for history_event in ReviewAuditRepository(session).list_for_target(
                        owner_scope=auth.owner_scope,
                        target_type="governance_rule",
                        target_id=draft.id,
                    )
                ],
            },
            "audit_event": serialize_review_audit_event(event),
        }
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
        repository = GovernanceRepository(session)
        existing = repository.get_rule_draft(owner_scope=auth.owner_scope, draft_id=draft_id)
        if existing is None:
            raise ValueError(f"Governance rule draft not found: {draft_id}")
        previous_state = _rule_state(existing)
        draft = update_rule_lifecycle(
            session=session,
            owner_scope=auth.owner_scope,
            draft_id=draft_id,
            lifecycle_status=request.lifecycle_status,
            lifecycle_rationale=request.lifecycle_rationale,
            superseded_by_rule_id=request.superseded_by_rule_id,
        )
        event = ReviewAuditRepository(session).create_event(
            owner_scope=auth.owner_scope,
            workspace_id=None,
            actor_id=auth.actor_id,
            actor_username=auth.username,
            actor_role=auth.role,
            target_type="governance_rule",
            target_id=draft.id,
            action=f"governance_rule_lifecycle_{request.lifecycle_status}",
            previous_state=previous_state,
            new_state=_rule_state(draft),
            rationale=request.lifecycle_rationale,
            metadata={"superseded_by_rule_id": request.superseded_by_rule_id},
        )
        document = repository.get_document(owner_scope=auth.owner_scope, document_id=draft.document_id)
        session.commit()
        return {
            "rule": {
                **serialize_rule_draft(draft, source_title=document.title if document else None),
                "audit_history": [
                    serialize_review_audit_event(history_event)
                    for history_event in ReviewAuditRepository(session).list_for_target(
                        owner_scope=auth.owner_scope,
                        target_type="governance_rule",
                        target_id=draft.id,
                    )
                ],
            },
            "audit_event": serialize_review_audit_event(event),
        }
    except ValueError as exc:
        session.rollback()
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise HTTPException(status_code=status_code, detail=message) from exc
    finally:
        session.close()


@router.get("/guardrail")
def get_governance_guardrail(
    auth: AuthContext = Depends(require_actor),
) -> dict:
    require_scope_role(auth, owner_scope=auth.owner_scope, required_role="viewer")
    from app.governance.agent_guardrail import run_agent_governance_guardrail
    from app.config import REPO_ROOT
    session = get_db_session()
    try:
        result = run_agent_governance_guardrail(
            root=REPO_ROOT,
            owner_scope=auth.owner_scope,
            database_url=str(session.bind.url),
        )
        return result.to_dict()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        session.close()
