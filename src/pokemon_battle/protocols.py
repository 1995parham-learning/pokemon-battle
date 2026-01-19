"""Protocol definitions for pluggable interfaces."""

from typing import Protocol

from pokemon_battle.models import Pokemon
from pokemon_battle.schemas import PokemonCreate


class BattleResult(Protocol):
    """Protocol for battle result data."""

    @property
    def winner(self) -> Pokemon | None:
        """The winning Pokemon, or None if draw."""
        ...

    @property
    def pokemon1_score(self) -> float:
        """Score for the first Pokemon."""
        ...

    @property
    def pokemon2_score(self) -> float:
        """Score for the second Pokemon."""
        ...

    @property
    def battle_log(self) -> str:
        """Detailed battle log."""
        ...

    @property
    def is_draw(self) -> bool:
        """Whether the battle ended in a draw."""
        ...


class PokemonProvider(Protocol):
    """Protocol for fetching Pokemon data from external sources.

    Implementations can fetch from:
    - PokeAPI (default)
    - Local files (JSON, CSV)
    - Other Pokemon APIs
    - Mock data for testing
    """

    async def get_pokemon(self, name: str) -> PokemonCreate:
        """
        Fetch Pokemon data by name.

        Args:
            name: The name of the Pokemon to fetch.

        Returns:
            PokemonCreate schema with Pokemon data.

        Raises:
            PokemonNotFoundError: If the Pokemon is not found.
        """
        ...


class BattleEngine(Protocol):
    """Protocol for battle calculation engines.

    Implementations can use different algorithms:
    - Stats-based (default)
    - Turn-based simulation
    - Random outcomes
    - Custom scoring systems
    """

    def execute(self, pokemon1: Pokemon, pokemon2: Pokemon) -> BattleResult:
        """
        Execute a battle between two Pokemon.

        Args:
            pokemon1: The first Pokemon.
            pokemon2: The second Pokemon.

        Returns:
            BattleResult with winner, scores, and battle log.
        """
        ...
