"""FastAPI application entry point."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from pokemon_battle import __version__
from pokemon_battle.api import router
from pokemon_battle.config import get_settings
from pokemon_battle.database import close_db, init_db
from pokemon_battle.exceptions import PokemonBattleError

settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    """Application lifespan handler for startup and shutdown events."""
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()


app = FastAPI(
    title=settings.api.title,
    version=settings.api.version,
    description=(
        "A Pokemon battle simulator API that fetches Pokemon data from PokeAPI "
        "and determines battle outcomes based on stats and type effectiveness."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.exception_handler(PokemonBattleError)
async def pokemon_battle_error_handler(
    request: Request,  # noqa: ARG001
    exc: PokemonBattleError,
) -> JSONResponse:
    """Global exception handler for PokemonBattleError."""
    return JSONResponse(
        status_code=500,
        content={"detail": exc.message, "error_code": exc.error_code},
    )


# Include API routes
app.include_router(router, prefix="/api/v1")


# Root endpoint
@app.get("/", tags=["Root"])
async def root() -> dict[str, str]:
    """Root endpoint with API information."""
    return {
        "name": settings.api.title,
        "version": __version__,
        "docs": "/docs",
    }


def create_app() -> FastAPI:
    """Factory function for creating the FastAPI application."""
    return app
