from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


REPO_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    app_name: str = "DecisionAtlas Engine"
    app_env: str = "development"
    port: int = 8000
    database_url: str = "sqlite:///./decisionatlas.db"
    github_token: str | None = None
    llm_provider_mode: str = "auto"
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
    return Settings()
