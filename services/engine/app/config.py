from pathlib import Path
from threading import Lock

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


REPO_ROOT = Path(__file__).resolve().parents[3]
_runtime_override_lock = Lock()
_runtime_provider_overrides: dict[str, str | None] = {
    "llm_provider_mode": None,
    "embedding_provider_mode": None,
}


class Settings(BaseSettings):
    app_name: str = "DecisionAtlas Engine"
    app_env: str = "development"
    port: int = 8000
    database_url: str = "sqlite:///./decisionatlas.db"
    github_token: str | None = None
    github_import_max_pages: int = 5
    llm_provider_mode: str = "auto"
    embedding_provider_mode: str = "auto"
    llm_api_key: str | None = None
    embedding_api_key: str | None = None
    llm_base_url: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    llm_timeout_seconds: float = 60.0
    demo_workspace_slug: str = "demo-workspace"
    demo_repo: str = "encode/httpx"

    model_config = SettingsConfigDict(
        env_file=(REPO_ROOT / ".env", ".env"),
        extra="ignore",
    )

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        if isinstance(value, str) and value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+psycopg://", 1)
        return value


def get_settings() -> Settings:
    settings = Settings()
    with _runtime_override_lock:
        if _runtime_provider_overrides["llm_provider_mode"] is not None:
            settings.llm_provider_mode = str(_runtime_provider_overrides["llm_provider_mode"])
        if _runtime_provider_overrides["embedding_provider_mode"] is not None:
            settings.embedding_provider_mode = str(_runtime_provider_overrides["embedding_provider_mode"])
    return settings


def set_runtime_provider_modes(*, llm_provider_mode: str | None, embedding_provider_mode: str | None) -> None:
    with _runtime_override_lock:
        _runtime_provider_overrides["llm_provider_mode"] = llm_provider_mode
        _runtime_provider_overrides["embedding_provider_mode"] = embedding_provider_mode


def get_runtime_provider_modes() -> dict[str, str | None]:
    with _runtime_override_lock:
        return dict(_runtime_provider_overrides)
