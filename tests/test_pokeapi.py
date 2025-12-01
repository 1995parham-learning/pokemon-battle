"""Tests for PokeAPI client."""

import time
from typing import Any

from pokemon_battle.pokeapi import PokeAPIClient, PokemonCache


class TestPokemonCache:
    """Tests for the Pokemon cache."""

    def test_set_and_get(self) -> None:
        """Test setting and getting cache values."""
        cache = PokemonCache(ttl=60)
        cache.set("pikachu", {"name": "pikachu"})
        result = cache.get("pikachu")
        assert result == {"name": "pikachu"}

    def test_get_missing_key(self) -> None:
        """Test getting a missing key returns None."""
        cache = PokemonCache(ttl=60)
        result = cache.get("missing")
        assert result is None

    def test_cache_expiration(self) -> None:
        """Test that cache entries expire."""
        cache = PokemonCache(ttl=1)  # 1 second TTL
        cache.set("pikachu", {"name": "pikachu"})

        # Should be available immediately
        assert cache.get("pikachu") is not None

        # Wait for expiration
        time.sleep(1.1)
        assert cache.get("pikachu") is None

    def test_clear_cache(self) -> None:
        """Test clearing the cache."""
        cache = PokemonCache(ttl=60)
        cache.set("pikachu", {"name": "pikachu"})
        cache.set("charizard", {"name": "charizard"})

        cache.clear()

        assert cache.get("pikachu") is None
        assert cache.get("charizard") is None


class TestPokeAPIClientParsing:
    """Tests for PokeAPI client data parsing."""

    def test_parse_pokemon_data(self, mock_pikachu_data: dict[str, Any]) -> None:
        """Test parsing Pokemon data from API response."""
        client = PokeAPIClient()
        result = client._parse_pokemon_data(mock_pikachu_data)

        assert result.pokeapi_id == 25
        assert result.name == "pikachu"
        assert result.hp == 35
        assert result.attack == 55
        assert result.defense == 40
        assert result.special_attack == 50
        assert result.special_defense == 50
        assert result.speed == 90
        assert result.types == "electric"
        assert result.sprite_url == "https://example.com/pikachu.png"

    def test_parse_dual_type_pokemon(self, mock_charizard_data: dict[str, Any]) -> None:
        """Test parsing dual-type Pokemon data."""
        client = PokeAPIClient()
        result = client._parse_pokemon_data(mock_charizard_data)

        assert result.types == "fire,flying"

    def test_parse_missing_sprite(self, mock_pikachu_data: dict[str, Any]) -> None:
        """Test parsing Pokemon with missing sprite."""
        mock_pikachu_data["sprites"] = {}
        client = PokeAPIClient()
        result = client._parse_pokemon_data(mock_pikachu_data)

        assert result.sprite_url is None
