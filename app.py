"""
Application Entry Point

Professional YouTube Downloader
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from core.config import settings
from core.database import create_database
from core.logger import app_logger

from downloader.ytdlp import _ffmpeg_available
from web.routes import router as web_router


# ==========================================================
# Application Lifecycle
# ==========================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs once when the application starts and stops.
    """

    # Startup
    app_logger.info("=" * 70)
    app_logger.info(f"{settings.PROJECT_NAME} v{settings.VERSION}")
    app_logger.info("Initializing application...")

    # Create database
    create_database()

    app_logger.info(f"Download Folder : {settings.DOWNLOAD_DIR}")
    app_logger.info(f"Database        : {settings.DATA_DIR / settings.DATABASE_FILE}")
    app_logger.info(f"Server          : http://{settings.HOST}:{settings.PORT}")

    if _ffmpeg_available():
        app_logger.info("ffmpeg          : found  — high-quality merged downloads enabled")
    else:
        app_logger.warning(
            "ffmpeg          : NOT FOUND — downloads will use best single-file stream. "
            "Install ffmpeg and add it to PATH to enable 1080p+ merged quality."
        )

    app_logger.info("=" * 70)

    yield

    # Shutdown
    app_logger.info("Application stopped.")


# ==========================================================
# FastAPI
# ==========================================================

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Professional YouTube Downloader using yt-dlp",
    version=settings.VERSION,
    lifespan=lifespan,
)


# ==========================================================
# Static Files
# ==========================================================

app.mount(
    "/static",
    StaticFiles(
        directory=settings.BASE_DIR / "web" / "static"
    ),
    name="static",
)


# ==========================================================
# Routers
# ==========================================================

app.include_router(web_router)


# ==========================================================
# Health Check
# ==========================================================

@app.get("/health", tags=["System"])
async def health():
    return {
        "status": "ok",
        "application": settings.PROJECT_NAME,
        "version": settings.VERSION,
    }