from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.db.session import get_db_session
from app.indexing.embedder import FakeEmbedder
from app.retrieval.answering import answer_why_question

router = APIRouter(prefix="/query", tags=["query"])


class WhyQueryRequest(BaseModel):
    workspace_slug: str
    question: str


@router.post("/why")
def query_why(request: WhyQueryRequest) -> dict:
    session = get_db_session()
    try:
        try:
            return answer_why_question(
                session=session,
                workspace_slug=request.workspace_slug,
                question=request.question,
                embedder=FakeEmbedder(),
            )
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
    finally:
        session.close()
