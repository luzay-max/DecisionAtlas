from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.db.session import get_db_session
from app.llm.base import ProviderConfigurationError, ProviderError
from app.llm.provider_factory import build_runtime_providers
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
            runtime = build_runtime_providers()
            return answer_why_question(
                session=session,
                workspace_slug=request.workspace_slug,
                question=request.question,
                embedder=runtime.embedder,
            )
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ProviderConfigurationError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        except ProviderError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc
    finally:
        session.close()
