"""SQLAlchemy models for Pokemon and Battle data."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


class Pokemon(Base):
    """Pokemon entity stored in the database."""

    __tablename__ = "pokemon"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pokeapi_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)

    # Base stats
    hp: Mapped[int] = mapped_column(Integer)
    attack: Mapped[int] = mapped_column(Integer)
    defense: Mapped[int] = mapped_column(Integer)
    special_attack: Mapped[int] = mapped_column(Integer)
    special_defense: Mapped[int] = mapped_column(Integer)
    speed: Mapped[int] = mapped_column(Integer)

    # Types (comma-separated for simplicity)
    types: Mapped[str] = mapped_column(String(100))

    # Sprite URL for display
    sprite_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    if TYPE_CHECKING:
        battles_as_pokemon1: Mapped[list[Battle]]
        battles_as_pokemon2: Mapped[list[Battle]]
        battles_won: Mapped[list[Battle]]

    def __repr__(self) -> str:
        return f"<Pokemon(id={self.id}, name={self.name})>"


class Battle(Base):
    """Battle record between two Pokemon."""

    __tablename__ = "battles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    pokemon1_id: Mapped[int] = mapped_column(ForeignKey("pokemon.id"), index=True)
    pokemon2_id: Mapped[int] = mapped_column(ForeignKey("pokemon.id"), index=True)
    winner_id: Mapped[int | None] = mapped_column(ForeignKey("pokemon.id"), nullable=True)

    # Battle details
    pokemon1_score: Mapped[float] = mapped_column(Float)
    pokemon2_score: Mapped[float] = mapped_column(Float)
    battle_log: Mapped[str] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    pokemon1: Mapped[Pokemon] = relationship(
        "Pokemon", foreign_keys=[pokemon1_id], backref="battles_as_pokemon1"
    )
    pokemon2: Mapped[Pokemon] = relationship(
        "Pokemon", foreign_keys=[pokemon2_id], backref="battles_as_pokemon2"
    )
    winner: Mapped[Pokemon | None] = relationship(
        "Pokemon", foreign_keys=[winner_id], backref="battles_won"
    )

    def __repr__(self) -> str:
        return f"<Battle(id={self.id}, pokemon1={self.pokemon1_id}, pokemon2={self.pokemon2_id})>"
