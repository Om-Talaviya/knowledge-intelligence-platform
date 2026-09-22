"""FastAPI application factory and middleware configuration."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from kip.api.routers import auth, chat, documents, health, ingest, settings
from kip.config import get_settings
from kip.errors import register_exception_handlers
from kip.logging_setup import setup_logging


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app_settings = get_settings()
    setup_logging(app_settings.log_level)

    app = FastAPI(
        title="Knowledge Intelligence Platform",
        version="1.0.0",
        description="Autonomous Multimodal Research & Knowledge Intelligence API",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(documents.router)
    app.include_router(chat.router)
    app.include_router(settings.router)
    app.include_router(ingest.router)

    return app


app = create_app()
