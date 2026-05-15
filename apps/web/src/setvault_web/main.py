from fastapi import FastAPI

from setvault_core.db import init_engine

from setvault_web import __version__
from setvault_web.api import auth as auth_api
from setvault_web.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    init_engine(settings.database_url)
    app = FastAPI(title="SetVault", version=__version__)

    @app.get("/api/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "version": __version__, "base_url": settings.base_url}

    app.include_router(auth_api.router)
    return app


app = create_app()
