"""Pydantic schemas for API request/response models."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PokemonBase(BaseModel):
    """Base Pokemon schema with common attributes."""

    name: str
    hp: int
    attack: int
    defense: int
    special_attack: int
    special_defense: int
    speed: int
    types: list[str]
    sprite_url: str | None = None


class PokemonCreate(BaseModel):
    """Schema for creating a Pokemon from PokeAPI data."""

    pokeapi_id: int
    name: str
    hp: int
    attack: int
    defense: int
    special_attack: int
    special_defense: int
    speed: int
    types: str
    sprite_url: str | None = None


class PokemonResponse(BaseModel):
    """Pokemon response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    pokeapi_id: int
    name: str
    hp: int
    attack: int
    defense: int
    special_attack: int
    special_defense: int
    speed: int
    types: str
    sprite_url: str | None
    created_at: datetime


class BattleRequest(BaseModel):
    """Request schema for starting a battle."""

    pokemon1_name: str = Field(..., min_length=1, description="Name of the first Pokemon")
    pokemon2_name: str = Field(..., min_length=1, description="Name of the second Pokemon")


class BattleResponse(BaseModel):
    """Response schema for battle results."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    pokemon1: PokemonResponse
    pokemon2: PokemonResponse
    winner: PokemonResponse | None
    pokemon1_score: float
    pokemon2_score: float
    battle_log: str
    created_at: datetime


class BattleListResponse(BaseModel):
    """Response schema for listing battles."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    pokemon1_name: str
    pokemon2_name: str
    winner_name: str | None
    pokemon1_score: float
    pokemon2_score: float
    created_at: datetime


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str


class ErrorResponse(BaseModel):
    """Error response schema."""

    detail: str
    error_code: str | None = None
