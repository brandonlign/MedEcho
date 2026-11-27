"""FastAPI application factory."""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from medecho import __version__
from medecho.config import REPO_ROOT, Settings, load_settings
from medecho.db.session import Database

log = logging.getLogger("medecho")
WEB_DIR = REPO_ROOT / "web"


def create_app(settings: Settings | None = None) -> FastAPI:
    cfg = settings or load_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        cfg.ensure_dirs()
        app.state.db.create_all()
        log.info("MedEcho %s started (demo=%s, transport=%s)", __version__, cfg.demo, cfg.transport)
        yield

    app = FastAPI(title="MedEcho", version=__version__, lifespan=lifespan)
    app.state.settings = cfg
    app.state.db = Database(cfg.db_url)
    app.state.templates = Jinja2Templates(directory=str(WEB_DIR / "templates"))
    app.mount("/static", StaticFiles(directory=str(WEB_DIR / "static")), name="static")

    @app.get("/health")
    def health() -> dict[str, object]:
        return {
            "status": "ok",
            "version": __version__,
            "demo": cfg.demo,
            "transport": cfg.transport,
            "grader": cfg.grader,
            "paid_keys_required": False,
        }

    @app.get("/", response_class=HTMLResponse)
    def home(request: Request) -> HTMLResponse:
        templates: Jinja2Templates = request.app.state.templates
        return templates.TemplateResponse(request, "home.html", {"demo": cfg.demo})

    return app


app = create_app()
