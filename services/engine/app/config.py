from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "DecisionAtlas Engine"
    app_env: str = "development"
    port: int = 8000
    database_url: str = "sqlite:///./decisionatlas.db"
    github_token: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


def get_settings() -> Settings:
    return Settings()
