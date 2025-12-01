"""Custom exceptions for the Pokemon Battle application."""


class PokemonBattleError(Exception):
    """Base exception for Pokemon Battle application."""

    def __init__(self, message: str, error_code: str | None = None) -> None:
        self.message = message
        self.error_code = error_code
        super().__init__(message)


class PokemonNotFoundError(PokemonBattleError):
    """Raised when a Pokemon is not found."""

    def __init__(self, pokemon_name: str) -> None:
        super().__init__(
            message=f"Pokemon '{pokemon_name}' not found",
            error_code="POKEMON_NOT_FOUND",
        )
        self.pokemon_name = pokemon_name


class PokeAPIError(PokemonBattleError):
    """Raised when there's an error communicating with PokeAPI."""

    def __init__(self, message: str) -> None:
        super().__init__(
            message=f"PokeAPI error: {message}",
            error_code="POKEAPI_ERROR",
        )


class SamePokemonError(PokemonBattleError):
    """Raised when trying to battle a Pokemon against itself."""

    def __init__(self, pokemon_name: str) -> None:
        super().__init__(
            message=f"Cannot battle '{pokemon_name}' against itself",
            error_code="SAME_POKEMON",
        )
        self.pokemon_name = pokemon_name


class DatabaseError(PokemonBattleError):
    """Raised when there's a database error."""

    def __init__(self, message: str) -> None:
        super().__init__(
            message=f"Database error: {message}",
            error_code="DATABASE_ERROR",
        )
