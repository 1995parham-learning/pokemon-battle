"""Pytest fixtures for Pokemon Battle tests."""

from collections.abc import AsyncGenerator
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import StaticPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from pokemon_battle.database import get_db
from pokemon_battle.main import app
from pokemon_battle.models import Base, Pokemon
from pokemon_battle.pokeapi import PokeAPIClient, PokemonCache, get_pokeapi_client

# Test database setup
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession]:
    """Create a test database session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def test_cache() -> PokemonCache:
    """Create a test cache instance."""
    return PokemonCache()


@pytest.fixture
def mock_pikachu_data() -> dict[str, Any]:
    """Mock PokeAPI response for Pikachu."""
    return {
        "id": 25,
        "name": "pikachu",
        "stats": [
            {"base_stat": 35, "stat": {"name": "hp"}},
            {"base_stat": 55, "stat": {"name": "attack"}},
            {"base_stat": 40, "stat": {"name": "defense"}},
            {"base_stat": 50, "stat": {"name": "special-attack"}},
            {"base_stat": 50, "stat": {"name": "special-defense"}},
            {"base_stat": 90, "stat": {"name": "speed"}},
        ],
        "types": [{"type": {"name": "electric"}}],
        "sprites": {"front_default": "https://example.com/pikachu.png"},
    }


@pytest.fixture
def mock_charizard_data() -> dict[str, Any]:
    """Mock PokeAPI response for Charizard."""
    return {
        "id": 6,
        "name": "charizard",
        "stats": [
            {"base_stat": 78, "stat": {"name": "hp"}},
            {"base_stat": 84, "stat": {"name": "attack"}},
            {"base_stat": 78, "stat": {"name": "defense"}},
            {"base_stat": 109, "stat": {"name": "special-attack"}},
            {"base_stat": 85, "stat": {"name": "special-defense"}},
            {"base_stat": 100, "stat": {"name": "speed"}},
        ],
        "types": [{"type": {"name": "fire"}}, {"type": {"name": "flying"}}],
        "sprites": {"front_default": "https://example.com/charizard.png"},
    }


@pytest.fixture
def mock_blastoise_data() -> dict[str, Any]:
    """Mock PokeAPI response for Blastoise."""
    return {
        "id": 9,
        "name": "blastoise",
        "stats": [
            {"base_stat": 79, "stat": {"name": "hp"}},
            {"base_stat": 83, "stat": {"name": "attack"}},
            {"base_stat": 100, "stat": {"name": "defense"}},
            {"base_stat": 85, "stat": {"name": "special-attack"}},
            {"base_stat": 105, "stat": {"name": "special-defense"}},
            {"base_stat": 78, "stat": {"name": "speed"}},
        ],
        "types": [{"type": {"name": "water"}}],
        "sprites": {"front_default": "https://example.com/blastoise.png"},
    }


@pytest.fixture
def pikachu() -> Pokemon:
    """Create a test Pikachu Pokemon."""
    return Pokemon(
        id=1,
        pokeapi_id=25,
        name="pikachu",
        hp=35,
        attack=55,
        defense=40,
        special_attack=50,
        special_defense=50,
        speed=90,
        types="electric",
        sprite_url="https://example.com/pikachu.png",
    )


@pytest.fixture
def charizard() -> Pokemon:
    """Create a test Charizard Pokemon."""
    return Pokemon(
        id=2,
        pokeapi_id=6,
        name="charizard",
        hp=78,
        attack=84,
        defense=78,
        special_attack=109,
        special_defense=85,
        speed=100,
        types="fire,flying",
        sprite_url="https://example.com/charizard.png",
    )


@pytest.fixture
def blastoise() -> Pokemon:
    """Create a test Blastoise Pokemon."""
    return Pokemon(
        id=3,
        pokeapi_id=9,
        name="blastoise",
        hp=79,
        attack=83,
        defense=100,
        special_attack=85,
        special_defense=105,
        speed=78,
        types="water",
        sprite_url="https://example.com/blastoise.png",
    )


class MockPokeAPIClient(PokeAPIClient):
    """Mock PokeAPI client for testing."""

    def __init__(self, mock_data: dict[str, dict[str, Any]]) -> None:
        super().__init__(cache=PokemonCache())
        self.mock_data = mock_data

    async def get_pokemon(self, name: str) -> Any:
        """Return mock data instead of calling API."""
        name_lower = name.lower().strip()
        if name_lower in self.mock_data:
            return self._parse_pokemon_data(self.mock_data[name_lower])
        from pokemon_battle.exceptions import PokemonNotFoundError

        raise PokemonNotFoundError(name)


@pytest.fixture
def mock_pokeapi_client(
    mock_pikachu_data: dict[str, Any],
    mock_charizard_data: dict[str, Any],
    mock_blastoise_data: dict[str, Any],
) -> MockPokeAPIClient:
    """Create a mock PokeAPI client."""
    return MockPokeAPIClient(
        {
            "pikachu": mock_pikachu_data,
            "charizard": mock_charizard_data,
            "blastoise": mock_blastoise_data,
        }
    )


@pytest.fixture
async def client(
    db_session: AsyncSession,
    mock_pokeapi_client: MockPokeAPIClient,
) -> AsyncGenerator[AsyncClient]:
    """Create a test HTTP client."""

    async def override_get_db() -> AsyncGenerator[AsyncSession]:
        yield db_session

    def override_get_pokeapi_client() -> MockPokeAPIClient:
        return mock_pokeapi_client

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_pokeapi_client] = override_get_pokeapi_client

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
