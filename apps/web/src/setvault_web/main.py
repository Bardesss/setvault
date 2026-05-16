from fastapi import FastAPI
from setvault_core.db import init_engine

from setvault_web import __version__
from setvault_web.api import auth as auth_api
from setvault_web.api import connectors as connectors_api
from setvault_web.api import invites as invites_api
from setvault_web.api import media_roots as media_roots_api
from setvault_web.api import password_reset as password_reset_api
from setvault_web.api import uploads as uploads_api
from setvault_web.api import ws as ws_api
from setvault_web.config import get_settings
from setvault_web.middleware.csrf import CsrfMiddleware
from setvault_web.middleware.security_headers import SecurityHeadersMiddleware


def create_app() -> FastAPI:
    settings = get_settings()
    init_engine(settings.database_url)
    app = FastAPI(title="SetVault", version=__version__)

    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(CsrfMiddleware)

    @app.get("/api/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "version": __version__, "base_url": settings.base_url}

    app.include_router(auth_api.router)
    app.include_router(invites_api.router)
    app.include_router(password_reset_api.router)
    app.include_router(connectors_api.router)
    app.include_router(media_roots_api.router)
    app.include_router(uploads_api.router)
    app.include_router(ws_api.router)
    return app


app = create_app()
