from fastapi import FastAPI

from setvault_web import __version__
from setvault_web.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="SetVault", version=__version__)

    @app.get("/api/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "version": __version__, "base_url": settings.base_url}

    return app


app = create_app()
