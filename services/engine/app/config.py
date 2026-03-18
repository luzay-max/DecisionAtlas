from pydantic_settings import BaseSettings, SettingsConfigDict


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
    demo_repo: str = "openai/openai-cookbook"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


def get_settings() -> Settings:
    return Settings()
