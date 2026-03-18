from fastapi import FastAPI

from app.api.decisions import router as decisions_router
from app.api.health import router as health_router
from app.api.imports import router as imports_router
from app.api.query import router as query_router
from app.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name)
    app.include_router(health_router)
    app.include_router(imports_router)
    app.include_router(decisions_router)
    app.include_router(query_router)
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.port, reload=False)
