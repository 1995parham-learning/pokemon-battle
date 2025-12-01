"""Configuration settings for the Pokemon Battle application."""

import tomllib
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class DatabaseConfig:
    """Database configuration."""

    url: str = "postgresql+asyncpg://pokemon:pokemon@localhost:5432/pokemon_battle"


@dataclass(frozen=True)
class PokeAPIConfig:
    """PokeAPI configuration."""

    base_url: str = "https://pokeapi.co/api/v2"
    timeout: float = 30.0


@dataclass(frozen=True)
class CacheConfig:
    """Cache configuration."""

    pokemon_ttl: int = 3600  # 1 hour


@dataclass(frozen=True)
class APIConfig:
    """API configuration."""

    title: str = "Pokemon Battle API"
    version: str = "1.0.0"
    debug: bool = False


@dataclass(frozen=True)
class Settings:
    """Application settings loaded from TOML configuration."""

    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    pokeapi: PokeAPIConfig = field(default_factory=PokeAPIConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    api: APIConfig = field(default_factory=APIConfig)


def _load_config_file(path: Path) -> dict[str, Any]:
    """Load configuration from a TOML file."""
    if not path.exists():
        return {}
    with path.open("rb") as f:
        return tomllib.load(f)


def _create_settings(config: dict[str, Any]) -> Settings:
    """Create Settings from configuration dictionary."""
    db_config = config.get("database", {})
    pokeapi_config = config.get("pokeapi", {})
    cache_config = config.get("cache", {})
    api_config = config.get("api", {})

    return Settings(
        database=DatabaseConfig(
            url=db_config.get("url", DatabaseConfig.url),
        ),
        pokeapi=PokeAPIConfig(
            base_url=pokeapi_config.get("base_url", PokeAPIConfig.base_url),
            timeout=pokeapi_config.get("timeout", PokeAPIConfig.timeout),
        ),
        cache=CacheConfig(
            pokemon_ttl=cache_config.get("pokemon_ttl", CacheConfig.pokemon_ttl),
        ),
        api=APIConfig(
            title=api_config.get("title", APIConfig.title),
            version=api_config.get("version", APIConfig.version),
            debug=api_config.get("debug", APIConfig.debug),
        ),
    )


@lru_cache
def get_settings(config_path: str | None = None) -> Settings:
    """
    Get cached settings instance.

    Args:
        config_path: Optional path to config.toml file.
                    If not provided, looks for config.toml in current directory.
    """
    path = Path("config.toml") if config_path is None else Path(config_path)
    config = _load_config_file(path)
    return _create_settings(config)
