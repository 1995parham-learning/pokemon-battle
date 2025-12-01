"""Business logic services for Pokemon battles."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from pokemon_battle.battle import execute_battle
from pokemon_battle.exceptions import SamePokemonError
from pokemon_battle.models import Battle, Pokemon
from pokemon_battle.pokeapi import PokeAPIClient
from pokemon_battle.schemas import PokemonCreate


class PokemonService:
    """Service for Pokemon-related operations."""

    def __init__(self, db: AsyncSession, pokeapi_client: PokeAPIClient) -> None:
        self.db = db
        self.pokeapi_client = pokeapi_client

    async def get_or_fetch_pokemon(self, name: str) -> Pokemon:
        """
        Get a Pokemon from database or fetch from PokeAPI.

        Args:
            name: The name of the Pokemon.

        Returns:
            Pokemon model instance.

        Raises:
            PokemonNotFoundError: If the Pokemon doesn't exist.
            PokeAPIError: If there's an error fetching from PokeAPI.
        """
        name_lower = name.lower().strip()

        # Check database first
        stmt = select(Pokemon).where(Pokemon.name == name_lower)
        result = await self.db.execute(stmt)
        pokemon = result.scalar_one_or_none()

        if pokemon is not None:
            return pokemon

        # Fetch from PokeAPI
        pokemon_data = await self.pokeapi_client.get_pokemon(name_lower)

        # Create and save to database
        pokemon = await self._create_pokemon(pokemon_data)
        return pokemon

    async def _create_pokemon(self, data: PokemonCreate) -> Pokemon:
        """Create a new Pokemon in the database."""
        pokemon = Pokemon(
            pokeapi_id=data.pokeapi_id,
            name=data.name,
            hp=data.hp,
            attack=data.attack,
            defense=data.defense,
            special_attack=data.special_attack,
            special_defense=data.special_defense,
            speed=data.speed,
            types=data.types,
            sprite_url=data.sprite_url,
        )
        self.db.add(pokemon)
        await self.db.flush()
        return pokemon

    async def get_pokemon_by_id(self, pokemon_id: int) -> Pokemon | None:
        """Get a Pokemon by its database ID."""
        stmt = select(Pokemon).where(Pokemon.id == pokemon_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_pokemon(self, limit: int = 100, offset: int = 0) -> list[Pokemon]:
        """List all Pokemon in the database."""
        stmt = select(Pokemon).order_by(Pokemon.name).limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class BattleService:
    """Service for battle-related operations."""

    def __init__(self, db: AsyncSession, pokemon_service: PokemonService) -> None:
        self.db = db
        self.pokemon_service = pokemon_service

    async def execute_battle(self, pokemon1_name: str, pokemon2_name: str) -> Battle:
        """
        Execute a battle between two Pokemon.

        Args:
            pokemon1_name: Name of the first Pokemon.
            pokemon2_name: Name of the second Pokemon.

        Returns:
            Battle record with results.

        Raises:
            SamePokemonError: If both names refer to the same Pokemon.
            PokemonNotFoundError: If a Pokemon doesn't exist.
        """
        # Normalize names
        name1 = pokemon1_name.lower().strip()
        name2 = pokemon2_name.lower().strip()

        # Check for same Pokemon
        if name1 == name2:
            raise SamePokemonError(name1)

        # Get or fetch both Pokemon
        pokemon1 = await self.pokemon_service.get_or_fetch_pokemon(name1)
        pokemon2 = await self.pokemon_service.get_or_fetch_pokemon(name2)

        # Execute battle
        result = execute_battle(pokemon1, pokemon2)

        # Save battle record
        battle = Battle(
            pokemon1_id=pokemon1.id,
            pokemon2_id=pokemon2.id,
            winner_id=result.winner.id if result.winner else None,
            pokemon1_score=result.pokemon1_score,
            pokemon2_score=result.pokemon2_score,
            battle_log=result.battle_log,
        )
        self.db.add(battle)
        await self.db.flush()

        # Load relationships for response
        battle.pokemon1 = pokemon1
        battle.pokemon2 = pokemon2
        battle.winner = result.winner

        return battle

    async def get_battle(self, battle_id: int) -> Battle | None:
        """Get a battle by ID with related Pokemon loaded."""
        stmt = (
            select(Battle)
            .where(Battle.id == battle_id)
            .options(
                selectinload(Battle.pokemon1),
                selectinload(Battle.pokemon2),
                selectinload(Battle.winner),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_battles(self, limit: int = 100, offset: int = 0) -> list[Battle]:
        """List all battles with related Pokemon loaded."""
        stmt = (
            select(Battle)
            .order_by(Battle.created_at.desc())
            .limit(limit)
            .offset(offset)
            .options(
                selectinload(Battle.pokemon1),
                selectinload(Battle.pokemon2),
                selectinload(Battle.winner),
            )
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
