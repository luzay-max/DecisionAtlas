from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.config import get_runtime_provider_modes, get_settings, set_runtime_provider_modes
from app.llm.provider_factory import build_runtime_providers

router = APIRouter(prefix="/runtime", tags=["runtime"])


class ProviderModeRequest(BaseModel):
    mode: str


@router.get("/provider-mode")
def get_provider_mode() -> dict:
    settings = get_settings()
    runtime = build_runtime_providers(settings)
    overrides = get_runtime_provider_modes()
    return {
        "mode": runtime.mode,
        "is_live": runtime.is_live,
        "llm_provider_mode": settings.llm_provider_mode,
        "embedding_provider_mode": settings.embedding_provider_mode,
        "override_active": overrides["llm_provider_mode"] is not None,
    }


@router.post("/provider-mode")
def set_provider_mode(request: ProviderModeRequest) -> dict:
    normalized = request.mode.lower()
    if normalized == "fake":
        set_runtime_provider_modes(llm_provider_mode="fake", embedding_provider_mode="fake")
    elif normalized == "live":
        set_runtime_provider_modes(
            llm_provider_mode="openai_compatible",
            embedding_provider_mode=None,
        )
    elif normalized == "auto":
        set_runtime_provider_modes(llm_provider_mode=None, embedding_provider_mode=None)
    else:
        raise HTTPException(status_code=400, detail="Invalid provider mode")

    settings = get_settings()
    try:
        runtime = build_runtime_providers(settings)
    except Exception as exc:
        if normalized == "live":
            set_runtime_provider_modes(llm_provider_mode="fake", embedding_provider_mode="fake")
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    overrides = get_runtime_provider_modes()
    return {
        "mode": runtime.mode,
        "is_live": runtime.is_live,
        "llm_provider_mode": settings.llm_provider_mode,
        "embedding_provider_mode": settings.embedding_provider_mode,
        "override_active": overrides["llm_provider_mode"] is not None,
    }
