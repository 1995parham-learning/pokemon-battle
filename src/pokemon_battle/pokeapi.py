"""PokeAPI client with caching support."""

import time
from dataclasses import dataclass, field
from typing import Any

import httpx

from pokemon_battle.config import get_settings
from pokemon_battle.exceptions import PokeAPIError, PokemonNotFoundError
from pokemon_battle.schemas import PokemonCreate

settings = get_settings()


@dataclass
class CacheEntry:
    """A cached entry with expiration time."""

    data: dict[str, Any]
    expires_at: float


@dataclass
class PokemonCache:
    """Simple in-memory cache for Pokemon data."""

    _cache: dict[str, CacheEntry] = field(default_factory=dict)
    ttl: int = field(default_factory=lambda: settings.cache.pokemon_ttl)

    def get(self, key: str) -> dict[str, Any] | None:
        """Get a value from cache if not expired."""
        entry = self._cache.get(key)
        if entry is None:
            return None
        if time.time() > entry.expires_at:
            del self._cache[key]
            return None
        return entry.data

    def set(self, key: str, value: dict[str, Any]) -> None:
        """Set a value in cache with TTL."""
        self._cache[key] = CacheEntry(
            data=value,
            expires_at=time.time() + self.ttl,
        )

    def clear(self) -> None:
        """Clear all cached entries."""
        self._cache.clear()


# Global cache instance
_pokemon_cache = PokemonCache()


def get_cache() -> PokemonCache:
    """Get the global cache instance."""
    return _pokemon_cache


class PokeAPIClient:
    """Client for interacting with the PokeAPI."""

    def __init__(self, cache: PokemonCache | None = None) -> None:
        self.base_url = settings.pokeapi.base_url
        self.timeout = settings.pokeapi.timeout
        self.cache = cache or get_cache()

    async def get_pokemon(self, name: str) -> PokemonCreate:
        """
        Fetch Pokemon data from PokeAPI.

        Args:
            name: The name of the Pokemon to fetch.

        Returns:
            PokemonCreate schema with Pokemon data.

        Raises:
            PokemonNotFoundError: If the Pokemon is not found.
            PokeAPIError: If there's an error communicating with PokeAPI.
        """
        name_lower = name.lower().strip()

        # Check cache first
        cached_data = self.cache.get(name_lower)
        if cached_data is not None:
            return self._parse_pokemon_data(cached_data)

        # Fetch from API
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(f"{self.base_url}/pokemon/{name_lower}")

                if response.status_code == 404:
                    raise PokemonNotFoundError(name)

                response.raise_for_status()
                data = response.json()

                # Cache the response
                self.cache.set(name_lower, data)

                return self._parse_pokemon_data(data)

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    raise PokemonNotFoundError(name) from e
                raise PokeAPIError(f"HTTP error {e.response.status_code}") from e
            except httpx.RequestError as e:
                raise PokeAPIError(str(e)) from e

    def _parse_pokemon_data(self, data: dict[str, Any]) -> PokemonCreate:
        """Parse raw PokeAPI response into PokemonCreate schema."""
        stats = {stat["stat"]["name"]: stat["base_stat"] for stat in data["stats"]}
        types = [t["type"]["name"] for t in data["types"]]

        sprite_url = None
        if sprites := data.get("sprites"):
            sprite_url = sprites.get("front_default")

        return PokemonCreate(
            pokeapi_id=data["id"],
            name=data["name"],
            hp=stats.get("hp", 0),
            attack=stats.get("attack", 0),
            defense=stats.get("defense", 0),
            special_attack=stats.get("special-attack", 0),
            special_defense=stats.get("special-defense", 0),
            speed=stats.get("speed", 0),
            types=",".join(types),
            sprite_url=sprite_url,
        )


def get_pokeapi_client() -> PokeAPIClient:
    """Get a PokeAPI client instance."""
    return PokeAPIClient()
