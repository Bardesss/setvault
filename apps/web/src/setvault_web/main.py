from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from setvault_core.db import init_engine
from starlette.responses import FileResponse

from setvault_web import __version__
from setvault_web.api import admin as admin_api
from setvault_web.api import auth as auth_api
from setvault_web.api import catalog as catalog_api
from setvault_web.api import connectors as connectors_api
from setvault_web.api import dev_seed as dev_seed_api
from setvault_web.api import invites as invites_api
from setvault_web.api import jobs as jobs_api
from setvault_web.api import me as me_api
from setvault_web.api import media_roots as media_roots_api
from setvault_web.api import password_reset as password_reset_api
from setvault_web.api import providers as providers_api
from setvault_web.api import search as search_api
from setvault_web.api import sets as sets_api
from setvault_web.api import tracklist as tracklist_api
from setvault_web.api import uploads as uploads_api
from setvault_web.api import users as users_api
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
    app.include_router(catalog_api.router)
    app.include_router(sets_api.router)
    app.include_router(tracklist_api.router)
    app.include_router(search_api.router)
    app.include_router(ws_api.router)
    app.include_router(admin_api.router)
    app.include_router(providers_api.router)
    app.include_router(jobs_api.router)
    app.include_router(users_api.router)
    app.include_router(me_api.router)
    if dev_seed_api.is_enabled():
        app.include_router(dev_seed_api.router)

    # Static frontend bundle (SvelteKit adapter-static output). The build/
    # contents are dropped here by the Docker frontend stage; only a
    # placeholder index.html ships in source control.
    static_root = Path(__file__).parent / "static"
    if static_root.exists():
        if (static_root / "_app").exists():
            app.mount(
                "/_app",
                StaticFiles(directory=static_root / "_app"),
                name="sveltekit_assets",
            )
        if (static_root / "fonts").exists():
            app.mount(
                "/fonts",
                StaticFiles(directory=static_root / "fonts"),
                name="fonts",
            )

        @app.get("/{full_path:path}", include_in_schema=False)
        async def spa_fallback(full_path: str) -> FileResponse:
            if full_path.startswith(("api/", "uploads/", "ws/")):
                raise HTTPException(status_code=404)
            candidate = static_root / full_path
            if candidate.is_file():
                return FileResponse(candidate)
            return FileResponse(static_root / "index.html")

    return app


app = create_app()
