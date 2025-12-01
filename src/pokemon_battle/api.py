"""REST API endpoints for Pokemon Battle application."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from pokemon_battle import __version__
from pokemon_battle.database import get_db
from pokemon_battle.exceptions import (
    PokeAPIError,
    PokemonBattleError,
    PokemonNotFoundError,
    SamePokemonError,
)
from pokemon_battle.pokeapi import PokeAPIClient, get_pokeapi_client
from pokemon_battle.schemas import (
    BattleListResponse,
    BattleRequest,
    BattleResponse,
    ErrorResponse,
    HealthResponse,
    PokemonResponse,
)
from pokemon_battle.services import BattleService, PokemonService

router = APIRouter()


# Dependencies
def get_pokemon_service(
    db: Annotated[AsyncSession, Depends(get_db)],
    pokeapi: Annotated[PokeAPIClient, Depends(get_pokeapi_client)],
) -> PokemonService:
    """Dependency for PokemonService."""
    return PokemonService(db, pokeapi)


def get_battle_service(
    db: Annotated[AsyncSession, Depends(get_db)],
    pokemon_service: Annotated[PokemonService, Depends(get_pokemon_service)],
) -> BattleService:
    """Dependency for BattleService."""
    return BattleService(db, pokemon_service)


# Exception handlers helper
def handle_pokemon_error(error: PokemonBattleError) -> HTTPException:
    """Convert Pokemon errors to HTTP exceptions."""
    if isinstance(error, PokemonNotFoundError):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error.message,
        )
    if isinstance(error, SamePokemonError):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error.message,
        )
    if isinstance(error, PokeAPIError):
        return HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=error.message,
        )
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=error.message,
    )


# Health check endpoint
@router.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Health check",
)
async def health_check() -> HealthResponse:
    """Check if the API is running."""
    return HealthResponse(status="healthy", version=__version__)


# Pokemon endpoints
@router.get(
    "/pokemon/{name}",
    response_model=PokemonResponse,
    tags=["Pokemon"],
    summary="Get Pokemon by name",
    responses={
        404: {"model": ErrorResponse, "description": "Pokemon not found"},
        502: {"model": ErrorResponse, "description": "PokeAPI error"},
    },
)
async def get_pokemon(
    name: str,
    pokemon_service: Annotated[PokemonService, Depends(get_pokemon_service)],
) -> PokemonResponse:
    """
    Get Pokemon data by name.

    If the Pokemon is not in the database, it will be fetched from PokeAPI
    and cached locally.
    """
    try:
        pokemon = await pokemon_service.get_or_fetch_pokemon(name)
        return PokemonResponse.model_validate(pokemon)
    except PokemonBattleError as e:
        raise handle_pokemon_error(e) from e


@router.get(
    "/pokemon",
    response_model=list[PokemonResponse],
    tags=["Pokemon"],
    summary="List all Pokemon",
)
async def list_pokemon(
    pokemon_service: Annotated[PokemonService, Depends(get_pokemon_service)],
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[PokemonResponse]:
    """List all Pokemon stored in the database."""
    pokemon_list = await pokemon_service.list_pokemon(limit=limit, offset=offset)
    return [PokemonResponse.model_validate(p) for p in pokemon_list]


# Battle endpoints
@router.post(
    "/battles",
    response_model=BattleResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Battles"],
    summary="Start a new battle",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid battle request"},
        404: {"model": ErrorResponse, "description": "Pokemon not found"},
        502: {"model": ErrorResponse, "description": "PokeAPI error"},
    },
)
async def create_battle(
    request: BattleRequest,
    battle_service: Annotated[BattleService, Depends(get_battle_service)],
) -> BattleResponse:
    """
    Start a battle between two Pokemon.

    The battle result is determined by comparing stats, type effectiveness,
    and speed advantages. The result is persisted in the database.
    """
    try:
        battle = await battle_service.execute_battle(
            request.pokemon1_name,
            request.pokemon2_name,
        )
        return BattleResponse(
            id=battle.id,
            pokemon1=PokemonResponse.model_validate(battle.pokemon1),
            pokemon2=PokemonResponse.model_validate(battle.pokemon2),
            winner=PokemonResponse.model_validate(battle.winner) if battle.winner else None,
            pokemon1_score=battle.pokemon1_score,
            pokemon2_score=battle.pokemon2_score,
            battle_log=battle.battle_log,
            created_at=battle.created_at,
        )
    except PokemonBattleError as e:
        raise handle_pokemon_error(e) from e


@router.get(
    "/battles/{battle_id}",
    response_model=BattleResponse,
    tags=["Battles"],
    summary="Get battle by ID",
    responses={404: {"model": ErrorResponse, "description": "Battle not found"}},
)
async def get_battle(
    battle_id: int,
    battle_service: Annotated[BattleService, Depends(get_battle_service)],
) -> BattleResponse:
    """Get a specific battle by its ID."""
    battle = await battle_service.get_battle(battle_id)
    if battle is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Battle with id {battle_id} not found",
        )
    return BattleResponse(
        id=battle.id,
        pokemon1=PokemonResponse.model_validate(battle.pokemon1),
        pokemon2=PokemonResponse.model_validate(battle.pokemon2),
        winner=PokemonResponse.model_validate(battle.winner) if battle.winner else None,
        pokemon1_score=battle.pokemon1_score,
        pokemon2_score=battle.pokemon2_score,
        battle_log=battle.battle_log,
        created_at=battle.created_at,
    )


@router.get(
    "/battles",
    response_model=list[BattleListResponse],
    tags=["Battles"],
    summary="List all battles",
)
async def list_battles(
    battle_service: Annotated[BattleService, Depends(get_battle_service)],
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[BattleListResponse]:
    """List all battles with summary information."""
    battles = await battle_service.list_battles(limit=limit, offset=offset)
    return [
        BattleListResponse(
            id=b.id,
            pokemon1_name=b.pokemon1.name,
            pokemon2_name=b.pokemon2.name,
            winner_name=b.winner.name if b.winner else None,
            pokemon1_score=b.pokemon1_score,
            pokemon2_score=b.pokemon2_score,
            created_at=b.created_at,
        )
        for b in battles
    ]
